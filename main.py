#!/usr/bin/env python3

from yaml import safe_load as yaml_load
from ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS
from chargeport import ChargePort
from display import DisplayPort
from usb import USBPort
from dataclasses import dataclass
from time import sleep
from icons import USB_CONNECTED_ICONS, USB_DISCONNECTED_ICONS
from usbdevs import USB_DEVICE_OVERRIDES
from math import floor

BLANK_ROW = [0x00] * LED_MATRIX_COLS
FULL_ROW = [0xFF] * LED_MATRIX_COLS

def _make_row_bar(width: float, height: int = 1, reverse: bool = False) -> list[int]:
    if width >= LED_MATRIX_COLS:
        return FULL_ROW * height
    if width <= 0:
        return BLANK_ROW * height
    
    width_int = int(width)
    width_frac = float(width) - float(width_int)
    end_width_int = LED_MATRIX_COLS - width_int

    frac_piece = []
    if width_frac > 0:
        end_width_int -= 1
        frac_piece = [int(width_frac * 0xFF)]

    ret = (([0xFF] * width_int) + frac_piece + ([0x00] * end_width_int)) * height
    if reverse:
        ret = ret[::-1]
    return ret

def _make_multirow_bar(width: float, height: int = 1, reverse: bool = False) -> list[int]:
    res = []
    while width > 0:
        res += _make_row_bar(width, height, reverse)
        width -= LED_MATRIX_COLS
    return res

@dataclass(frozen=True)
class PortConfig:
    charge: ChargePort | None
    usb: USBPort | None
    display: DisplayPort | None
    matrix: LEDMatrix
    row: int

    # Rows are 9 bytes long

    def render(self) -> list[int]:
        res = self.render_display()
        if res:
            return res

        res = self.render_usb()
        if res:
            return res

        res = self.render_charge()
        if res:
            return res
        
        return None

    def render_display(self) -> list[int]:
        if not self.display:
            return None
        
        display_info = self.display.get_info()
        if not display_info or not display_info.connected:
            return self.render_usb(False)

        return self.render_usb(True)

    def render_usb(self, is_connected: bool = True) -> list[int]:
        if not self.usb:
            return None
        
        port_info = self.usb.get_info()
        if not port_info:
            return None
        
        port_module = port_info.module

        override = USB_DEVICE_OVERRIDES.get(port_info)
        if override:
            port_module = override.module
            is_connected = override.is_connected()

        is_valid_config = self.usb.is_valid_module(port_module)

        invert = self.matrix.id == "right"
        if not is_valid_config:
            invert = not invert

        if override:
            override_icon = override.get_icon()
            if override_icon:
                return override_icon

        if not is_connected:
            return USB_DISCONNECTED_ICONS[port_module]

        return USB_CONNECTED_ICONS[port_module]

    def render_charge(self) -> list[int]:
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

        return _make_row_bar(current_int, 2, invert) + _make_row_bar(current_frac * 10.0, 1, invert) + (BLANK_ROW * 2) + _make_row_bar(voltage_tens, 2, invert) + _make_row_bar(voltage, 1, invert)

class PortUI:
    ports: list[PortConfig]
    def __init__(self, ports: list[PortConfig]):
        self.ports = ports

    def render(self) -> None:
        all_images: dict[LEDMatrix, bytearray | None] = {}
        for port in self.ports:
            res = port.render()
            if not res:
                if port.matrix not in all_images:
                    all_images[port.matrix] = None
                continue

            image_data = all_images.get(port.matrix, None)
            if not image_data:
                image_data = ([0x00] * LED_MATRIX_ROWS) * LED_MATRIX_COLS
                all_images[port.matrix] = image_data
    
            lines = len(res) // LED_MATRIX_COLS
            for col in range(LED_MATRIX_COLS):
                start = (col * LED_MATRIX_ROWS) + port.row
                image_data[start:start+lines] = res[col::9]

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

PER_POS_OFFSET = LED_MATRIX_ROWS // 3

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
            usb_port = USBPort(ele["usb2"], ele["usb3"], bool(display_port))

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
