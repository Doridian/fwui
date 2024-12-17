from .base import DevInfo
from functools import cached_property

class DisplayInfo(DevInfo):
    @cached_property
    def connected(self) -> bool:
        return self.status == "connected"

    @cached_property
    def status(self) -> str | None:
        return self.read_str_subfile("status")

class DisplayPort:
    display: str

    def __init__(self, display: str):
        super().__init__()
        self.display = display

    def get_info(self) -> DisplayInfo | None:
        info = DisplayInfo(self.display)
        if not info.status:
            return None
        return info
