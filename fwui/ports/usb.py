from .base import DevInfo

class USBInfo(DevInfo):
    @property
    def vid(self) -> int:
        return self.read_int_subfile("idVendor", base=16, default=0)

    @property
    def pid(self) -> int:
        return self.read_int_subfile("idProduct", base=16, default=0)

    @property
    def speed(self) -> int:
        return self.read_int_subfile("speed", default=0)

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
