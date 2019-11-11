from .register_device import I2CRegisterDevice
from .i2c import I2C


bus = I2C()
bus.open()


def test_register_device():
    assert 2 == 2
