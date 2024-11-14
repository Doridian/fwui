#!/usr/bin/env python3

from yaml import safe_load as yaml_load
from ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS
from chargeport import ChargePort
from dataclasses import dataclass
from time import sleep

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
    matrix: LEDMatrix
    row: int

    # Rows are 9 bytes long
    def render(self) -> list[int]:
        if not self.charge:
            return None
        
        invert = self.matrix.id == "right"

        voltage = self.charge.voltage()
        if voltage == 0:
            return None

        voltage /= 1000000
        current = self.charge.current() / 1000000
        online = self.charge.online()
        if current < 0 or voltage < 0 or not online:
            invert = not invert

        current = abs(current)
        voltage = abs(voltage)

        return _make_row_bar(current, 2, invert) + (BLANK_ROW * 2) + _make_multirow_bar(voltage, 1, invert)

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
    CHARGE_PORTS: dict[str, ChargePort] = {}

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
            CHARGE_PORTS[ele["id"]] = charge_port

        if "led_matrix" in ele:
            ui_ports.append(PortConfig(
                charge=charge_port,
                matrix=LED_MATRICES[ele["led_matrix"]["id"]],
                row=((ele["led_matrix"]["pos"] * PER_POS_OFFSET) + 2),
            ))

    ui = PortUI(ui_ports)

    print("FWUI loaded!")

    while True:
        ui.render()
        sleep(1)

if __name__ == "__main__":
    main()
