from os import path
from enum import Enum
from typing import Optional
from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True, eq=True)
class DisplayPortInfo:
    connected: bool

class DisplayPort:
    display: str

    def __init__(self, display: str):
        self.display = display

    def read_subfile(self, file: str) -> str:
        try:
            with open(path.join(self.display, file), "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    def get_info(self) -> Optional[DisplayPortInfo]:
        status = self.read_subfile("status")
        if not status:
            return None
        return DisplayPortInfo(connected=(status == "connected"))
