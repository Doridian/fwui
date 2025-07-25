#!/usr/bin/env python3

from yaml import safe_load as yaml_load
from fwui.ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS
from fwui.ports.charge import ChargePort
from fwui.ports.display import DisplayPort
from fwui.ports.usb import USBPort
from time import sleep
from fwui.icons import EMPTY_ICON
from fwui.devices import DEVICE_MATCHERS
from fwui.render import RenderInfo, RenderResult, PER_POS_OFFSET, ICON_ROWS, SEPARATOR_PIXEL, BLANK_PIXEL, BLANK_MATRIX
from threading import Thread
from datetime import datetime, timedelta

TIME_ZERO = datetime.fromtimestamp(0)
sleep_idle_seconds = timedelta(seconds=60)
sleep_individual_ports = False
frame_time_seconds = 1.0

class PortConfig:
    usb_port: USBPort | None
    display_port: DisplayPort | None
    charge_port: ChargePort | None
    matrix: LEDMatrix
    row: int

    last_sleep_block: datetime
    _last_render: RenderResult | None = None

    def __init__(self, usb_port: USBPort | None, display_port: DisplayPort | None, charge_port: ChargePort | None, matrix: LEDMatrix, row: int):
        super().__init__()
        self.charge_port = charge_port
        self.display_port = display_port
        self.usb_port = usb_port
        self.row = row
        self.matrix = matrix
        self.last_sleep_block = datetime.now()

    def render(self) -> list[int] | None:
        res = self._render()
        if not res:
            res = RenderResult(data=None)

        if res == self._last_render:
            allow_sleep = res.allow_sleep
        else:
            allow_sleep = False
            self._last_render = res

        if not allow_sleep:
            self.last_sleep_block = datetime.now()

        return res.data

    def _render(self) -> RenderResult | None:
        if not self.usb_port:
            return None

        render_info = RenderInfo(
            usb=self.usb_port.get_info() if self.usb_port else None,
            display=self.display_port.get_info() if self.display_port else None,
            charge=self.charge_port.get_info() if self.charge_port else None,
            matrix=self.matrix,
        )

        for matcher, usbdev in DEVICE_MATCHERS:
            if not matcher.matches(render_info):
                continue
            res = usbdev.render(render_info)
            if res:
                return res

        return None

class PortUI:
    ports: list[PortConfig]

    def __init__(self, ports: list[PortConfig]):
        super().__init__()
        self.ports = ports

    def _render_port(self, port: PortConfig, image_data: list[int], last_sleep_blocks: dict[LEDMatrix, datetime]) -> None:
        data = port.render()

        if sleep_idle_seconds is None:
            pass
        elif sleep_individual_ports:
            if port.last_sleep_block + sleep_idle_seconds < datetime.now():
                return
        elif last_sleep_blocks.get(port.matrix, TIME_ZERO) < port.last_sleep_block:
            last_sleep_blocks[port.matrix] = port.last_sleep_block

        if not data:
            data = EMPTY_ICON

        if len(data) != LED_MATRIX_COLS * ICON_ROWS:
            raise ValueError(f"Invalid icon size expected={LED_MATRIX_COLS * ICON_ROWS} actual={len(data)} data={data}")

        for col in range(LED_MATRIX_COLS):
            start = (col * LED_MATRIX_ROWS) + port.row
            image_data[start:start+ICON_ROWS+4] = [SEPARATOR_PIXEL, BLANK_PIXEL] + data[col::9] + [BLANK_PIXEL, SEPARATOR_PIXEL]

    def _draw_matrix(self, matrix: LEDMatrix, image_data: list[int]) -> None:
        if not image_data or image_data == BLANK_MATRIX:
            if matrix.is_asleep:
                return

            matrix.clear(sleep=True)
            return

        matrix.wakeup()
        #matrix.draw(bytes(image_data))

        for col in range(LED_MATRIX_COLS):
            data = image_data[col * LED_MATRIX_ROWS:(col + 1) * LED_MATRIX_ROWS]
            matrix.stage_col(col, bytes(data))

        matrix.flush_cols()

    def render(self) -> None:
        all_images: dict[LEDMatrix, list[int] | None] = {}
        all_threads: list[Thread] = []
        last_sleep_blocks: dict[LEDMatrix, datetime] = {}

        for port in self.ports:
            image_data = all_images.get(port.matrix, None)
            if not image_data:
                image_data = BLANK_MATRIX.copy()
                all_images[port.matrix] = image_data

            t = Thread(target=self._render_port, args=(port, image_data, last_sleep_blocks))
            all_threads.append(t)
            t.start()

        for t in all_threads:
            t.join()
        all_threads.clear()

        for matrix, image_data in all_images.items():
            if not sleep_individual_ports:
                last_sleep_block = last_sleep_blocks.get(matrix, TIME_ZERO)
                if sleep_idle_seconds is None:
                    pass
                elif last_sleep_block and (last_sleep_block + sleep_idle_seconds < datetime.now()):
                    image_data = None
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
    global sleep_idle_seconds, sleep_individual_ports, frame_time_seconds
    with open("config.yml", "r") as f:
        config = yaml_load(f)

    sleep_config = config.get("sleep")
    if sleep_config:
        config_sleep_idle_seconds = sleep_config.get("idle_seconds")
        if config_sleep_idle_seconds:
            if config_sleep_idle_seconds < 0:
                sleep_idle_seconds = None
            else:
                sleep_idle_seconds = timedelta(seconds=config_sleep_idle_seconds)
        config_sleep_individual_ports = sleep_config.get("individual_ports")
        if config_sleep_individual_ports is not None:
            sleep_individual_ports = bool(config_sleep_individual_ports)

    render_config = config.get("render")
    if render_config:
        config_frame_time_seconds = render_config.get("frame_time_seconds")
        if config_frame_time_seconds:
            frame_time_seconds = float(config_frame_time_seconds)

    print("Loading LED matrices...")
    for ele in config["led_matrices"]:
        matrix = LEDMatrix(ele["id"], ele["serial"])
        LED_MATRICES[ele["id"]] = matrix

    print("Clearing matrices...")
    for matrix in LED_MATRICES.values():
        clear_matrices(sleep=False)

    print("Loading charge ports...")

    ui_ports: list[PortConfig] = []

    for ele in config["ports"]:
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
                charge_port=charge_port,
                display_port=display_port,
                matrix=LED_MATRICES[ele["led_matrix"]["id"]],
                usb_port=usb_port,
                row=(ele["led_matrix"]["pos"] * PER_POS_OFFSET),
            ))

    ui = PortUI(ui_ports)

    print("FWUI loaded!")

    while True:
        ui.render()
        print("Render OK")
        sleep(frame_time_seconds)

if __name__ == "__main__":
    try:
        main()
    finally:
        clear_matrices(sleep=True)
