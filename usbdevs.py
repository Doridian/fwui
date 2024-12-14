from usb import USBPortInfo, USBPortModule
from abc import ABC, abstractmethod
from typing import Optional

# All icons should be 9x8 pixels

class USBDeviceOverride(ABC):
    module: USBPortModule

    def __init__(self, module: USBPortModule):
        self.module = module

    def is_connected(self) -> bool:
        return True

    @abstractmethod
    def get_icon(self) -> Optional[list[int]]:
        pass
    
class SimpleUSBDeviceOverride(USBDeviceOverride):
    connected_icon: list[int]
    disconnected_icon: list[int]

    def __init__(self, module: USBPortModule, connected_icon: list[int], disconnected_icon: list[int]):
        super().__init__(module)
        self.connected_icon = connected_icon
        self.disconnected_icon = disconnected_icon

    def get_icon(self) -> Optional[list[int]]:
        if self.is_connected():
            return self.connected_icon
        return self.disconnected_icon

USB_DEVICE_OVERRIDES: dict[USBPortInfo, USBDeviceOverride] = {}

# Define devices below
