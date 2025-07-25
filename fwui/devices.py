from typing import override

from fwui.ledmatrix import LED_MATRIX_COLS
from .icons import parse_str_info, make_invalid_icon, USB2_ICON, USB3_ICON
from .render import BLANK_ROW, RenderInfo, RenderResult, make_roman_numeral_str
from abc import ABC, abstractmethod

# All icons should be 9x8 pixels

class DeviceMatcher(ABC):
    @abstractmethod
    def matches(self, info: RenderInfo) -> bool:
        pass

class USBDeviceIDMatcher(DeviceMatcher):
    vid: int
    pid: int

    def __init__(self, vid: int, pid: int):
        super().__init__()
        self.vid = vid
        self.pid = pid

    @override
    def matches(self, info: RenderInfo) -> bool:
        if not info.usb:
            return False
        return info.usb.vid == self.vid and info.usb.pid == self.pid

class Device:
    def render(self, info: RenderInfo) -> RenderResult | None:
        return None

class DeviceIcon(Device):
    icon: list[int]

    def __init__(self, icon: list[int]):
        super().__init__()
        self.icon = icon

    @override
    def render(self, info: RenderInfo) -> RenderResult | None:
        return RenderResult(data=self.icon)

class ConnectionDevice(Device):
    connected_icon: list[int]
    disconnected_icon: list[int]

    def __init__(self, connected_icon: list[int], disconnected_icon: list[int]):
        super().__init__()
        self.connected_icon = connected_icon
        self.disconnected_icon = disconnected_icon

    def is_connected(self, info: RenderInfo) -> bool:
        raise NotImplementedError()

    @override
    def render(self, info: RenderInfo) -> RenderResult | None:
        if self.is_connected(info):
            return RenderResult(data=self.connected_icon)
        return RenderResult(data=self.disconnected_icon)

class DisplayDevice(ConnectionDevice):
    invalid_icon: list[int]

    def __init__(self, connected_icon: list[int], disconnected_icon: list[int], invalid_icon: list[int] | None):
        super().__init__(connected_icon=connected_icon, disconnected_icon=disconnected_icon)
        if not invalid_icon:
            invalid_icon = make_invalid_icon(connected_icon)
        self.invalid_icon = invalid_icon

    @override
    def is_connected(self, info: RenderInfo) -> bool:
        if not info.display:
            return False
        return info.display.connected

    @override
    def render(self, info: RenderInfo) -> RenderResult | None:
        if not info.display:
            return RenderResult(data=self.invalid_icon, allow_sleep=False)
        return super().render(info)

class EthernetDevice(ConnectionDevice):
    @override
    def is_connected(self, info: RenderInfo) -> bool:
        if not info.usb:
            return False
        return info.usb.read_str_subfile("*/net/*/operstate") == "up"

_ETHERNET_DEVICE = EthernetDevice(
    connected_icon=parse_str_info(
        " ####### " +
        " # # # # " +
        " # # # # " +
        " #     # " +
        " #     # " +
        " #     # " +
        " ##   ## " +
        "  #####  "
    ),
    disconnected_icon=parse_str_info(
        " ####### " +
        " # 3 3 # " +
        " # 3 3 # " +
        " #     # " +
        " #     # " +
        " #     # " +
        " ##   ## " +
        "  #####  "
    ),
)

_AUDIO_DEVICE = DeviceIcon(parse_str_info(
    "      #  " +
    "     ##  " +
    "  ### #  " +
    "  #   #  " +
    "  #   #  " +
    "  ### #  " +
    "     ##  " +
    "      #  "
))

_SD_DEVICE = DeviceIcon(parse_str_info(
    " #####   " +
    " #    #  " +
    " ##    # " +
    "  #    # " +
    " #     # " +
    " #     # " +
    " #     # " +
    " ####### "
))

_MICROSD_DEVICE = DeviceIcon(parse_str_info(
    "  ####   " +
    "  #   #  " +
    "  #   #  " +
    "  #    # " +
    "  #   #  " +
    "  #    # " +
    "  #    # " +
    "  ###### "
))

_DISPLAY_PORT_DEVICE = DisplayDevice(
    connected_icon=parse_str_info(
        "   ####  " +
        "  #   #  " +
        "  ### #  " +
        "  # # #  " +
        "  # # #  " +
        "  ### #  " +
        "  #   #  " +
        "  #####  "
    ),
    disconnected_icon=parse_str_info(
        "   ####  " +
        "  #   #  " +
        "  #33 #  " +
        "  # 3 #  " +
        "  # 3 #  " +
        "  #33 #  " +
        "  #   #  " +
        "  #####  "
    ),
    invalid_icon=None,
)

_HDMI_DEVICE = DisplayDevice(
    connected_icon=parse_str_info(
        "   ####  " +
        "  #   #  " +
        "  # # #  " +
        "  # # #  " +
        "  # # #  " +
        "  # # #  " +
        "  #   #  " +
        "   ####  "
    ),
    disconnected_icon=parse_str_info(
        "   ####  " +
        "  #   #  " +
        "  # 3 #  " +
        "  # 3 #  " +
        "  # 3 #  " +
        "  # 3 #  " +
        "  #   #  " +
        "   ####  "
    ),
    invalid_icon=None,
)


class ChargeMatcher(DeviceMatcher):
    @override
    def matches(self, info: RenderInfo) -> bool:
        if not info.charge:
            return False
        if not info.charge.voltage:
            return False
        if info.charge.voltage < 0 and info.usb:
            return False
        return True

class ChargeDevice(Device):
    xit: int = 0
    @override
    def render(self, info: RenderInfo) -> RenderResult | None:
        if not info.charge:
            return None

        invert = info.matrix.id == "right"

        voltage = info.charge.voltage
        if voltage == 0:
            return None

        current = info.charge.current
        online = info.charge.online
        incoming = True
        if current < 0 or voltage < 0 or not online:
            incoming = False

        current = abs(current)
        voltage = abs(voltage)

        border_on_left = incoming ^ invert

        left_border_col = 0x10 if border_on_left else 0x00
        right_border_col = 0x00 if border_on_left else 0x10
        filled_line = [left_border_col, left_border_col, 0x00, 0x00, 0x00, 0x00, 0x00, right_border_col, right_border_col]

        data: list[int] = BLANK_ROW * 3 + filled_line * 2 + BLANK_ROW * 3

        oflow = make_roman_numeral_str(int(voltage), 0, 0, data)
        if oflow:
            off = int(LED_MATRIX_COLS * 3.5) - 1
            data[off:off+3] = [0x40, 0x40, 0x40]
        oflow = make_roman_numeral_str(int(current), 0, 5, data)
        if oflow:
            off = int(LED_MATRIX_COLS * 4.5) - 1
            data[off:off+3] = [0x40, 0x40, 0x40]

        self.xit += 1
        if self.xit > 100:
            self.xit = 0
        return RenderResult(data=data)

class AnyUSBMatcher(DeviceMatcher):
    @override
    def matches(self, info: RenderInfo) -> bool:
        return bool(info.usb)


class AnyUSBDevice(Device):
    @override
    def render(self, info: RenderInfo) -> RenderResult | None:
        if not info.usb:
            return None
        speed = info.usb.speed
        if speed and speed >= 5000:
            return RenderResult(data=USB3_ICON)
        return RenderResult(data=USB2_ICON)

DEVICE_MATCHERS: list[tuple[DeviceMatcher, Device]] = []

def add_matcher(matcher: DeviceMatcher, device: Device):
    DEVICE_MATCHERS.append((matcher, device))

# Define devices below

add_matcher(ChargeMatcher(), ChargeDevice()) # Always first

add_matcher(USBDeviceIDMatcher(vid=0x32ac, pid=0x0010), _AUDIO_DEVICE)
add_matcher(USBDeviceIDMatcher(vid=0x0bda, pid=0x8156), _ETHERNET_DEVICE)
add_matcher(USBDeviceIDMatcher(vid=0x32ac, pid=0x0009), _SD_DEVICE)
add_matcher(USBDeviceIDMatcher(vid=0x090c, pid=0x1000), _MICROSD_DEVICE)

add_matcher(USBDeviceIDMatcher(vid=0x32ac, pid=0x0002), _HDMI_DEVICE)
add_matcher(USBDeviceIDMatcher(vid=0x32ac, pid=0x0003), _DISPLAY_PORT_DEVICE)

add_matcher(AnyUSBMatcher(), AnyUSBDevice()) # Always last
