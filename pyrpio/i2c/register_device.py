'''
Create a generic register device that runs over I2C
'''
import struct
from typing import Collection, Tuple

from .i2c import I2C


FORMAT_SIZE = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}


class I2CRegisterDevice:
    '''
    Generic I2C device that implements registers
    '''

    def __init__(self, bus: I2C, address: int, register_size: int = 1, data_size: int = 1):
        '''
        [summary]

        Args:
            bus (I2C): i2c bus to use to communicate with the device
            address (int): i2c address of the device
            register_size (int, optional): register address size in bytes. Defaults to 1.
            data_size (int, optional): register size in bytes. Defaults to 1.
        '''
        self._bus = bus
        self._address = address
        self._register_size = register_size
        self._data_size = data_size

    def read_register(self, register: int) -> int:
        '''
        [summary]

        Args:
            register (int): [description]

        Returns:
            int: [description]
        '''
        return int.from_bytes(self.read_register_bytes(register), byteorder='big')

    def read_register_bytes(self, register: int) -> bytes:
        '''
        [summary]

        Args:
            register (int): [description]

        Returns:
            bytes: [description]
        '''
        self._bus.set_address(self._address)
        return self._bus.read_write(register.to_bytes(length=self._register_size, byteorder='big'), self._data_size)

    def write_register(self, register: int, data: int):
        '''
        [summary]

        Args:
            register (int): [description]
            data (int): [description]
        '''
        self.write_register_bytes(register, data.to_bytes(length=self._data_size, byteorder='big'))

    def write_register_bytes(self, register: int, data: bytes):
        '''
        [summary]

        Args:
            register (int): [description]
            data (bytes): [description]
        '''
        self._bus.set_address(self._address)
        message = register.to_bytes(length=self._register_size, byteorder='big') + data
        self._bus.write(message)

    def read_register_sequential(self, register: int, length: int) -> Tuple[int]:
        '''
        [summary]

        Args:
            register (int): [description]
            length (int): [description]

        Returns:
            Tuple[int]: [description]
        '''
        self._bus.set_address(self._address)
        data_bytes = self.read_register_sequential_bytes(register, length)
        return struct.unpack(f'>{length}{FORMAT_SIZE[self._data_size]}', data_bytes)

    def read_register_sequential_bytes(self, register: int, length: int) -> bytes:
        '''
        [summary]

        Args:
            register (int): [description]
            length (int): [description]

        Returns:
            bytes: [description]
        '''
        self._bus.set_address(self._address)
        return self._bus.read_write(
            data=register.to_bytes(length=self._register_size, byteorder='big'),
            length=self._data_size * length
        )

    def write_register_sequential(self, register: int, data: Collection[int]):
        '''
        [summary]

        Args:
            register (int): [description]
            data (Collection[int]): [description]
        '''
        self.write_register_sequential_bytes(register, struct.pack(
            f'>{len(data)}{FORMAT_SIZE[self._data_size]}', *data))

    def write_register_sequential_bytes(self, register: int, data: bytes):
        '''
        [summary]

        Args:
            register (int): [description]
            data (bytes): [description]
        '''
        self._bus.set_address(self._address)
        message = register.to_bytes(length=self._register_size, byteorder='big') + data
        self._bus.write(message)
