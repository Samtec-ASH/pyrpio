""" I2C via FTDI USB-Serial Interface (FT232H) """

from typing import List, Optional
import pyftdi.i2c  # pylint: disable=import-error
from .types import I2CBase, I2CMessage


class FtdiI2C(I2CBase):
    ''' FTDI device based I2C. '''
    def __init__(self, path: str = 'ftdi://ftdi:232h:1/1'):
        '''
        Create an i2c bus with 7-bit addressing via FTDI usb-serial device.
        TODO: Unlike i2c.I2C, if multiple classes are instantiated the device comm.
        is detroyed once first instance is closed. Perhaps, make into a singleton with locks for given path.

        Args:
            path (str, optional): path of i2c bus. Defaults to '/dev/i2c-1'.
        '''
        self.path: str = path
        self._address = 0x0
        self._bus = pyftdi.i2c.I2cController()

    def open(self, frequency: float = 100_000):
        self._bus.configure(self.path, frequency=frequency)

    def close(self):
        self._bus.close()

    def __enter__(self):
        if not self._bus.configured:
            self._bus.configure(self.path)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass

    def __del__(self):
        self.close()

    def set_address(self, address: int):
        self._address = address

    def read(self, length: int = 1) -> bytes:
        return self._bus.read(address=self._address, readlen=2)

    def write(self, data: bytes):
        self._bus.write(address=self._address, out=data)

    def read_write(self, data: bytes, length: int = 1) -> bytes:
        return self._bus.exchange(address=self._address, out=data, readlen=length)

    def transfer(self, address: int, messages: List[I2CMessage]):
        raise NotImplementedError()

    def detect(self, first: int = 0x03, last: int = 0x77, data: Optional[bytes] = None, length: int = 1) -> List[int]:
        addresses = []
        for i in range(first, last+1):
            try:
                self.set_address(i)
                if data is not None:
                    self.read_write(data=data, length=length)
                else:
                    self.read(length=length)
                addresses.append(i)
            except Exception:
                pass
        return addresses
