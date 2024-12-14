from usb import USBPortInfo, USBPortModule, USBPort
from typing import Optional
from icons import parse_str_info

# All icons should be 9x8 pixels

class USBDeviceOverride:
    module: USBPortModule

    def __init__(self, module: USBPortModule = USBPortModule.USB):
        self.module = module

    def get_icon(self, port: USBPort, info: USBPortInfo) -> Optional[list[int]]:
        return None
    
class SimpleUSBDeviceOverride(USBDeviceOverride):
    connected_icon: list[int]
    disconnected_icon: list[int]

    def __init__(self, connected_icon: list[int], disconnected_icon: Optional[list[int]] = None, module: USBPortModule = USBPortModule.USB):
        super().__init__(module)
        self.connected_icon = connected_icon
        if disconnected_icon is None:
            disconnected_icon = connected_icon.copy()
        self.disconnected_icon = disconnected_icon

    def is_connected(self, port: USBPort, info: USBPortInfo) -> bool:
        raise NotImplementedError()

    def get_icon(self, port: USBPort, info: USBPortInfo) -> Optional[list[int]]:
        if self.is_connected(port, info):
            return self.connected_icon
        return self.disconnected_icon

USB_DEVICE_OVERRIDES: dict[USBPortInfo, USBDeviceOverride] = {}

# Define devices below

class EthernetUSBDeviceOverride(SimpleUSBDeviceOverride):
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

    def is_connected(self, port: USBPort, info: USBPortInfo) -> bool:
        return port.read_subfile("*/net/*/operstate", info.is_usb3) == "up"

_ETHERNET_DEVICE = EthernetUSBDeviceOverride()

_AUDIO_DEVICE = SimpleUSBDeviceOverride(parse_str_info(
     "      #  " +
    "     ##  " +
    "  ### #  " +
    "  #   #  " +
    "  #   #  " +
    "  ### #  " +
    "     ##  " +
    "      #  "
))

_SD_DEVICE = SimpleUSBDeviceOverride(parse_str_info(
    " #####   " +
    " #    #  " +
    " ##    # " +
    "  #    # " +
    " #     # " +
    " #     # " +
    " #     # " +
    " ####### "
))

_MICROSD_DEVICE = SimpleUSBDeviceOverride(parse_str_info(
    "  ####   " +
    "  #   #  " +
    "  #   #  " +
    "  #    # " +
    "  #   #  " +
    "  #    # " +
    "  #    # " +
    "  ###### "
))

USB_DEVICE_OVERRIDES[USBPortInfo(vid=0x32ac, pid=0x0010)] = _AUDIO_DEVICE
USB_DEVICE_OVERRIDES[USBPortInfo(vid=0x0bda, pid=0x8156)] = _ETHERNET_DEVICE
USB_DEVICE_OVERRIDES[USBPortInfo(vid=0x32ac, pid=0x0009)] = _SD_DEVICE
USB_DEVICE_OVERRIDES[USBPortInfo(vid=0x090c, pid=0x1000)] = _MICROSD_DEVICE

USB_DEVICE_OVERRIDES[USBPortInfo(vid=0x32ac, pid=0x0002)] = USBDeviceOverride(USBPortModule.HDMI)
USB_DEVICE_OVERRIDES[USBPortInfo(vid=0x32ac, pid=0x0003)] = USBDeviceOverride(USBPortModule.DISPLAY_PORT)

