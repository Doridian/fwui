#!/usr/bin/env python3

from yaml import safe_load as yaml_load
from fwui.ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS
from fwui.ports.charge import ChargePort
from fwui.ports.display import DisplayPort
from fwui.ports.usb import USBPort
from dataclasses import dataclass
from time import sleep
from fwui.icons import USB2_ICON, USB3_ICON
from fwui.devices import DEVICE_MATCHERS
from typing import Optional
from fwui.render import RenderInfo, RenderResult, PER_POS_OFFSET, ICON_ROWS, render_charge, SEPARATOR_PIXEL, BLANK_PIXEL, BLANK_ROW
from threading import Thread

@dataclass(kw_only=True, frozen=True)
class PortConfig:
    render_info: RenderInfo
    usb_port: Optional[USBPort]
    row: int

    def render(self) -> RenderResult:
        res = self.render_usb()
        if res:
            return res

        res = render_charge(info=self.render_info)
        if res:
            return res
        
        return RenderResult(data=None)

    def render_usb(self) -> Optional[RenderResult]:
        if not self.usb_port:
            return None

        port_info = self.usb_port.get_info()
        render_info = self.render_info
        if port_info:
            render_info = self.render_info.augment_usb(
                usb=port_info,
            )

        for matcher, usbdev in DEVICE_MATCHERS:
            if not matcher.matches(render_info):
                continue
            res = usbdev.render(render_info)
            if res:
                return res

        if not render_info.usb:
            return None

        res = render_charge(info=render_info, input_only=True)
        if res:
            return res

        speed = render_info.usb.speed
        if speed and speed >= 5000:
            return RenderResult(data=USB3_ICON)
        return RenderResult(data=USB2_ICON)

class PortUI:
    ports: list[PortConfig]

    def __init__(self, ports: list[PortConfig]):
        super().__init__()
        self.ports = ports

    def _render_port(self, port: PortConfig, image_data: list[int]) -> None:
        res = port.render()
        if not res.data:
            return

        data = res.data
        if len(data) != LED_MATRIX_COLS * ICON_ROWS:
            raise ValueError(f"Invalid icon size expected={LED_MATRIX_COLS * ICON_ROWS} actual={len(data)} data={data}")

        for col in range(LED_MATRIX_COLS):
            start = (col * LED_MATRIX_ROWS) + port.row
            image_data[start:start+ICON_ROWS+4] = [SEPARATOR_PIXEL, BLANK_PIXEL] + data[col::9] + [BLANK_PIXEL, SEPARATOR_PIXEL]

    def _draw_matrix(self, matrix: LEDMatrix, image_data: list[int]) -> None:
        if not image_data:
            if matrix.is_asleep:
                return

            matrix.clear(sleep=True)
            return

        matrix.wakeup()

        for col in range(LED_MATRIX_COLS):
            data = image_data[col * LED_MATRIX_ROWS:(col + 1) * LED_MATRIX_ROWS]
            matrix.stage_col(col, bytes(data))

        matrix.flush_cols()

    def render(self) -> None:
        all_images: dict[LEDMatrix, list[int] | None] = {}
        all_threads: list[Thread] = []
        for port in self.ports:
            image_data = all_images.get(port.render_info.matrix, None)
            if not image_data:
                image_data = [BLANK_PIXEL] * (LED_MATRIX_COLS * LED_MATRIX_ROWS)
                all_images[port.render_info.matrix] = image_data
            t = Thread(target=self._render_port, args=(port, image_data))
            all_threads.append(t)
            t.start()

        for t in all_threads:
            t.join()
        all_threads.clear()

        for matrix, image_data in all_images.items():
            t = Thread(target=self._draw_matrix, args=(matrix, image_data))
            all_threads.append(t)
            t.start()

        for t in all_threads:
            t.join()
        all_threads.clear()


LED_MATRICES: dict[str, LEDMatrix] = {}

def _clear_matrix(matrix: LEDMatrix, sleep: bool) -> None:
    try:
        matrix.clear(sleep=sleep)
    except:
        pass

def clear_matrices(sleep: bool) -> None:
    all_threads: list[Thread] = []
    for matrix in LED_MATRICES.values():
        t = Thread(target=_clear_matrix, args=(matrix, sleep))
        all_threads.append(t)
        t.start()

    for t in all_threads:
        t.join()

def main():
    with open("config.yml", "r") as f:
        CONFIG = yaml_load(f)

    print("Loading LED matrices...")
    for ele in CONFIG["led_matrices"]:
        matrix = LEDMatrix(ele["id"], ele["serial"])
        LED_MATRICES[ele["id"]] = matrix

    print("Clearing matrices...")
    for matrix in LED_MATRICES.values():
        clear_matrices(sleep=False)

    print("Loading charge ports...")

    ui_ports: list[PortConfig] = []

    for ele in CONFIG["ports"]:
        charge_port = None
        if "pd" in ele:
            charge_port = ChargePort(ele["pd"])

        display_port = None
        if "display" in ele:
            display_port = DisplayPort(ele["display"])

        usb_port = None
        if "usb" in ele:
            usb_port = USBPort(ele["usb"])

        if "led_matrix" in ele:
            ui_ports.append(PortConfig(
                render_info=RenderInfo(
                    charge=charge_port,
                    display=display_port,
                    matrix=LED_MATRICES[ele["led_matrix"]["id"]],
                    usb=None,
                ),
                usb_port=usb_port,
                row=(ele["led_matrix"]["pos"] * PER_POS_OFFSET),
            ))

    ui = PortUI(ui_ports)

    print("FWUI loaded!")

    while True:
        ui.render()
        print("Render OK")
        sleep(1)

if __name__ == "__main__":
    try:
        main()
    finally:
        clear_matrices(sleep=True)
