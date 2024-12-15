#!/usr/bin/env python3

from yaml import safe_load as yaml_load
from ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS
from chargeport import ChargePort
from display import DisplayPort
from usb import USBPort
from dataclasses import dataclass
from time import sleep
from icons import USB2_ICON, USB3_ICON
from usbdevs import USB_MATCHERS
from typing import Optional
from render import RenderInfo, RenderResult, PER_POS_OFFSET, ICON_ROWS, render_charge

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
        if not port_info:
            return None

        render_info = self.render_info.augment_usb(
            usb=port_info,
        )
        for matcher, usbdev in USB_MATCHERS:
            if not matcher.matches(render_info):
                continue
            res = usbdev.render(render_info)
            if res:
                return res

        res = render_charge(info=render_info, input_only=True)
        if res:
            return res

        if port_info.speed >= 5000:
            return RenderResult(data=USB3_ICON)
        return RenderResult(data=USB2_ICON)

class PortUI:
    ports: list[PortConfig]
    def __init__(self, ports: list[PortConfig]):
        self.ports = ports

    def render(self) -> None:
        all_images: dict[LEDMatrix, bytearray | None] = {}
        for port in self.ports:
            res = port.render()
            if not res.data:
                if port.render_info.matrix not in all_images:
                    all_images[port.render_info.matrix] = None
                continue

            image_data = all_images.get(port.render_info.matrix, None)
            if not image_data:
                image_data = ([0x00] * LED_MATRIX_ROWS) * LED_MATRIX_COLS
                all_images[port.render_info.matrix] = image_data
    
            data = res.data
            if len(data) != LED_MATRIX_COLS * ICON_ROWS:
                raise ValueError(f"Invalid icon size expected={LED_MATRIX_COLS * ICON_ROWS} actual={len(data)} data={data}")

            for col in range(LED_MATRIX_COLS):
                start = (col * LED_MATRIX_ROWS) + port.row
                image_data[start:start+ICON_ROWS] = data[col::9]

        for matrix, image_data in all_images.items():
            if not image_data:
                matrix.sleep()
                continue

            matrix.wakeup()

            for col in range(LED_MATRIX_COLS):
                data = image_data[col * LED_MATRIX_ROWS:(col + 1) * LED_MATRIX_ROWS]
                for port in self.ports:
                    if port.row > 1:
                        data[port.row - 2] = 0x22
                data[LED_MATRIX_ROWS - 1] = 0x22
                matrix.stage_col(col, data)

            matrix.flush_cols()

def main():
    LED_MATRICES: dict[str, LEDMatrix] = {}

    with open("config.yml", "r") as f:
        CONFIG = yaml_load(f)

    print("Loading LED matrices...")
    for ele in CONFIG["led_matrices"]:
        matrix = LEDMatrix(ele["id"], ele["serial"])
        matrix.fill(False)
        matrix.wakeup()
        LED_MATRICES[ele["id"]] = matrix

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
                row=((ele["led_matrix"]["pos"] * PER_POS_OFFSET) + 2),
            ))

    ui = PortUI(ui_ports)

    print("FWUI loaded!")

    while True:
        ui.render()
        print("Render OK")
        sleep(1)

if __name__ == "__main__":
    main()
