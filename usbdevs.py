from usb import USBPortInfo, USBPort
from display import DisplayPort
from typing import Optional
from icons import parse_str_info, make_invalid_icon

# All icons should be 9x8 pixels

class USBDevice:
    def get_icon(self, port: USBPort, info: USBPortInfo, display: DisplayPort) -> Optional[list[int]]:
        return None

class USBDevice(USBDevice):
    connected_icon: list[int]
    disconnected_icon: list[int]

    def __init__(self, connected_icon: list[int], disconnected_icon: Optional[list[int]] = None):
        self.connected_icon = connected_icon
        if disconnected_icon is None:
            disconnected_icon = connected_icon.copy()
        self.disconnected_icon = disconnected_icon

    def is_connected(self, port: USBPort, info: USBPortInfo, display: DisplayPort) -> bool:
        raise NotImplementedError()

    def get_icon(self, port: USBPort, info: USBPortInfo, display: DisplayPort) -> Optional[list[int]]:
        if self.is_connected(port, info, display):
            return self.connected_icon
        return self.disconnected_icon

class USBDisplayDevice(USBDevice):
    invalid_icon: list[int]

    def __init__(self, connected_icon: list[int], disconnected_icon: list[int], invalid_icon: Optional[list[int]]):
        super().__init__(connected_icon=connected_icon, disconnected_icon=disconnected_icon)
        if not invalid_icon:
            invalid_icon = make_invalid_icon(connected_icon)
        self.invalid_icon = invalid_icon

    def is_connected(self, port: USBPort, info: USBPortInfo, display: DisplayPort) -> bool:
        display_info = display.get_info()
        return display_info and display_info.connected

    def get_icon(self, port: USBPort, info: USBPortInfo, display: DisplayPort) -> Optional[list[int]]:
        if not display:
            return self.invalid_icon
        return super().get_icon(port, info, display)

USB_DEVICES: dict[USBPortInfo, USBDevice] = {}

# Define devices below

class EthernetDevice(USBDevice):
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

    def is_connected(self, port: USBPort, info: USBPortInfo, display: DisplayPort) -> bool:
        return port.read_subfile("*/net/*/operstate", info.is_usb3) == "up"

_ETHERNET_DEVICE = EthernetDevice()

_AUDIO_DEVICE = USBDevice(parse_str_info(
     "      #  " +
    "     ##  " +
    "  ### #  " +
    "  #   #  " +
    "  #   #  " +
    "  ### #  " +
    "     ##  " +
    "      #  "
))

_SD_DEVICE = USBDevice(parse_str_info(
    " #####   " +
    " #    #  " +
    " ##    # " +
    "  #    # " +
    " #     # " +
    " #     # " +
    " #     # " +
    " ####### "
))

_MICROSD_DEVICE = USBDevice(parse_str_info(
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
