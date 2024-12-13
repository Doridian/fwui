from os import path
from enum import Enum
from typing import Optional

class USBPortType(Enum):
    USB2 = 0
    USB3 = 1
    HDMI = 2
    DP = 3

class USBPort:
    usb2: str
    usb3: str
    can_display: bool

    def __init__(self, usb2: str, usb3: str, can_display: bool):
        self.usb2 = usb2
        self.usb3 = usb3
        self.can_display = can_display

    def read_subfile(self, file: str, usb3: bool) -> str:
        devbase = self.usb3 if usb3 else self.usb2
        if not devbase:
            return ""
        try:
            with open(path.join(devbase, file), "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    def is_valid_port_type(self, port_type: USBPortType) -> bool:
        if port_type == USBPortType.HDMI or port_type == USBPortType.DP:
            return self.can_display
        return True

    def get_port_type(self) -> Optional[USBPortType]:
        is_usb3 = True
        vendor_id = self.read_subfile("idVendor", is_usb3)
        if not vendor_id:
            is_usb3 = False
            vendor_id = self.read_subfile("idVendor", is_usb3)
            if not vendor_id:
                return None

        product_id = self.read_subfile("idProduct", is_usb3)
        if not product_id:
            return None

        if vendor_id == "32ac": # Framework
            if product_id == "0002":
                return USBPortType.HDMI
            elif product_id == "0003":
                return USBPortType.DP
            
        return USBPortType.USB3 if is_usb3 else USBPortType.USB2
