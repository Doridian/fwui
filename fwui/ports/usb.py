from .cachable import Cachable

class USBInfo(Cachable):
    @property
    def vid(self) -> int | None:
        return self.read_int_subfile("idVendor", 16)

    @property
    def pid(self) -> int | None:
        return self.read_int_subfile("idProduct", 16)

    @property
    def speed(self) -> int | None:
        return self.read_int_subfile("speed")

class USBPort:
    subdevs: list[str]

    def __init__(self, subdevs: list[str]):
        super().__init__()
        self.subdevs = subdevs

    def get_info(self) -> USBInfo | None:
        for subdev in self.subdevs:
            info = USBInfo(subdev)
            if info.vid and info.pid:
                return info

        return None
