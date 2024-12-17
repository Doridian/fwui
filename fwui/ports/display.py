from .cachable import Cachable

class DisplayPortInfo(Cachable):
    @property
    def connected(self) -> bool:
        return self.read_subfile("status") == "connected"

class DisplayPort:
    display: str

    def __init__(self, display: str):
        super().__init__()
        self.display = display

    def get_info(self) -> DisplayPortInfo | None:
        info = DisplayPortInfo(self.display)
        status = info.read_subfile("status")
        if not status:
            return None
        return info
