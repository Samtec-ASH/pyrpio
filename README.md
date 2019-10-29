# PyRPIO


#### A Python addon which provides high-speed access to the Raspberry Pi GPIO interface, supporting regular GPIO as well as i²c, PWM, and SPI.
#### This package is inspired by [node-rpio](https://github.com/jperkin/node-rpio) which is a node.js addon.

## TODO List:

* Geared towards Python 3 (async, dataclass, static type hinting)
* Expose all major, high-level C routines in bcm2835
* Create convenience Python class for each IO protocol: I2C, SPI, MDIO, PWM, GPIO
* Enable specifying I2C bus:
  - RPI 4 has 6 I2C buses
  - For older RPIs, later Raspbian images enable kernel-level bit-bang i2c.
* Make thread safe and support
* Make mock version to allow testing/developing on non-RPI (MacOS, x86 Linux).

