from fcntl import ioctl
import struct

class I2C:
    I2C_SLAVE = 0x0703
    def __init__(self, path):
        self.path = path
        self._bus = open(path, 'r+b', buffering=0)

    def set_address(self, address):
        ioctl(self._bus.fileno(), I2C.I2C_SLAVE, address & 0x7F)

    def read(self, length: int):
        return self._bus.read(length)

    def write(self, data: bytes):
        self._bus.write(data)

    def fmt_lookup(self, nbytes, signed=False):
        table = {1:'B', 2: 'H', 4: 'L', 8: 'Q'}
        fmt: str = table.get(nbytes, 's')
        return fmt.lower() if signed else fmt

    def register_to_bytes(self, register, reg_nbytes):
        return struct.pack(f'>{self.fmt_lookup(reg_nbytes)}', register)

    def values_to_bytes(self, values, nbytes=1, fmt=None, signed=False):
        fmt = self.fmt_lookup(nbytes, signed) if not fmt else fmt
        values = [values] if isinstance(values, int) else values
        return struct.unpack(f'>{len(values)}{fmt}', *values)

    def bytes_to_values(self, data, nbytes=1, fmt=None, signed=False):
        fmt = self.fmt_lookup(nbytes, signed) if not fmt else fmt
        return struct.unpack(f'>{len(data)//nbytes}{fmt}', data)

    def read_register(self, register: int, reg_nbytes=1, val_nbytes=1, fmt=None, signed=False):
        self.write(self.values_to_bytes(register, nbytes=reg_nbytes))
        return self.bytes_to_values(self.read(val_nbytes), nbytes=val_nbytes, fmt=fmt, signed=signed)[0]

    def write_register(self, register: int, value: int, reg_nbytes=1, val_nbytes=1, fmt=None, signed=False):
        self.write(
            self.values_to_bytes(register, nbytes=reg_nbytes) +
            self.values_to_bytes([value], nbytes=val_nbytes, fmt=fmt, signed=signed)
        )

    def read_register_sequential(self, register: int, length: int, reg_nbytes=1, val_nbytes=1, fmt=None, signed=False):
        self.write(self.values_to_bytes(register, nbytes=reg_nbytes))
        data = self.read(val_nbytes*length)
        return self.bytes_to_values(data, nbytes=val_nbytes, fmt=fmt, signed=signed)

    def write_register_sequential(self, register: int, values: int, reg_nbytes=1, val_nbytes=1, fmt=None, signed=False):
        self.write(
            self.values_to_bytes(register, nbytes=reg_nbytes) +
            self.values_to_bytes(values, nbytes=val_nbytes, fmt=fmt, signed=signed)
        )
