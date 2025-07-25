from dataclasses import dataclass, field
from .ports.usb import USBInfo
from .ports.charge import ChargeInfo
from .ports.display import DisplayInfo
from .ledmatrix import LEDMatrix, LED_MATRIX_COLS, LED_MATRIX_ROWS

BLANK_PIXEL = 0x00
SEPARATOR_PIXEL = 0x22

BLANK_ROW = [BLANK_PIXEL] * LED_MATRIX_COLS
FULL_ROW = [0xFF] * LED_MATRIX_COLS

BLANK_MATRIX = BLANK_ROW * LED_MATRIX_ROWS

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

ROMAN_HEIGHT = 3
ROMAN_NUMERALS = {
    'I':  [0xFF] * 3,
    'V':   [0xFF, 0x00, 0xFF,
            0xFF, 0x00, 0xFF,
            0x00, 0xFF, 0x00],
    'X':   [0xFF, 0x00, 0xFF,
            0x00, 0xFF, 0x00,
            0xFF, 0x00, 0xFF],
    'L':   [0xFF, 0x00,
            0xFF, 0x00,
            0xFF, 0xFF],
    'C':   [0xFF, 0xFF, 0xFF,
            0xFF, 0x00, 0x00,
            0xFF, 0xFF, 0xFF],
    'D':   [0xFF, 0xFF, 0x00,
            0xFF, 0x00, 0xFF,
            0xFF, 0xFF, 0x00],
    'M':   [0xFF, 0xFF, 0xFF,
            0xFF, 0x00, 0xFF,
            0xFF, 0x00, 0xFF],
}
ROMAN_NUMERAL_DIGITS: list[list[str]] = [
    [
        '',
        'I',
        'II',
        'III',
        'IV',
        'V',
        'VI',
        'VII',
        'VIII',
        'IX',
    ],
    [
        '',
        'X',
        'XX',
        'XXX',
        'XL',
        'L',
        'LX',
        'LXX',
        'LXXX',
        'XC',
    ],
    [
        '',
        'C',
        'CC',
        'CCC',
        'CD',
        'D',
        'DC',
        'DCC',
        'DCCC',
        'CM',
    ],
]

def __draw_numeral_char(char: str, xoffset: int, yoffset: int, data: list[int]) -> int:
    cdata = ROMAN_NUMERALS.get(char, None)
    if not cdata:
        return 0

    width = len(cdata) // ROMAN_HEIGHT

    if xoffset > LED_MATRIX_COLS:
        return -1

    xlen = width
    if xoffset + xlen > LED_MATRIX_COLS:
        xlen = LED_MATRIX_COLS - xoffset

    for y in range(ROMAN_HEIGHT):
        xbase = (y + yoffset) * LED_MATRIX_COLS + xoffset
        data[xbase:xbase + xlen] = cdata[y * width:y * width + xlen]

    if xlen != width:
        return -1

    return xoffset + xlen + 1

def make_roman_numeral_str(value: int, xoffset: int, yoffset: int, data: list[int]) -> bool:
    if value <= 0:
        return True

    x = 0
    curvalue = value
    digitstr = ""
    xpos = xoffset
    while curvalue > 0:
        digit = curvalue % 10
        curvalue //= 10

        digitstr = ROMAN_NUMERAL_DIGITS[x][digit] + digitstr
        x += 1

    for char in digitstr:
        xpos = __draw_numeral_char(char, xpos, yoffset, data)
        if xpos < 0:
            return True

    return False

def make_multirow_bar(width: float, height: int = 1, reverse: bool = False) -> list[int]:
    res: list[int] = []
    while width > 0:
        res += make_row_bar(width, height, reverse)
        width -= LED_MATRIX_COLS
    return res

@dataclass(kw_only=True, frozen=True, eq=True)
class RenderInfo:
    usb: USBInfo | None
    display: DisplayInfo | None
    charge: ChargeInfo | None
    matrix: LEDMatrix

@dataclass(kw_only=True, frozen=True)
class RenderResult:
    data: list[int] | None
    allow_sleep: bool = field(default=True)
