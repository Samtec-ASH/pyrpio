''' PyRPIO module '''
# pylint: disable=import-self
try:
    from pyrpio.rpiolib import rpio_init
except ImportError:
    import warnings
    warnings.warn('Failed importing rpiolib. Assuming development mode.')

    def rpio_init(_):
        ''' Mock init function. '''
        return 0
from pyrpio.defs import RPIOConfigs

__version__ = "0.0.4"

RPIO_INITIALIZED = False


def configure(configs: RPIOConfigs):
    ''' Configure module w/ supplied configs.
    Args:
        - configs (RPIOConfigs): module configs
    '''
    # pylint: disable=global-statement
    global RPIO_INITIALIZED
    if not RPIO_INITIALIZED:
        rpio_init(1 if configs.gpiomem else 0)
    RPIO_INITIALIZED = True
