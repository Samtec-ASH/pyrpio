""" I2C Types """
from abc import ABC
from typing import Optional, List, Union
from dataclasses import dataclass

class I2CError(IOError):
    """
    Exceptions that occur during i2c operations. (before OS level ops)
    """
    ...

@dataclass
class I2CMessage:
    """ I2C message for transfer operation. """
    data: Union[bytes, bytearray, List[int]]
    read: bool
    flags: int

class I2CBase(ABC):
    """ Abstract base class for I2C. """
    def open(self):
        """ Open the i2c bus. """
        raise NotImplementedError()

    def close(self):
        """ Close the i2c bus. """
        raise NotImplementedError()

    def set_address(self, address: int):
        """
        Set the i2c bus address if it has changed

        Args:
            address (int): address of i2c device

        Raises:
            I2CError: Bus is not open
        """
        raise NotImplementedError()

    def read(self, length: int = 1) -> bytes:
        """
        Read amount of bytes back from i2c bus

        Args:
            length (int, optional): Number of bytes to read. Defaults to 1.

        Raises:
            I2CError: Bus is not open

        Returns:
            bytes: read from i2c bus
        """
        raise NotImplementedError()

    def write(self, data: bytes):
        """
        Write amount of bytes on i2c bus

        Args:
            data (bytes): bytes written on the bus

        Raises:
            I2CError: Bus is not open
        """
        raise NotImplementedError()

    def read_write(self, data: bytes, length: int = 1) -> bytes:
        """
        Perform read write operation to get information back from device on bus

        Args:
            data (bytes): command to send device
            length (int, optional): number of bytes to read back. Defaults to 1.

        Raises:
            I2CError: Bus is not open

        Returns:
            bytes: infromation read back from device on bus
        """
        raise NotImplementedError()

    def transfer(self, address: int, messages: List[I2CMessage]):
        """Transfer `messages` to the specified I2C `address`. Modifies the
        `messages` array with the results of any read transactions.
        Args:
            address (int): I2C address.
            messages (list): list of I2C.Message messages.
        Raises:
            I2CError: if an I/O or OS error occurs.
            TypeError: if `messages` type is not list.
            ValueError: if `messages` length is zero, or if message data is not valid bytes.
        """
        raise NotImplementedError()

    def detect(self, first: int = 0x03, last: int = 0x77, data: Optional[bytes] = None, length: int = 1) -> List[int]:
        """
        Scans bus looking for devices.

        Args:
            first (int, optional): first address (inclusive). Defaults to 0x03
            last  (int, optional): last address (inclusive). Defaults to 0x77
            data (bytes, optional): Attempt to write given data. Defaults to None
            length (int, optional): Number of bytes to read. Defaults to 1

        Returns:
            List[int]: List of device base-10 addresses that responded.
        """
        raise NotImplementedError()
