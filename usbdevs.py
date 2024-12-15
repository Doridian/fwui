from usb import USBPortInfo
from typing import Optional
from icons import parse_str_info, make_invalid_icon
from render import RenderInfo, RenderResult

# All icons should be 9x8 pixels

class USBDevice:
    def render(self, info: RenderInfo) -> Optional[RenderResult]:
        return None

class USBBasicDevice(USBDevice):
    icon: list[int]

    def __init__(self, icon: list[int]):
        self.icon = icon

    def render(self, info: RenderInfo) -> Optional[RenderResult]:
        return RenderResult(data=self.icon)

class USBConnectionDevice(USBDevice):
    connected_icon: list[int]
    disconnected_icon: list[int]

    def __init__(self, connected_icon: list[int], disconnected_icon: list[int]):
        self.connected_icon = connected_icon
        self.disconnected_icon = disconnected_icon

    def is_connected(self, info: RenderInfo) -> bool:
        raise NotImplementedError()

    def render(self, info: RenderInfo) -> Optional[RenderResult]:
        if self.is_connected(info):
            return RenderResult(data=self.connected_icon)
        return RenderResult(data=self.disconnected_icon)

class USBDisplayDevice(USBConnectionDevice):
    invalid_icon: list[int]

    def __init__(self, connected_icon: list[int], disconnected_icon: list[int], invalid_icon: Optional[list[int]]):
        super().__init__(connected_icon=connected_icon, disconnected_icon=disconnected_icon)
        if not invalid_icon:
            invalid_icon = make_invalid_icon(connected_icon)
        self.invalid_icon = invalid_icon

    def is_connected(self, info: RenderInfo) -> bool:
        display_info = info.display.get_info()
        return display_info and display_info.connected

    def render(self, info: RenderInfo) -> Optional[RenderResult]:
        if not info.display:
            return RenderResult(data=self.invalid_icon, allow_sleep=False)
        return super().render(info)

USB_DEVICES: dict[USBPortInfo, USBDevice] = {}

# Define devices below

class EthernetDevice(USBConnectionDevice):
    _ETHERNET_DISCONNECTED_ICON = parse_str_info(
        " ####### " +
        " # 3 3 # " +
        " # 3 3 # " +
        " #     # " +
        " #     # " +
        " #     # " +
        " ##   ## " +
        "  #####  "
    )
    _ETHERNET_CONNECTED_ICON = parse_str_info(
        " ####### " +
        " # # # # " +
        " # # # # " +
        " #     # " +
        " #     # " +
        " #     # " +
        " ##   ## " +
        "  #####  "
    )

    def __init__(self):
        super().__init__(self._ETHERNET_CONNECTED_ICON, self._ETHERNET_DISCONNECTED_ICON)

    def is_connected(self, info: RenderInfo) -> bool:
        return info.usb.read_subfile("*/net/*/operstate", info.usbinfo.is_usb3) == "up"

_ETHERNET_DEVICE = EthernetDevice()

_AUDIO_DEVICE = USBBasicDevice(parse_str_info(
     "      #  " +
    "     ##  " +
    "  ### #  " +
    "  #   #  " +
    "  #   #  " +
    "  ### #  " +
    "     ##  " +
    "      #  "
))

_SD_DEVICE = USBBasicDevice(parse_str_info(
    " #####   " +
    " #    #  " +
    " ##    # " +
    "  #    # " +
    " #     # " +
    " #     # " +
    " #     # " +
    " ####### "
))

_MICROSD_DEVICE = USBBasicDevice(parse_str_info(
    "  ####   " +
    "  #   #  " +
    "  #   #  " +
    "  #    # " +
    "  #   #  " +
    "  #    # " +
    "  #    # " +
    "  ###### "
))

_DISPLAY_PORT_DEVICE = USBDisplayDevice(
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

_HDMI_DEVICE = USBDisplayDevice(
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

USB_DEVICES[USBPortInfo(vid=0x32ac, pid=0x0010)] = _AUDIO_DEVICE
USB_DEVICES[USBPortInfo(vid=0x0bda, pid=0x8156)] = _ETHERNET_DEVICE
USB_DEVICES[USBPortInfo(vid=0x32ac, pid=0x0009)] = _SD_DEVICE
USB_DEVICES[USBPortInfo(vid=0x090c, pid=0x1000)] = _MICROSD_DEVICE

USB_DEVICES[USBPortInfo(vid=0x32ac, pid=0x0002)] = _HDMI_DEVICE
USB_DEVICES[USBPortInfo(vid=0x32ac, pid=0x0003)] = _DISPLAY_PORT_DEVICE
