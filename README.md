# PyRPIO

![./icon.png](./icon.png)

A Python 3 addon which provides high-speed access to the Raspberry Pi GPIO interface, supporting regular GPIO as well as i²c, PWM, SPI, and MDIO.

This package is inspired by [node-rpio](https://github.com/jperkin/node-rpio) which is a node.js addon.

![PyPI](https://img.shields.io/pypi/v/pyrpio)

## Compatibility

- Raspberry Pi Models: A, B (revisions 1.0 and 2.0), A+, B+, 2, 3, 3+, 3 A+, 4, Compute Module 3, Zero.
- Python 3.7+

## Install

Install the latest from PyPi:

> `pip install pyrpio`

## Supported Interfaces

- GPIO
- PWM
- I2C
- MDIO
- SPI

## Examples

```python
from pyrpio.i2c import I2C
from pyrpio.mdio import MDIO
from pyrpio.i2c_register_device import I2CRegisterDevice
### I2C Operations ###

i2c_bus = i2c.I2C('/dev/i2c-3')
i2c_bus.open()

i2c_bus.set_address(0x50)

i2c_bus.read_write(data=bytes([0x23]), length=1)

i2c_dev = I2CRegisterDevice(bus=i2c_bus, address=0x50, register_size=1, data_size=1)

# Read register
val = i2c_dev.read_register(register=0x23)

# Read sequential registers
vals = i2c_dev.read_register_sequential(register=0x23, length=4)

# Close up shop
i2c_bus.close()

### MDIO Operations ###

# Create bus using GPIO pins 23 and 24 (bit-bang)
mdio_bus = mdio.MDIO(clk_pin=23, data_pin=24, path='/dev/gpiochip0')
mdio_bus.open()

# Read register 0x10 from device 0x30 (CLAUSE-45)
mdio_bus.read_c45_register(0x30, 0x00, 0x10)

# Read register set from device 0x30 (CLAUSE-45)
mdio_bus.read_c45_registers(0x30, 0x00, [0,1,2,3,4])

# Close up shop
mdio_bus.close()
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Maintainers

- [Samtec - ASH](https://samtec-ash.com)
