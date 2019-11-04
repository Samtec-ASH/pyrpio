from typing import List
import spidev
from pyrpio import rpiolib

class MDIO:
    def __init__(self, clk_pin: int, data_pin: int):
        self.clk_pin = clk_pin
        self.data_pin = data_pin

    def open(self):
        ''' Open mdio bus. '''
        rpiolib.mdio_open(self.clk_pin, self.data_pin)

    def close(self):
        ''' Close mdio bus. '''
        rpiolib.mdio_close(self.clk_pin, self.data_pin)

    def read_c22_register(self, pad: int, reg: int):
        ''' Read reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|XX|16-bit val]'''
        return rpiolib.mdio_c22_read(self.clk_pin, self.data_pin, pad, reg)

    def read_c45_register(self, pad: int, dad: int, reg: int):
        ''' Read reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|XX|16-bit reg]
            [00|11|5-bit pad|5-bit dad|XX|16-bit val]
        '''
        return rpiolib.mdio_c45_read(self.clk_pin, self.data_pin, pad, dad, reg)

    def write_c22_register(self, pad: int, reg: int, val: int):
        ''' Write reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|01|16-bit val]'''
        rpiolib.mdio_c22_write(self.clk_pin, self.data_pin, pad, reg, val)

    def write_c45_register(self, pad: int, dad: int, reg: int, val: int):
        ''' Write reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit val]
        '''
        rpiolib.mdio_c45_write(self.clk_pin, self.data_pin, pad, dad, reg, val)

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


class MDIOSPI:
    """Peform MDIO over SPI interface.
    Requires MOSI and MISO to be tied together with external pull-up
    Chip select is not used either since MDIO packet contains phy_addr
    """
    C22_FRAME = 0x01
    C45_FRAME = 0x00
    OP_C22_WR = 0x01
    OP_C22_RD = 0x02
    OP_C45_AD = 0x00
    OP_C45_WR = 0x01
    OP_C45_RD_INC = 0x02
    OP_C45_RD = 0x03

    def __init__(self, path: str='/dev/spi-1'):
        self.path: str = path
        self._bus: spidev.SpiDev()

    def open(self, speed_hz: int=5000):
        self._bus.open()
        self._bus.max_speed_hz = speed_hz
        self._bus.no_cs = True # Dont need chip select
        self._bus.mode = 0 # Mode 0: Clock pulse on 1, posedge data valid
        self._bus.threewire = True
        self._bus.bits_per_word = 32

    def close(self):
        self._bus.close()

    def mdio_flush(self):
        # Send 32-bit 1s to flush
        rst = self._bus.xfer((0xFFFFFFFF).to_bytes(4, byteorder='big'))

    def mdio_xfer(self, st: int, op: int, pad: int, dad: int, tat: int=0x3, val: int = 0xFFFF):
        # Construct 32-bit packet (16-bit header and 16-bit data)
        hdr = ( st & 0x03) << 14 |\
              ( op & 0x03) << 12 |\
              (pad & 0x1F) <<  7 |\
              (dad & 0x1F) <<  2 |\
              (tat & 0x03) <<  0
        packet = (hdr << 16) & (val & 0xFFFF)
        # Flush (ignore input)
        self.mdio_flush()
        # Transfer packet (on reads we write fake 1's to get data back)
        rst = self._bus.xfer(packet.to_bytes(4, byteorder='big'))
        # Flush (ignore input)
        self.mdio_flush()
        # Extract 16-bit data regardless of operation
        return int.from_bytes(rst, byteorder='big') & 0xFFFF

    def read_c22_register(self, pad: int, reg: int):
        # Read register in one transaction
        val = self.mdio_xfer(MDIOSPI.C22_FRAME, MDIOSPI.OP_C22_RD, pad=pad, dad=reg)
        return val

    def read_c45_register(self, pad: int, dad: int, reg: int):
        # Write register address
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_AD, pad=pad, dad=dad, val=reg)
        # Read register data
        val = self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_RD, pad=pad, dad=dad)
        return val

    def write_c22_register(self, pad: int, reg: int, val: int):
        # Read register in one transaction
        self.mdio_xfer(MDIOSPI.C22_FRAME, MDIOSPI.OP_C22_WR, pad=pad, dad=reg, val=val)

    def write_c45_register(self, pad: int, dad: int, reg: int, val: int):
        # Write register address
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_AD, pad=pad, dad=dad, val=reg)
        # Write register data
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_RD, pad=pad, dad=dad, val=val)
