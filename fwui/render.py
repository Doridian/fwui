from dataclasses import dataclass, field
from typing import Optional
from .ports.usb import USBPortInfo
from .ports.charge import ChargePort
from .ports.display import DisplayPort
from .ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS
from math import floor

BLANK_PIXEL = 0x00
SEPARATOR_PIXEL = 0x22

BLANK_ROW = [BLANK_PIXEL] * LED_MATRIX_COLS
FULL_ROW = [0xFF] * LED_MATRIX_COLS

PER_POS_OFFSET = (LED_MATRIX_ROWS - 1) // 3
ICON_ROWS = PER_POS_OFFSET - 3 # Top line, top space, bottom space

def make_row_bar(width: float, height: int = 1, reverse: bool = False) -> list[int]:
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

def make_multirow_bar(width: float, height: int = 1, reverse: bool = False) -> list[int]:
    res: list[int] = []
    while width > 0:
        res += make_row_bar(width, height, reverse)
        width -= LED_MATRIX_COLS
    return res

@dataclass(kw_only=True, frozen=True, eq=True)
class RenderInfo:
    usb: USBPortInfo | None
    display: DisplayPort | None
    charge: ChargePort | None
    matrix: LEDMatrix

    def augment_usb(self, usb: USBPortInfo) -> "RenderInfo":
        return RenderInfo(
            usb=usb,
            display=self.display,
            charge=self.charge,
            matrix=self.matrix,
        )

@dataclass(kw_only=True, frozen=True)
class RenderResult:
    data: list[int] | None
    allow_sleep: bool = field(default=True)


def render_charge(info: RenderInfo, input_only: bool = False) -> Optional[RenderResult]:
    if not info.charge:
        return None

    invert = info.matrix.id == "right"

    voltage = info.charge.voltage()
    if voltage == 0:
        return None

    current = info.charge.current()
    online = info.charge.online()
    if current < 0 or voltage < 0 or not online:
        if input_only:
            return None
        invert = not invert

    current = abs(current)
    voltage = abs(voltage)

    voltage_tens = floor(voltage / 10)
    voltage = voltage - (voltage_tens * 10)

    current_int = floor(current)
    current_frac = current - current_int

    data = make_row_bar(current_int, 2, invert) + make_row_bar(current_frac * 10.0, 1, invert) + (BLANK_ROW * 2) + make_row_bar(voltage_tens, 2, invert) + make_row_bar(voltage, 1, invert)
    return RenderResult(data=data)
