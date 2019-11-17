from pyrpio import rpiolib
from pyrpio import spi, i2c, mdio, pwm
from pyrpio.defs import RPIOConfigs
import pyrpio.defs as defs
import pyrpio.pins as pins

__version__ = "0.0.3"

__all__ = ['defs', 'gpio', 'spi', 'i2c', 'mdio', 'pwm', 'pins']

rpio_initialized = False


def configure(configs: RPIOConfigs):
    global rpio_initialized
    if not rpio_initialized:
        rpiolib.rpio_init(1 if configs.gpiomem else 0)
    rpio_initialized = True
