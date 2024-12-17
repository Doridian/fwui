from .base import DevInfo
from functools import cached_property

class ChargeInfo(DevInfo):
    @cached_property
    def current(self) -> float:
        return self.read_int_subfile("current_now", default=0) / 1000000

    @cached_property
    def voltage(self) -> float:
        return self.read_int_subfile("voltage_now", default=0) / 1000000

    @cached_property
    def online(self) -> bool:
        return self.read_int_subfile("online") == 1
    
    @cached_property
    def usb_type(self) -> str | None:
        return self.read_str_subfile("usb_type")

class ChargePort:
    devpath: str

    def __init__(self, devpath: str):
        super().__init__()
        self.devpath = devpath

    def get_info(self) -> ChargeInfo | None:
        info = ChargeInfo(self.devpath)
        if not info.usb_type:
            return None
        return info
