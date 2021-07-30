""" I2C Interface """
from .types import I2CError, I2CBase
from .i2c import I2C

__all__ = ['I2CError', 'I2CBase', 'I2C']
