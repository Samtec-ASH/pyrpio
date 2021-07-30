""" I2C Interface """
from .types import SPIError, SPIBase, ByteLike
from .spi import SPI

__all__ = ['SPIError', 'SPIBase', 'SPI', 'ByteLike']
