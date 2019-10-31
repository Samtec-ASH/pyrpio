from pyrpio import mdiolib
from dataclasses import dataclass
from enum import Enum

class MDIO:
    def __init__(self, clk_pin: int, data_pin: int):
        self.clk_pin = clk_pin
        self.data_pin = data_pin

    def open(self):
        ''' Open mdio bus. '''
        mdiolib.mdio_open(self.clk_pin, self.data_pin)

    def close(self):
        ''' Close mdio bus. '''
        mdiolib.mdio_close(self.clk_pin, self.data_pin)

    def read_c22_register(self, pad: int, reg: int):
        ''' Read reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|XX|16-bit val]'''
        return mdiolib.mdio_c22_read(self.clk_pin, self.data_pin, pad, reg)

    def read_c45_register(self, pad: int, dad: int, reg: int):
        ''' Read reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|XX|16-bit reg]
            [00|11|5-bit pad|5-bit dad|XX|16-bit val]
        '''
        return mdiolib.mdio_c45_read(self.clk_pin, self.data_pin, pad, dad, reg)

    def write_c22_register(self, pad: int, reg: int, val: int):
        ''' Write reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|01|16-bit val]'''
        mdiolib.mdio_c22_write(self.clk_pin, self.data_pin, pad, reg, val)

    def write_c45_register(self, pad: int, dad: int, reg: int, val: int):
        ''' Write reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit val]
        '''
        mdiolib.mdio_c45_write(self.clk_pin, self.data_pin, pad, dad, reg, val)

    def read_c22_registers(self, pad: int, regs: List[int]):
        ''' Read multiple registers in CLAUSE22. '''
        return [self.read_c22_register(pad, reg) for reg in regs]

    def read_c45_registers(self, pad: int, dad: int, regs: List[int]):
        ''' Read multiple registers in CLAUSE45.
            NOTE: C45 supports read and addr++ but not sure if supported.
        '''
        return [self.read_c45_register(pad, dad, reg) for reg in regs]

    def write_c22_registers(self, pad: int, regs: List[int], vals: List[int]):
        ''' Write multiple registers in CLAUSE22. '''
        return [self.write_c22_register(pad, reg, val) for reg, val in zip(regs, vals)]

    def write_c45_registers(self, pad: int, dad: int, regs: List[int], vals: List[int]):
        ''' Write multiple registers in CLAUSE45. '''
        return [self.write_c45_register(pad, dad, reg, val) for reg, val in zip(regs, vals)]
