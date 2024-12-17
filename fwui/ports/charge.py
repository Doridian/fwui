from .cachable import Cachable


class ChargePortInfo(Cachable):
    @property
    def current(self) -> int:
        return self.read_int_subfile("current_now", 10, 0) // 1000000

    @property
    def voltage(self) -> int:
        return self.read_int_subfile("voltage_now") // 1000000

    @property
    def online(self) -> bool:
        return self.read_int_subfile("online") == 1

class ChargePort:
    devpath: str

    def __init__(self, devpath: str):
        super().__init__()
        self.devpath = devpath

    def get_info(self) -> ChargePortInfo | None:
        info = ChargePortInfo(self.devpath)
        if info.read_subfile("online") is None:
            return None
        return info
