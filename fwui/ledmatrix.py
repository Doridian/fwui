from serial import Serial

LED_MATRIX_COLS = 9
LED_MATRIX_ROWS = 34

class LEDMatrix:
    port: Serial
    id: str
    is_asleep: bool = False

    def __init__(self, id: str, port: str):
        super().__init__()
        # Baudrate doesn't matter, those are CDC serial ports
        # which do not follow any baudrate
        self.id = id
        self.port = Serial(port, timeout=5.0)

    def send_command(self, id: int, payload: bytes) -> None:
        _ = self.port.write(bytes([0x32, 0xAC, id]) + payload)

    def send_rpc(self, id: int, payload: bytes) -> bytes:
        self.send_command(id, payload)
        return self.port.read(32)

    def version(self) -> bytes:
        return self.send_rpc(0x20, bytes())

    def wakeup(self) -> None:
        self.set_sleep(False)
        _ = self.send_rpc(0x03, bytes())

    def sleep(self) -> None:
        if self.is_asleep:
            return
        self.set_sleep(True)

    def set_sleep(self, val: bool) -> None:
        self.send_command(0x03, bytes([0x01 if val else 0x00]))
        self.is_asleep = val

    def draw_bw(self, bitmap: bytes) -> None:
        if len(bitmap) != 39:
            raise ValueError("Bitmap must be 39 bytes long")
        self.send_command(0x06, bitmap)

    def fill(self, on: bool) -> None:
        self.draw_bw(bytes([0xFF if on else 0x00] * 39))

    def clear(self, sleep: bool = False) -> None:
        self.wakeup()
        self.fill(False)
        if sleep:
            self.sleep()

    def draw(self, bitmap: bytes) -> None:
        if len(bitmap) != LED_MATRIX_ROWS * LED_MATRIX_COLS:
            raise ValueError(f"Bitmap must be {LED_MATRIX_ROWS * LED_MATRIX_COLS} bytes long")
        self.send_command(0x70, bitmap)

    def stage_col(self, col: int, data: bytes) -> None:
        if len(data) != LED_MATRIX_ROWS:
            raise ValueError(f"Data must be {LED_MATRIX_ROWS} bytes long")
        if col < 0 or col >= LED_MATRIX_COLS:
            raise ValueError(f"Column must be between 0 and {LED_MATRIX_COLS - 1}")
        self.send_command(0x07, bytes([col]) + data)

    def flush_cols(self) -> None:
        self.send_command(0x08, bytes())
