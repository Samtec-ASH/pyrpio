""" Create a generic register device that runs over I2C. """
import struct
from typing import Collection, Tuple, Optional
from .i2c.types import I2CBase


class I2CRegisterDevice:
    """
    Generic I2C device that implements registers.
    """
    FORMAT_SIZE = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}

    def __init__(self, bus: I2CBase, address: int, register_size: int = 1, data_size: int = 1):
        """
        Generic I2C device that implements registers.

        Args:
            bus (I2C): i2c bus to use to communicate with the device
            address (int): i2c address of the device
            register_size (int, optional): register address size in bytes. Defaults to 1.
            data_size (int, optional): register size in bytes. Defaults to 1.
        """
        self._bus = bus
        self._address = address
        self._register_size = register_size
        self._data_size = data_size

    def read_register(self, register: int, mask: Optional[int] = None) -> int:
        """
        Read single register as int

        Args:
            register (int): Register address

        Returns:
            int: Register value
        """
        value = int.from_bytes(self.read_register_bytes(register), byteorder='big')
        if mask is not None:
            value = value & mask
        return value

    def read_register_bytes(self, register: int) -> bytes:
        """
        Read single register as bytes

        Args:
            register (int): Register address

        Returns:
            bytes: Register bytes
        """
        self._bus.set_address(self._address)
        return self._bus.read_write(register.to_bytes(length=self._register_size, byteorder='big'), self._data_size)

    def write_register(self, register: int, data: int, mask: Optional[int] = None):
        """
        Write int data to signle register.

        Args:
            register (int): Register address
            data (int): Register value as int
        """
        if mask is not None:
            pdata = self.read_register(register, mask=~mask)  # pylint: disable=E1130
            data = pdata | (data & mask)
        self.write_register_bytes(register, data.to_bytes(length=self._data_size, byteorder='big'))

    def write_register_bytes(self, register: int, data: bytes):
        """
        Write bytes data to single register.

        Args:
            register (int): Register address
            data (bytes): Register value as raw bytes
        """
        self._bus.set_address(self._address)
        message = register.to_bytes(length=self._register_size, byteorder='big') + data
        self._bus.write(message)

    def read_register_sequential(self, register: int, length: int) -> Tuple[int]:
        """
        Read sequential registers by issuing repeated i2c starts to increment address.
        Ensure device supports auto-incrementing address on repeated starts.

        Args:
            register (int): Start register address
            length (int): Number of registers to read

        Returns:
            Tuple[int]: Register values
        """
        self._bus.set_address(self._address)
        data_bytes = self.read_register_sequential_bytes(register, length)
        # pylint: disable=E1101
        return struct.unpack(f'>{length}{I2CRegisterDevice.FORMAT_SIZE[self._data_size]}', data_bytes)

    def read_register_sequential_bytes(self, register: int, length: int) -> bytes:
        """
        Read sequential registers by issuing repeated i2c starts to increment address.
        Ensure device supports auto-incrementing address on repeated starts.

        Args:
            register (int): Start register address
            length (int): Number of registers to read

        Returns:
            bytes: Register values as raw bytes
        """
        self._bus.set_address(self._address)
        return self._bus.read_write(
            data=register.to_bytes(length=self._register_size, byteorder='big'),
            length=self._data_size * length
        )

    def write_register_sequential(self, register: int, data: Collection[int]):
        """
        Write sequential registers by issuing repeated i2c starts to increment address.
        Ensure device supports auto-incrementing address on repeated starts.

        Args:
            register (int): Start register address
            data (Collection[int]): Register values to write
        """
        # pylint: disable=E1101
        self.write_register_sequential_bytes(register, struct.pack(
            f'>{len(data)}{I2CRegisterDevice.FORMAT_SIZE[self._data_size]}', *data))

    def write_register_sequential_bytes(self, register: int, data: bytes):
        """
        Write sequential registers by issuing repeated i2c starts to increment address.
        Ensure device supports auto-incrementing address on repeated starts.

        Args:
            register (int): Start egister address
            data (bytes): Raw bytes to write
        """
        self._bus.set_address(self._address)
        message = register.to_bytes(length=self._register_size, byteorder='big') + data
        self._bus.write(message)
