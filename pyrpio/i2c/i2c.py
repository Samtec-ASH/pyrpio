'''
Create a controller to perform operations on an I2C bus
'''
from fcntl import ioctl
from typing import Optional, IO


class I2CException(Exception):
    '''
    Exceptions that occur during i2c operations. (before OS level ops)
    '''
    ...


class I2C:
    '''
    Controller to handle an I2C bus
    '''
    I2C_SLAVE = 0x0703

    def __init__(self, path: str = '/dev/i2c-1'):
        '''
        Create an i2c bus with 7-bit addressing

        Args:
            path (str, optional): path of i2c bus. Defaults to '/dev/i2c-1'.
        '''
        self.path: str = path
        self._address = 0x0
        self._bus: Optional[IO[bytes]] = None

    def open(self):
        '''
        Open the i2c bus
        '''
        if not self._bus:
            self._bus = open(self.path, 'r+b', buffering=0)
            self._address = 0x0

    def close(self):
        '''
        Close the i2c bus
        '''
        if self._bus:
            self._bus.close()
            self._bus = None

    def set_address(self, address: int):
        '''
        Set the i2c bus address if it has changed

        Args:
            address (int): address of i2c device

        Raises:
            I2CException: Bus is not open
        '''
        if self._bus is None:
            raise I2CException(f'Bus: {self.path} is not open')
        if address != self._address:
            ioctl(self._bus.fileno(), I2C.I2C_SLAVE, address & 0x7F)
            self._address = address

    def read(self, length: int = 1) -> bytes:
        '''
        Read amount of bytes back from i2c bus

        Args:
            length (int, optional): Number of bytes to read. Defaults to 1.

        Raises:
            I2CException: Bus is not open

        Returns:
            bytes: read from i2c bus
        '''
        if self._bus is None:
            raise I2CException(f'Bus: {self.path} is not open')
        return self._bus.read(length)

    def write(self, data: bytes):
        '''
        Write amount of bytes on i2c bus

        Args:
            data (bytes): bytes written on the bus

        Raises:
            I2CException: Bus is not open
        '''
        if self._bus is None:
            raise I2CException(f'Bus: {self.path} is not open')
        self._bus.write(data)

    def read_write(self, data: bytes, length: int = 1) -> bytes:
        '''
        Perform read write operation to get information back from device on bus

        Args:
            data (bytes): command to send device
            length (int, optional): number of bytes to read back. Defaults to 1.

        Raises:
            I2CException: Bus is not open

        Returns:
            bytes: infromation read back from device on bus
        '''
        if self._bus is None:
            raise I2CException(f'Bus: {self.path} is not open')
        self._bus.write(data)
        return self._bus.read(length)
