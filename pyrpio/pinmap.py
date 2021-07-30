""" Handles detecting pin mapping of given board. """
import re
from typing import Optional
from pyrpio.types import PinMapName, RPIOConfigs, RPIOBoard, RPIOMapping, PIN_MAPPINGS


def detect_pinmap_name_dt() -> Optional[PinMapName]:
    """ Detect pinmap using device tree.
        Args: None
        Returns:
            Optional[str]: Pinmap name
    """
    model = None
    try:
        with open('/proc/device-tree/model', 'r') as fp:
            model = fp.read()
    except Exception:
        return None
    if not model:
        return None
    pattern = re.compile(r'^Raspberry Pi (.*) Model')
    board_rev = None
    for line in model.split('\n'):
        found = pattern.search(line)
        if found:
            board_rev = next((int(s) for s in found.group(0).split() if s.isdigit()), None)
            break
    if board_rev in [2, 3, 4]:
        return PinMapName.PINMAP_40
    return None


def detect_pinmap_name() -> Optional[PinMapName]:
    """ Detect pinmap by extracting revision in /proc/cpuinfo.
        Args: None
        Returns:
            Optional[PinMapName]: Pinmap name
    """
    cpu_info = None
    try:
        with open('/proc/cpuinfo', 'r') as fp:
            cpu_info = fp.read()
    except Exception:
        return None
    if not cpu_info:
        return None
    pattern = re.compile(r'^Revision.*(.{4})')
    board_rev = None
    for line in cpu_info.split('\n'):
        found = pattern.search(line)
        if found:
            board_rev = next((int(s, base=16) for s in found.group(0).split() if s.replace('0x', '').isdigit()), None)
            break
    if board_rev in [0x2, 0x3]:
        return PinMapName.PINMAP_26_R1
    if board_rev in [0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xd, 0xe, 0xf]:
        return PinMapName.PINMAP_26
    if board_rev in [
            0x10, 0x12, 0x13, 0x15, 0x92, 0x93, 0xc1, 0x1041, 0x2042,
            0x2082, 0x20a0, 0x20d3, 0x20e0, 0x2100, 0x3111]:
        return PinMapName.PINMAP_40
    return detect_pinmap_name_dt()


def set_mock_pinmap(configs: RPIOConfigs) -> Optional[PinMapName]:
    """Get pinmap based on supplied mock board type.

    Args:
        configs (RPIOConfigs): Configuration

    Returns:
        Optional[PinMapName]: Pin mapping based on config
    """
    if configs.mock in [RPIOBoard.RASPI_B_R1]:
        return PinMapName.PINMAP_26_R1
    if configs.mock in [RPIOBoard.RASPI_A, RPIOBoard.RASPI_B]:
        return PinMapName.PINMAP_26
    if configs.mock in [
            RPIOBoard.RASPI_A_P, RPIOBoard.RASPI_B_P,
            RPIOBoard.RASPI_2, RPIOBoard.RASPI_3, RPIOBoard.RASPI_4,
            RPIOBoard.RASPI_ZERO, RPIOBoard.RASPI_ZERO_W]:
        return PinMapName.PINMAP_40
    return None


def pin_to_gpio(pin: int, configs: RPIOConfigs) -> int:
    """ Translate pin based on board and selected mapping.
    Args:
        pin (int): Pin number (physical or gpio #)
        configs (RPIOConfigs): Selected configs
    Return:
        int: Translated pin number
    """
    gpio_pin = pin
    if configs.mapping == RPIOMapping.physical:
        gpio_pin = PIN_MAPPINGS[configs.pinmap_name][pin]
    elif configs.mapping == RPIOMapping.gpio:
        gpio_pin = pin
    if gpio_pin < 0:
        raise Exception(f'Invalid pin {pin}')
    return gpio_pin
