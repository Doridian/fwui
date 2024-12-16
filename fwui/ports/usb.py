from os import path
from glob import glob

class USBPortInfo:
    devpath: str
    filecache: dict[str, str  | None]

    def __init__(self, devpath: str):
        super().__init__()
        self.devpath = devpath
        self.filecache = {}

    def read_subfile(self, file: str) -> str | None:
        if file in self.filecache:
            return self.filecache[file]
        res = self._read_subfile(file)
        self.filecache[file] = res
        return res

    def _read_subfile(self, file: str) -> str | None:
        devfile = path.join(self.devpath, file)
        globs = glob(devfile)
        if not globs:
            return None
        devfile = globs[0]

        try:
            with open(devfile, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def read_int_subfile(self, file: str, base: int = 10) -> int | None:
        value = self.read_subfile(file)
        if value is None:
            return None
        return int(value, base)

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

    def get_info(self) -> USBPortInfo | None:
        for subdev in self.subdevs:
            info = USBPortInfo(subdev)
            if info.vid and info.pid:
                return info

        return None
