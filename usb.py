from os import path
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field

class USBPortModule(Enum):
    USB2 = 1
    USB3 = 2
    USB4 = 3
    HDMI = 4
    DISPLAY_PORT = 5
    ETHERNET = 6
    MICRO_SD = 7
    SD = 8
    AUDIO = 9

@dataclass(kw_only=True, frozen=True, eq=True)
class USBPortInfo:
    vid: int
    pid: int
    module: USBPortModule = field(compare=False)

class USBPort:
    usb2: str
    usb3: str

    def __init__(self, usb2: str, usb3: str):
        self.usb2 = usb2
        self.usb3 = usb3

    def read_subfile(self, file: str, usb3: bool) -> int:
        devbase = self.usb3 if usb3 else self.usb2
        if not devbase:
            return 0
        try:
            with open(path.join(devbase, file), "r") as f:
                return int(f.read().strip(), 16)
        except FileNotFoundError:
            return 0

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
