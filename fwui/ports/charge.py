from .base import DevInfo

class ChargeInfo(DevInfo):
    @property
    def current(self) -> int:
        return self.read_int_subfile("current_now", default=0) // 1000000

    @property
    def voltage(self) -> int:
        return self.read_int_subfile("voltage_now", default=0) // 1000000

    @property
    def online(self) -> bool:
        return self.read_int_subfile("online") == 1

class ChargePort:
    devpath: str

    def __init__(self, devpath: str):
        super().__init__()
        self.devpath = devpath

    def get_info(self) -> ChargeInfo | None:
        info = ChargeInfo(self.devpath)
        if info.read_str_subfile("online") is None:
            return None
        return info
