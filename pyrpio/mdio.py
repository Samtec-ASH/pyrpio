""" Handle MDIO interface via bitbang and SPI bus. """
from typing import List, Optional
from pyrpio.spi import SPI
from pyrpio import rpiolib


class MDIO:
    ''' Bit-bang MDIO interface. '''

    def __init__(self, clk_pin: int, data_pin: int):
        '''
        Bit-bang MDIO interface.
        Args:
            clk_pin (int): GPIO pin of clock
            data_pin (int): GPIO pin of data
        '''
        self.clk_pin = clk_pin
        self.data_pin = data_pin

    def open(self):
        ''' Open mdio bus. '''
        return rpiolib.mdio_open(self.clk_pin, self.data_pin)

    def close(self):
        ''' Close mdio bus. '''
        return rpiolib.mdio_close(self.clk_pin, self.data_pin)

    def read_c22_register(self, pad: int, reg: int):
        ''' Read reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
            Returns:
                int: 16-bit register value
        '''
        return rpiolib.mdio_c22_read(self.clk_pin, self.data_pin, pad, reg)

    def read_c45_register(self, pad: int, dad: int, reg: int):
        ''' Read reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|XX|16-bit reg]
            [00|11|5-bit pad|5-bit dad|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
            Returns:
                int: 16-bit register value
        '''
        return rpiolib.mdio_c45_read(self.clk_pin, self.data_pin, pad, dad, reg)

    def read_c45_dword_register(self, pad: int, dad: int, reg: int):
        ''' Read 32-bit reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|XX|16-bit LSB reg]
            [00|00|5-bit pad|5-bit dad|XX|16-bit MSB reg]
            [00|11|5-bit pad|5-bit dad|XX|16-bit LSB val]
            [00|11|5-bit pad|5-bit dad|XX|16-bit MSB val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 32-bit register address
            Returns:
                int: 32-bit register value
        '''
        return rpiolib.mdio_c45_read_dword(self.clk_pin, self.data_pin, pad, dad, reg)

    def write_c22_register(self, pad: int, reg: int, val: int):
        ''' Write reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
                val (int): 16-bit register value
        '''
        return rpiolib.mdio_c22_write(self.clk_pin, self.data_pin, pad, reg, val)

    def write_c45_register(self, pad: int, dad: int, reg: int, val: int):
        ''' Write reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
                val (int): 16-bit register value
        '''
        return rpiolib.mdio_c45_write(self.clk_pin, self.data_pin, pad, dad, reg, val)

    def write_c45_dword_register(self, pad: int, dad: int, reg: int, val: int):
        ''' Write 32-bit reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit LSB reg]
            [00|00|5-bit pad|5-bit dad|01|16-bit MSB reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit LSB val]
            [00|01|5-bit pad|5-bit dad|01|16-bit MSB val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 32-bit register address
                val (int): 32-bit register value
        '''
        return rpiolib.mdio_c45_write_dword(self.clk_pin, self.data_pin, pad, dad, reg, val)

    def read_c22_registers(self, pad: int, regs: List[int]):
        ''' Read multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        '''
        return [self.read_c22_register(pad, reg) for reg in regs]

    def read_c45_registers(self, pad: int, dad: int, regs: List[int]):
        ''' Read multiple registers in CLAUSE45.
            NOTE: C45 supports read and addr++ but not sure if supported.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        '''
        return [self.read_c45_register(pad, dad, reg) for reg in regs]

    def read_c45_dword_registers(self, pad: int, dad: int, regs: List[int]):
        ''' Read multiple dword registers in CLAUSE45.
            NOTE: C45 supports read and addr++ but not sure if supported.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 32-bit register addreses
            Return:
                List[int]: List of 32-bit register values
        '''
        return [self.read_c45_dword_register(pad, dad, reg) for reg in regs]

    def write_c22_registers(self, pad: int, regs: List[int], vals: List[int]):
        ''' Write multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
                vals (List[int]): List of 16-bit register values
        '''
        return [self.write_c22_register(pad, reg, val) for reg, val in zip(regs, vals)]

    def write_c45_registers(self, pad: int, dad: int, regs: List[int], vals: List[int]):
        ''' Write multiple registers in CLAUSE45.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
                vals (List[int]): List of 16-bit register values
        '''
        return [self.write_c45_register(pad, dad, reg, val) for reg, val in zip(regs, vals)]

    def write_c45_dword_registers(self, pad: int, dad: int, regs: List[int], vals: List[int]):
        ''' Write multiple dword registers in CLAUSE45.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 32-bit register addreses
                vals (List[int]): List of 32-bit register values
        '''
        return [self.write_c45_dword_register(pad, dad, reg, val) for reg, val in zip(regs, vals)]


class MDIOSPI:
    '''Peform MDIO over SPI interface.
    Requires MOSI and MISO to be tied together with external pull-up
    Chip select is not used either since MDIO packet contains phy_addr
    '''
    C22_FRAME = 0x01
    C45_FRAME = 0x00
    OP_C22_WR = 0x01
    OP_C22_RD = 0x02
    OP_C45_AD = 0x00
    OP_C45_WR = 0x01
    OP_C45_RD_INC = 0x02
    OP_C45_RD = 0x03

    def __init__(self, path: str = '/dev/spidev0.0'):
        '''
            SPI-based MDIO interface.
            Args:
                path: spidev bus path
        '''
        self.path: str = path
        self._bus: Optional[SPI]

    def open(self, speed_hz: int = 5000):
        ''' Open mdio bus. '''
        self._bus = SPI(self.path, 0, speed_hz, extra_flags=SPI.SPI_3WIRE)

    def close(self):
        ''' Close mdio bus. '''
        self._bus.close()

    def mdio_flush(self):
        ''' Flush bus by sending 32 1's '''
        self._bus.transfer(tx_data=(0xFFFFFFFF).to_bytes(4, byteorder='big'), cs_change=False)

    def mdio_xfer(self, st: int, op: int, pad: int, dad: int, tat: int = 0x2, val: int = 0xFFFF):
        ''' Perform low-level 32-bit frame transfer.
            Args:
                st (int): 2-bit start field
                op (int): 2-bit operation field
                pad (int): 5-bit physical address
                dad (int): 5-bit register address / device type
                tat (int): 2-bit turn around field
                val (int): 16-bit write value
        '''
        is_read = op in [MDIOSPI.OP_C22_RD, MDIOSPI.OP_C45_RD, MDIOSPI.OP_C45_RD_INC]
        # Construct 16-bit header
        # Flush 32-bits
        self.mdio_flush()
        # Transfer 16-bit header
        tat = 0x3 if is_read else tat
        hdr = (st & 0x3) << 14 | (op & 0x3) << 12 | (pad & 0x1F) << 7 | (dad & 0x1F) << 2 | (tat & 0x3)
        self._bus.transfer(tx_data=hdr.to_bytes(2, byteorder='big'), cs_change=False)
        # Read next 16 bits
        if is_read:
            rst = self._bus.transfer(rx_data=val.to_bytes(2, byteorder='big'), cs_change=False)
            val = int.from_bytes(rst, byteorder='big') & 0xFFFF
        else:
            self._bus.transfer(tx_data=hdr.to_bytes(2, byteorder='big'), cs_change=False)
        # self.mdio_flush()
        return val

    def read_c22_register(self, pad: int, reg: int):
        ''' Read reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
            Returns:
                int: 16-bit register value
        '''
        val = self.mdio_xfer(MDIOSPI.C22_FRAME, MDIOSPI.OP_C22_RD, pad=pad, dad=reg)
        return val

    def read_c45_register(self, pad: int, dad: int, reg: int):
        ''' Read reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|XX|16-bit reg]
            [00|11|5-bit pad|5-bit dad|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
            Returns:
                int: 16-bit register value
        '''
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_AD, pad=pad, dad=dad, val=reg)
        val = self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_RD, pad=pad, dad=dad)
        return val

    def write_c22_register(self, pad: int, reg: int, val: int):
        ''' Write reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
                val (int): 16-bit register value
        '''
        self.mdio_xfer(MDIOSPI.C22_FRAME, MDIOSPI.OP_C22_WR, pad=pad, dad=reg, val=val)

    def write_c45_register(self, pad: int, dad: int, reg: int, val: int):
        ''' Write reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
                val (int): 16-bit register value
        '''
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_AD, pad=pad, dad=dad, val=reg)
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_RD, pad=pad, dad=dad, val=val)

    def read_c22_registers(self, pad: int, regs: List[int]):
        ''' Read multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        '''
        return [self.read_c22_register(pad, reg) for reg in regs]

    def read_c45_registers(self, pad: int, dad: int, regs: List[int]):
        ''' Read multiple registers in CLAUSE45.
            NOTE: C45 supports read and addr++ but not sure if supported.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        '''
        return [self.read_c45_register(pad, dad, reg) for reg in regs]

    def write_c22_registers(self, pad: int, regs: List[int], vals: List[int]):
        ''' Write multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
                vals (List[int]): List of 16-bit register values
        '''
        return [self.write_c22_register(pad, reg, val) for reg, val in zip(regs, vals)]

    def write_c45_registers(self, pad: int, dad: int, regs: List[int], vals: List[int]):
        ''' Write multiple registers in CLAUSE45.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
                vals (List[int]): List of 16-bit register values
        '''
        return [self.write_c45_register(pad, dad, reg, val) for reg, val in zip(regs, vals)]
