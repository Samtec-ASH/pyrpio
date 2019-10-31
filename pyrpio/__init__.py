import os
import re
from enum import Enum
from typing import Optional, List
import dataclasses
from dataclasses import dataclass
from pyrpio import rpiolib

LOW = 0x0
HIGH = 0x1

INPUT = 0x0
OUTPUT = 0x1
PWM = 0x2

PULL_OFF = 0x0
PULL_DOWN = 0x1
PULL_UP = 0x2

POLL_LOW = 0x1;
POLL_HIGH = 0x2
POLL_BOTH = 0x3

PAD_GROUP_0_27     = 0x0
PAD_GROUP_28_45    = 0x1
PAD_GROUP_46_53    = 0x2
PAD_DRIVE_2mA      = 0x00
PAD_DRIVE_4mA      = 0x01
PAD_DRIVE_6mA      = 0x02
PAD_DRIVE_8mA      = 0x03
PAD_DRIVE_10mA     = 0x04
PAD_DRIVE_12mA     = 0x05
PAD_DRIVE_14mA     = 0x06
PAD_DRIVE_16mA     = 0x07
PAD_HYSTERESIS     = 0x08
PAD_SLEW_UNLIMITED = 0x10


defmock = 'raspi-3'

class RPIOMapping(str, Enum):
    physical = 'physical'
    gpio = 'gpio'

class RPIOBoard(str, Enum):
    RASPI_B_R1 = 'RASPI_B_R1'
    RASPI_A = 'RASPI_A'
    RASPI_B = 'RASPI_B'
    RASPI_A_P = 'RASPI_A_P'
    RASPI_B_P = 'RASPI_B_P'
    RASPI_2 = 'RASPI_2'
    RASPI_3 = 'RASPI_3'
    RASPI_4 = 'RASPI-4'
    RASPI_ZERO = 'RASPI_ZERO'
    RASPI_ZERO_W = 'RASPI_ZERO_W'

@dataclass
class RPIOOptions:
    gpiomem: bool = True
    mapping: RPIOMapping = RPIOMapping.physical
    mock: Optional[RPIOBoard] = None

class PinMapName(str, Enum):
    PINMAP_26_R1 = 'PINMAP_26_R1'
    PINMAP_26 = 'PINMAP_26'
    PINMAP_40 = 'PINMAP_40'

pincache = {}
pinmap = None
pinmaps = {
    PinMapName.PINMAP_26_R1: [
        -1,
        -1, -1,        #  P1  P2 #
         0, -1,        #  P3  P4 #
         1, -1,        #  P5  P6 #
         4, 14,        #  P7  P8 #
        -1, 15,        #  P9  P10 #
        17, 18,        # P11  P12 #
        21, -1,        # P13  P14 #
        22, 23,        # P15  P16 #
        -1, 24,        # P17  P18 #
        10, -1,        # P19  P20 #
         9, 25,        # P21  P22 #
        11,  8,        # P23  P24 #
        -1,  7        # P25  P26 #
    ],
    # Original Raspberry Pi, PCB revision 2.0.
    # Differs to R1 on pins 3, 5, and 13.
    # XXX: no support yet for the P5 header pins.
    PinMapName.PINMAP_26: [
        -1,
        -1, -1,        #  P1  P2 */
         2, -1,        #  P3  P4 */
         3, -1,        #  P5  P6 */
         4, 14,        #  P7  P8 */
        -1, 15,        #  P9  P10 */
        17, 18,        # P11  P12 */
        27, -1,        # P13  P14 */
        22, 23,        # P15  P16 */
        -1, 24,        # P17  P18 */
        10, -1,        # P19  P20 */
         9, 25,        # P21  P22 */
        11,  8,        # P23  P24 */
        -1,  7        # P25  P26 */
    ],
    # Raspberry Pi 40-pin models.
    # First 26 pins are the same as PINMAP_26.
    PinMapName.PINMAP_40: [
        -1,
        -1, -1,        #  P1  P2 #
         2, -1,        #  P3  P4 #
         3, -1,        #  P5  P6 #
         4, 14,        #  P7  P8 #
        -1, 15,        #  P9  P10 #
        17, 18,        # P11  P12 #
        27, -1,        # P13  P14 #
        22, 23,        # P15  P16 #
        -1, 24,        # P17  P18 #
        10, -1,        # P19  P20 #
         9, 25,        # P21  P22 #
        11,  8,        # P23  P24 #
        -1,  7,        # P25  P26 #
         0,  1,        # P27  P28 #
         5, -1,        # P29  P30 #
         6, 12,        # P31  P32 #
        13, -1,        # P33  P34 #
        19, 16,        # P35  P36 #
        26, 20,        # P37  P38 #
        -1, 21        # P39  P40 #
    ]
}

def detect_pinmap_devicetree() -> Optional[PinMapName]:
    model = None
    try:
        with open('/proc/device-tree/model', 'r') as fp:
            model = fp.read()
    except Exception as err:
        return None
    if not model: return None
    pattern = re.compile(r'^Raspberry Pi (.*) Model')
    board_rev = None
    for line in model.split('\n'):
        m = pattern.search(line)
        if m:
            board_rev = next((int(s) for s in m.group(0).split() if s.isdigit()), None)
            break
    if board_rev in [2, 3, 4]:
        return PinMapName.PINMAP_40
    return None

def detect_pinmap() -> Optional[PinMapName]:
    cpu_info = None
    try:
        with open('/proc/cpuinfo', 'r') as fp:
            cpu_info = fp.read()
    except Exception as err:
        return None
    if not cpu_info: return None
    pattern = re.compile(r'^Revision.*(.{4})')
    board_rev = None
    for line in cpu_info.split('\n'):
        m = pattern.search(line)
        if m:
            board_rev = next((int(s, base=16) for s in m.group(0).split() if s.replace('0x', '').isdigit()), None)
            break
    if board_rev in [0x2, 0x3]:
        return PinMapName.PINMAP_26_R1;
    if board_rev in [0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xd, 0xe, 0xf]:
        return PinMapName.PINMAP_26;
    if board_rev in [0x10, 0x12, 0x13, 0x15, 0x92, 0x93, 0xc1, 0x1041, 0x2042, 0x2082, 0x20a0, 0x20d3, 0x20e0, 0x2100, 0x3111]:
        return PinMapName.PINMAP_40;
    return detect_pinmap_devicetree()

def set_mock_pinmap(options: RPIOOptions) -> Optional[PinMapName]:
    if options.mock in [RPIOBoard.RASPI_B_R1]:
        return PinMapName.PINMAP_26_R1
    if options.mock in [RPIOBoard.RASPI_A, RPIOBoard.RASPI_B]:
        return PinMapName.PINMAP_26
    if options.mock in [
        RPIOBoard.RASPI_A_P, RPIOBoard.RASPI_B_P,
        RPIOBoard.RASPI_2, RPIOBoard.RASPI_3, RPIOBoard.RASPI_4,
        RPIOBoard.RASPI_ZERO, RPIOBoard.RASPI_ZERO_W]:
        return PinMapName.PINMAP_40
    return None

def pin_to_gpio(options: RPIOOptions, pin):
    if pincache and pin in pincache:
        return pincache[pin]
    if options.mapping == RPIOMapping.physical:
        gpio_pin = pinmaps[detect_pinmap()][pin]
    elif options.mapping == RPIOMapping.gpio:
        gpio_pin = pin
    if gpio_pin < 0:
        raise Exception(f'Invalid pin {pin}')


rpio_inited = False
rpio_options: RPIOOptions = RPIOOptions()
def configure(options: RPIOOptions):
    global rpio_inited
    if not rpio_inited:
        rpiolib.rpio_init(1 if options.gpiomem else 0)
    rpio_inited = True
    rpio_options = options