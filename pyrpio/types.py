""" PyRPIO definitions: enums and dataclasses. """

from enum import Enum
from typing import Optional, List
from dataclasses import dataclass

LOW = 0x0
HIGH = 0x1

INPUT = 0x0
OUTPUT = 0x1
PWM = 0x2

PULL_OFF = 0x0
PULL_DOWN = 0x1
PULL_UP = 0x2

POLL_LOW = 0x1
POLL_HIGH = 0x2
POLL_BOTH = 0x3

PAD_GROUP_0_27 = 0x0
PAD_GROUP_28_45 = 0x1
PAD_GROUP_46_53 = 0x2
PAD_DRIVE_2MA = 0x00
PAD_DRIVE_4MA = 0x01
PAD_DRIVE_6MA = 0x02
PAD_DRIVE_8MA = 0x03
PAD_DRIVE_10MA = 0x04
PAD_DRIVE_12MA = 0x05
PAD_DRIVE_14MA = 0x06
PAD_DRIVE_16MA = 0x07
PAD_HYSTERESIS = 0x08
PAD_SLEW_UNLIMITED = 0x10


class PinMapName(str, Enum):
    """ Board pin map name. """
    PINMAP_26_R1 = 'PINMAP_26_R1'
    PINMAP_26 = 'PINMAP_26'
    PINMAP_40 = 'PINMAP_40'


PINMAP_26_R1_MAPPING: List[int] = [
    -1,
    -1, -1,  # P1   P2  #
    0, -1,   # P3   P4  #
    1, -1,   # P5   P6  #
    4, 14,   # P7   P8  #
    -1, 15,  # P9   P10 #
    17, 18,  # P11  P12 #
    21, -1,  # P13  P14 #
    22, 23,  # P15  P16 #
    -1, 24,  # P17  P18 #
    10, -1,  # P19  P20 #
    9, 25,   # P21  P22 #
    11, 8,   # P23  P24 #
    -1, 7    # P25  P26 #
]


PINMAP_26_MAPPING: List[int] = [
    -1,
    -1, -1,  # P1   P2  #
    2, -1,   # P3   P4  #
    3, -1,   # P5   P6  #
    4, 14,   # P7   P8  #
    -1, 15,  # P9   P10 #
    17, 18,  # P11  P12 #
    27, -1,  # P13  P14 #
    22, 23,  # P15  P16 #
    -1, 24,  # P17  P18 #
    10, -1,  # P19  P20 #
    9, 25,   # P21  P22 #
    11, 8,   # P23  P24 #
    -1, 7    # P25  P26 #
]

PINMAP_40_MAPPING: List[int] = [
    -1,
    -1, -1,  # P1   P2  #
    2, -1,   # P3   P4  #
    3, -1,   # P5   P6  #
    4, 14,   # P7   P8  #
    -1, 15,  # P9   P10 #
    17, 18,  # P11  P12 #
    27, -1,  # P13  P14 #
    22, 23,  # P15  P16 #
    -1, 24,  # P17  P18 #
    10, -1,  # P19  P20 #
    9, 25,   # P21  P22 #
    11, 8,   # P23  P24 #
    -1, 7,   # P25  P26 #
    0, 1,    # P27  P28 #
    5, -1,   # P29  P30 #
    6, 12,   # P31  P32 #
    13, -1,  # P33  P34 #
    19, 16,  # P35  P36 #
    26, 20,  # P37  P38 #
    -1, 21   # P39  P40 #
]

PIN_MAPPINGS = {
    PinMapName.PINMAP_26_R1: PINMAP_26_R1_MAPPING,
    # Original Raspberry Pi, PCB revision 2.0.
    # Differs to R1 on pins 3, 5, and 13.
    PinMapName.PINMAP_26: PINMAP_26_MAPPING,
    # Raspberry Pi 40-pin models.
    # First 26 pins are the same as PINMAP_26.
    PinMapName.PINMAP_40: PINMAP_40_MAPPING
}


class RPIOMapping(str, Enum):
    """ Pin mapping convention: physical or gpio. """
    physical = 'physical'
    gpio = 'gpio'


class RPIOBoard(str, Enum):
    """ Board names. """
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
class RPIOConfigs:
    """ PyRPIO configuration options. """
    gpiomem: bool = True
    mapping: RPIOMapping = RPIOMapping.physical
    mock: Optional[RPIOBoard] = None
    pinmap_name: PinMapName = PinMapName.PINMAP_40
