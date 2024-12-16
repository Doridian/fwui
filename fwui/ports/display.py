from os import path
from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True, eq=True)
class DisplayPortInfo:
    connected: bool

class DisplayPort:
    display: str

    def __init__(self, display: str):
        super().__init__()
        self.display = display

    def read_subfile(self, file: str) -> str:
        try:
            with open(path.join(self.display, file), "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    def get_info(self) -> DisplayPortInfo | None:
        status = self.read_subfile("status")
        if not status:
            return None
        return DisplayPortInfo(connected=(status == "connected"))
