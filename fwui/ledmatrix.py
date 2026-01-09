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
        _ = self.port.write(b's\x7F')
        self.clear()

    def fill(self, on: bool) -> None:
        _ = self.port.write(b'w ' + (b'\xFF' if on else b'\x00'))

    def clear(self) -> None:
        self.fill(False)

    def draw(self, bitmap: bytes, blocking: bool = True, pwm: bool = False) -> None:
        if len(bitmap) != LED_MATRIX_ROWS * LED_MATRIX_COLS:
            raise ValueError(f"Bitmap must be {LED_MATRIX_ROWS * LED_MATRIX_COLS} bytes long")

        mode_char = b'm' if pwm else b'n'
        if blocking:
            mode_char = mode_char.upper()
        _ = self.port.write(mode_char + bitmap)
        if blocking:
            assert self.port.read(1) == mode_char
