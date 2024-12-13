from os import path
from enum import Enum
from typing import Optional
from dataclasses import dataclass

class USBPortModule(Enum):
    USB2 = 0
    USB3 = 1
    HDMI = 2
    DISPLAY_PORT = 3
    ETHERNET = 4
    MICRO_SD = 5
    SD = 6
    AUDIO = 7

@dataclass(kw_only=True, frozen=True, eq=True)
class USBPortInfo:
    vid: int
    pid: int
    module: USBPortModule

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
                return int(f.read().strip(), 16)
        except FileNotFoundError:
            return ""

    def is_valid_module(self, module: USBPortModule) -> bool:
        if module == USBPortModule.HDMI or module == USBPortModule.DISPLAY_PORT:
            return self.can_display
        return True

    def get_info(self) -> Optional[USBPortInfo]:
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
        
        port_type = USBPort.get_module_from_id(vendor_id, product_id)
        if not port_type:
            port_type = USBPortModule.USB3 if is_usb3 else USBPortModule.USB2

        return USBPortInfo(vid=vendor_id, pid=product_id, module=port_type)

    @staticmethod
    def get_module_from_id(vendor_id: int, product_id: int) -> Optional[USBPortModule]:
        if vendor_id == 0x32ac: # Framework
            if product_id == 0x0002:
                return USBPortModule.HDMI
            elif product_id == 0x0003:
                return USBPortModule.DISPLAY_PORT
            elif product_id == 0x0009:
                return USBPortModule.SD
            elif product_id == 0x0010:
                return USBPortModule.AUDIO
        elif vendor_id == 0x0bda:
            if product_id == 0x8156:
                return USBPortModule.ETHERNET
        elif vendor_id == 0x090c:
            if product_id == 0x1000:
                return USBPortModule.MICRO_SD

        return None
