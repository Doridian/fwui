from os import path
from typing import Optional
from dataclasses import dataclass, field
from glob import glob

@dataclass(kw_only=True, frozen=True, eq=True)
class USBPortInfo:
    vid: int
    pid: int
    is_usb3: bool = field(compare=False, default=False)

class USBPort:
    usb2: str
    usb3: str

    def __init__(self, usb2: str, usb3: str):
        self.usb2 = usb2
        self.usb3 = usb3

    def read_subfile(self, file: str, usb3: bool) -> str:
        devbase = self.usb3 if usb3 else self.usb2
        if not devbase:
            return ""
        
        devfile = path.join(devbase, file)
        globs = glob(devfile)
        if not globs:
            return ""
        devfile = globs[0]

        try:
            with open(devfile, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""
        
    def read_int16_subfile(self, file: str, usb3: bool) -> Optional[int]:
        value = self.read_subfile(file, usb3)
        if not value:
            return None
        return int(value, 16)

    def get_info(self) -> Optional[USBPortInfo]:
        is_usb3 = True
        vendor_id = self.read_int16_subfile("idVendor", is_usb3)
        if not vendor_id:
            is_usb3 = False
            vendor_id = self.read_int16_subfile("idVendor", is_usb3)
            if not vendor_id:
                return None

        product_id = self.read_int16_subfile("idProduct", is_usb3)
        if not product_id:
            return None

        return USBPortInfo(vid=vendor_id, pid=product_id, is_usb3=is_usb3)
