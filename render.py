from dataclasses import dataclass, field
from typing import Optional
from usb import USBPort, USBPortInfo
from display import DisplayPort
from ledmatrix import LEDMatrix

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
