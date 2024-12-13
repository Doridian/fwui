# All icons should be 9x8 pixels
from usb import USBPortModule, USBPortInfo

USB_MODULE_ICONS: dict[USBPortModule, list[int]] = {}

def parse_str_info(src: str) -> list[int]:
    res = []
    for c in src:
        if c == " ":
            res.append(0)
        elif c == "#":
            res.append(0xFF)
    return res

USB_MODULE_ICONS[USBPortModule.USB2] = parse_str_info(
    "   ###   " +
    "  #   #  " +
    "      #  " +
    "     #   " +
    "    #    " +
    "   #     " +
    "  #      " +
    "  #####  "
)

USB_MODULE_ICONS[USBPortModule.USB3] = parse_str_info(
    "   ###   " +
    "  #   #  " +
    "      #  " +
    "    ##   " +
    "      #  " +
    "      #  " +
    "  #   #  " +
    "   ###   "
)

USB_MODULE_ICONS[USBPortModule.HDMI] = parse_str_info(
    "   ####  " +
    "  #   #  " +
    "  # # #  " +
    "  # # #  " +
    "  # # #  " +
    "  # # #  " +
    "  #   #  " +
    "   ####  "
)

USB_MODULE_ICONS[USBPortModule.DISPLAY_PORT] = parse_str_info(
    "   ####  " +
    "  #   #  " +
    "  ### #  " +
    "  # # #  " +
    "  # # #  " +
    "  ### #  " +
    "  #   #  " +
    "  #####  "
)

USB_MODULE_ICONS[USBPortModule.ETHERNET] = parse_str_info(
    " ####### " +
    " # # # # " +
    " # # # # " +
    " #     # " +
    " #     # " +
    " #     # " +
    " ##   ## " +
    "  #####  "
)

USB_MODULE_ICONS[USBPortModule.SD] = parse_str_info(
    " #####   " +
    " #    #  " +
    " ##    # " +
    "  #    # " +
    " #     # " +
    " #     # " +
    " #     # " +
    " ####### "
)

USB_MODULE_ICONS[USBPortModule.MICRO_SD] = parse_str_info(
    "  ####   " +
    "  #   #  " +
    "  #   #  " +
    "  #    # " +
    "  #   #  " +
    "  #    # " +
    "  #    # " +
    "  ###### "
)

USB_MODULE_ICONS[USBPortModule.AUDIO] = parse_str_info(
    "      #  " +
    "     ##  " +
    "  ### #  " +
    "  #   #  " +
    "  #   #  " +
    "  ### #  " +
    "     ##  " +
    "      #  "
)

USB_DEVICE_ICONS: dict[USBPortInfo, list[int]] = {}
