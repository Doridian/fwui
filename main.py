#!/usr/bin/env python3

from yaml import safe_load as yaml_load
from ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS
from chargeport import ChargePort
from display import DisplayPort
from usb import USBPort
from dataclasses import dataclass
from time import sleep
from icons import USB2_ICON, USB3_ICON
from usbdevs import USB_DEVICES
from math import floor
from typing import Optional
from render import RenderInfo, RenderResult, make_row_bar, BLANK_ROW, PER_POS_OFFSET, ICON_ROWS

@dataclass(frozen=True)
class PortConfig:
    charge: ChargePort | None
    usb: USBPort | None
    display: DisplayPort | None
    matrix: LEDMatrix
    row: int

    def render(self) -> RenderResult:
        res = self.render_usb()
        if res:
            return res

        res = self.render_charge()
        if res:
            return res
        
        return RenderResult(data=None)

    def render_usb(self) -> Optional[RenderResult]:
        if not self.usb:
            return None
        
        port_info = self.usb.get_info()
        if not port_info:
            return None

        usbdev = USB_DEVICES.get(port_info)
        if usbdev:
            res = usbdev.render(
                RenderInfo(
                    usb=self.usb,
                    usbinfo=port_info,
                    display=self.display,
                    matrix=self.matrix,
                )
            )
            if res:
                return res

        if port_info.is_usb3:
            return RenderResult(data=USB3_ICON)
        return RenderResult(data=USB2_ICON)

    def render_charge(self) -> Optional[RenderResult]:
        if not self.charge:
            return None

        invert = self.matrix.id == "right"

        voltage = self.charge.voltage()
        if voltage == 0:
            return None

        current = self.charge.current()
        online = self.charge.online()
        if current < 0 or voltage < 0 or not online:
            invert = not invert

        current = abs(current)
        voltage = abs(voltage)

        voltage_tens = floor(voltage / 10)
        voltage = voltage - (voltage_tens * 10)

        current_int = floor(current)
        current_frac = current - current_int

        data = make_row_bar(current_int, 2, invert) + make_row_bar(current_frac * 10.0, 1, invert) + (BLANK_ROW * 2) + make_row_bar(voltage_tens, 2, invert) + make_row_bar(voltage, 1, invert)
        return RenderResult(data=data)

class PortUI:
    ports: list[PortConfig]
    def __init__(self, ports: list[PortConfig]):
        self.ports = ports

    def render(self) -> None:
        all_images: dict[LEDMatrix, bytearray | None] = {}
        for port in self.ports:
            res = port.render()
            if not res.data:
                if port.matrix not in all_images:
                    all_images[port.matrix] = None
                continue

            image_data = all_images.get(port.matrix, None)
            if not image_data:
                image_data = ([0x00] * LED_MATRIX_ROWS) * LED_MATRIX_COLS
                all_images[port.matrix] = image_data
    
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
        if "usb2" in ele or "usb3" in ele:
            usb_port = USBPort(ele["usb2"], ele["usb3"])

        if "led_matrix" in ele:
            ui_ports.append(PortConfig(
                charge=charge_port,
                usb=usb_port,
                display=display_port,
                matrix=LED_MATRICES[ele["led_matrix"]["id"]],
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
