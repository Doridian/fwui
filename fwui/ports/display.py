from .devinfo import DevInfo

class DisplayInfo(DevInfo):
    @property
    def connected(self) -> bool:
        return self.read_subfile("status") == "connected"

class DisplayPort:
    display: str

    def __init__(self, display: str):
        super().__init__()
        self.display = display

    def get_info(self) -> DisplayInfo | None:
        info = DisplayInfo(self.display)
        status = info.read_subfile("status")
        if not status:
            return None
        return info
