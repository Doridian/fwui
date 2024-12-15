from dataclasses import dataclass, field
from typing import Optional
from usb import USBPort, USBPortInfo
from display import DisplayPort
from ledmatrix import LEDMatrix, LED_MATRIX_COLS

BLANK_ROW = [0x00] * LED_MATRIX_COLS
FULL_ROW = [0xFF] * LED_MATRIX_COLS

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
    res = []
    while width > 0:
        res += make_row_bar(width, height, reverse)
        width -= LED_MATRIX_COLS
    return res

@dataclass(kw_only=True, frozen=True, eq=True)
class RenderInfo:
    usb: USBPort
    usbinfo: USBPortInfo
    display: Optional[DisplayPort]
    matrix: LEDMatrix

@dataclass(kw_only=True, frozen=True)
class RenderResult:
    data: list[int]
    allow_sleep: bool = field(default=True)
