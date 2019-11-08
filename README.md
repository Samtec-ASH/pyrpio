# PyRPIO

⚠️ **WARNING: This is a very early pre-release. Expect things to break.** ⚠️

#### A Python 3 addon which provides high-speed access to the Raspberry Pi GPIO interface, supporting regular GPIO as well as i²c, PWM, and SPI.
#### This package is inspired by [node-rpio](https://github.com/jperkin/node-rpio) which is a node.js addon.

![PyPI](https://img.shields.io/pypi/v/pyrpio)

# Compatibility
* Raspberry Pi Models: A, B (revisions 1.0 and 2.0), A+, B+, 2, 3, 3+, 3 A+, 4, Compute Module 3, Zero.
* Python 3.7+

# Install

Install the latest from PyPi:

> ```pip install pyrpio```

_-OR-_ using __pipenv__:

> ```pipenv install pyrpio```

Install from source:

> ```python3 setup.py install```


# Supported Interfaces

* GPIO
* PWM
* I2C
* MDIO
* SPI

# Examples

```python
import pyrpio
from pyrpio import i2c, mdio

# Configure options
options = pyrpio.RPIOOptions(
  gpiomem=True
)
# Must be called prior to using any interface
pyrpio.configure(options)

### I2C Operations ###

i2c_bus = i2c.I2C('/dev/i2c-3')
i2c_bus.open()

i2c_bus.set_address(0x50)

# Read 8-bit value using 8-bit addressing
val = i2c_bus.read_register(0x0)
i2c_bus.set_address(0x21)

# Read uint16_t using 8-bit addressing
val = i2c_bus.read_register(0x0, reg_nbytes=1, val_nbytes=2)

# Read int16_t using 8-bit addressing
val = i2c_bus.read_register(0x0, reg_nbytes=1, val_nbytes=2, signed=True)

# Seq read 8 regs starting @ 0x0 using I2C repeat start
regs = i2c_bus.read_register_sequential(0,8)

# Close up shop
i2c_bus.close()

### MDIO Operations ###

# Create bus using GPIO pins 23 and 24 (bit-bang)
mdio_bus = mdio.MDIO(23, 24)
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

# TODO

* Expose all major, high-level C routines in bcm2835
* Create convenience Python class for each interface: I2C, SPI, MDIO, PWM, GPIO
* Enable specifying I2C bus:
  - RPI 4 has 6 I2C buses
  - For older RPIs, later Raspbian images enable kernel-level bit-bang i2c.
* Make thread safe and support locking mechanism
* Make mock version to allow testing/developing on non-RPI (MacOS, x86 Linux)
*
* Testing...