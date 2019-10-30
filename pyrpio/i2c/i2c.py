import struct
from fcntl import ioctl
from typing import List, Optional, IO

class I2C:
    I2C_SLAVE = 0x0703
    def __init__(self, path: str = '/dev/i2c-1'):
        self.path: str = path
        self._bus: Optional[IO] = None

    def open(self):
        ''' Open i2c bus. '''
        if not self._bus:
            self._bus = open(self.path, 'r+b', buffering=0)

    def close(self):
        ''' Close i2c bus. '''
        if self._bus:
            self._bus.close()
        self._bus.close()

    def set_address(self, address: int):
        ''' Set i2c address. '''
        ioctl(self._bus.fileno(), I2C.I2C_SLAVE, address & 0x7F)

    def read(self, length: int):
        ''' Low-level i2c read given # bytes as length. '''
        return self._bus.read(length)

    def write(self, data: bytes):
        ''' Low-level i2c write given bytes. '''
        self._bus.write(data)

    def fmt_lookup(self, nbytes: int, signed: bool=False):
        '''Helper routine used in struct un/pack of bytes <-> values '''
        table = {1:'B', 2: 'H', 4: 'L', 8: 'Q'}
        fmt: str = table.get(nbytes, 's')
        return fmt.lower() if signed else fmt

    def values_to_bytes(self, values: List[int], nbytes: int=1, fmt: Optional[str]=None, signed: bool=False):
        ''' Convert list of ints to bytes in given format. '''
        fmt = self.fmt_lookup(nbytes, signed) if not fmt else fmt
        values = [values] if isinstance(values, int) else values
        return struct.pack(f'>{len(values)}{fmt}', *values)

    def bytes_to_values(self, data: bytes, nbytes: int=1, fmt: Optional[str]=None, signed: bool=False):
        ''' Convert bytes to list of ints in given format. '''
        fmt = self.fmt_lookup(nbytes, signed) if not fmt else fmt
        return struct.unpack(f'>{len(data)//nbytes}{fmt}', data)

    def read_register(self, register: int, reg_nbytes: int=1, val_nbytes: int=1, fmt: Optional[str]=None, signed: bool=False):
        ''' Read from register-based i2c device. Enable specifying address size and data size/format. '''
        self.write(self.values_to_bytes(register, nbytes=reg_nbytes))
        return self.bytes_to_values(self.read(val_nbytes), nbytes=val_nbytes, fmt=fmt, signed=signed)[0]

    def write_register(self, register: int, value: int, reg_nbytes: int=1, val_nbytes: int=1, fmt:Optional[str]=None, signed: bool=False):
        ''' Write to register-based i2c device. Enable specifying address size and data size/format. '''
        self.write(
            self.values_to_bytes(register, nbytes=reg_nbytes) +
            self.values_to_bytes([value], nbytes=val_nbytes, fmt=fmt, signed=signed)
        )

    def read_register_sequential(self, register: int, length: int, reg_nbytes=1, val_nbytes=1, fmt:Optional[str]=None, signed: bool=False):
        ''' Read sequential registers. Enable specifying address size and data size/format.
            NOTE: Not all devices support auto-incrementing address or can have limits on length.
        '''
        self.write(self.values_to_bytes(register, nbytes=reg_nbytes))
        data = self.read(val_nbytes*length)
        return self.bytes_to_values(data, nbytes=val_nbytes, fmt=fmt, signed=signed)

    def write_register_sequential(self, register: int, values: List[int], reg_nbytes:int=1, val_nbytes:int=1, fmt:Optional[str]=None, signed: bool=False):
        ''' Write sequential registers. Enable specifying address size and data size/format.
            NOTE: Not all devices support auto-incrementing address or can have limits on length.
        '''
        self.write(
            self.values_to_bytes(register, nbytes=reg_nbytes) +
            self.values_to_bytes(values, nbytes=val_nbytes, fmt=fmt, signed=signed)
        )

    def read_word_register(self, register: int):
        ''' Convenience to read word length register (both address and data). '''
        return self.read_register(register, reg_nbytes=2, val_nbytes=2)

    def write_word_register(self, register: int):
        ''' Convenience to write word length register (both address and data). '''
        self.write_register(register, reg_nbytes=2, val_nbytes=2)

    def read_word_register_sequential(self, register: int, length: int):
        ''' Convenience to read sequential word length registers (both address and data). '''
        return self.read_register_sequential(register, length, reg_nbytes=2, val_nbytes=2)

    def write_word_register_sequential(self, register: int, values: List[int]):
        ''' Convenience to write sequential word length registers (both address and data). '''
        return self.write_register_sequential(register, values, reg_nbytes=2, val_nbytes=2)
