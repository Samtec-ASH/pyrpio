''' PyRPIO module '''
# pylint: disable=import-self
from pyrpio import rpiolib
from pyrpio.defs import RPIOConfigs

__version__ = "0.0.3"

RPIO_INITIALIZED = False


def configure(configs: RPIOConfigs):
    ''' Configure module w/ supplied configs.
    Args:
        - configs (RPIOConfigs): module configs
    '''
    # pylint: disable=global-statement
    global RPIO_INITIALIZED
    if not RPIO_INITIALIZED:
        rpiolib.rpio_init(1 if configs.gpiomem else 0)
    RPIO_INITIALIZED = True
