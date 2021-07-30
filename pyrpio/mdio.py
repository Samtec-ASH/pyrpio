""" Handle MDIO interface via bitbang and SPI bus. """
from typing import List, Optional
from pyrpio.gpio import CdevGPIO
from pyrpio.spi import SPI

class MDIO:
    """ Bit-bang MDIO interface. """
    C22_FRAME = 0x01
    C45_FRAME = 0x00
    OP_C22_WR = 0x01
    OP_C22_RD = 0x02
    OP_C45_AD = 0x00
    OP_C45_WR = 0x01
    OP_C45_RD_INC = 0x02
    OP_C45_RD = 0x03

    def __init__(self, clk_pin: int, data_pin: int, path: str, **kwargs):
        """
        Bit-bang MDIO interface via cdev gpio.
        Args:
            clk_pin (int): GPIO pin of clock
            data_pin (int): GPIO pin of data
        """
        self.clk_pin = clk_pin
        self.data_pin = data_pin
        self.clk_gpio = CdevGPIO(path=path, line=clk_pin, direction="low")
        self.data_gpio = CdevGPIO(path=path, line=data_pin, direction="high", bias="pull_up")
        self._clock_delay = kwargs.get('clock_delay', 50)
        self._setup_delay = kwargs.get('setup_delay', 10)
        self._read_delay = kwargs.get('read_delay', 1000)

    def open(self):
        """ Open mdio bus. """

    def close(self):
        """ Close mdio bus. """
        self.clk_gpio.close()
        self.data_gpio.close()

    def _ndelay(self, delay):  # pylint: disable=no-self-use
        while delay > 0:
            delay -= 1

    def _write_bit(self, val: int):
        self._ndelay(self._clock_delay)
        self.data_gpio.write(bool(val))
        self._ndelay(self._setup_delay)
        self.clk_gpio.write(True)
        self._ndelay(self._clock_delay)
        self.clk_gpio.write(False)

    def _read_bit(self) -> int:
        self._ndelay(self._clock_delay)
        v = int(self.data_gpio.read())
        self._ndelay(self._setup_delay)
        self.clk_gpio.write(True)
        self._ndelay(self._clock_delay)
        self.clk_gpio.write(False)
        return v

    def _write_bits(self, val, bits):
        for i in range(bits - 1, -1, -1):
            self._write_bit((val >> i) & 1)

    def _read_bits(self, bits) -> int:
        ret = 0
        for _ in range(bits - 1, -1, -1):
            ret <<= 1
            ret |= self._read_bit()
        return ret

    def _flush(self):
        for _ in range(32):
            self._write_bit(1)

    def _cmd(self, sf, op, pad, dad):
        # Preamble
        self._flush()
        # Header
        self._write_bits(sf & 3, 2)  # Start frame
        self._write_bits(op & 3, 2)  # OP Code
        self._write_bits(pad, 5)  # Phy addr
        self._write_bits(dad, 5)  # Reg addr(C22) / dev type(C45)

    def _c45_write_addr(self, pad: int, dad: int, reg: int):
        # Send preamble/header - C45 - ADDR
        self._cmd(MDIO.C45_FRAME, MDIO.OP_C45_AD, pad, dad)
        # Send the turnaround(10)
        self._write_bits(2, 2)
        # Send 16-bit value
        self._write_bits(reg, 16)
        return 0

    def _c45_write_val(self, pad: int, dad: int, val: int):
        # Send preamble/header - C45 - WRITE
        self._cmd(MDIO.C45_FRAME, MDIO.OP_C45_WR, pad, dad)
        # Send the turnaround(10)
        self._write_bits(2, 2)
        # Send 16-bit value
        self._write_bits(val, 16)
        return 0

    def _c45_read_val(self, pad: int, dad: int) -> int:
        # Send preamble/header
        self._cmd(MDIO.C45_FRAME, MDIO.OP_C45_RD, pad, dad)
        # Release data pin
        self.data_gpio.direction = "in"
        self._ndelay(self._read_delay)
        # Read 2-bit turnaround(gives slave time)
        self._read_bits(2)
        # Read 16-bit value
        ret = self._read_bits(16)
        # Capture data pin
        self.data_gpio.direction = "high"
        return ret

    def read_c22_register(self, pad: int, reg: int):
        """ Read reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
            Returns:
                int: 16-bit register value
        """
        # Send preamble/header
        self._cmd(MDIO.C22_FRAME, MDIO.OP_C22_RD, pad, reg)
        # Release data pin
        self.data_gpio.direction = "in"
        self._ndelay(self._read_delay)
        # Read 2-bit turnaround (gives slave time)
        self._read_bits(2)
        # Read 16-bit value
        ret = self._read_bits(16)
        # Capture data pin
        self.data_gpio.direction = "high"
        self._flush()
        return ret

    def read_c45_register(self, pad: int, dad: int, reg: int):
        """ Read reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|XX|16-bit reg]
            [00|11|5-bit pad|5-bit dad|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
            Returns:
                int: 16-bit register value
        """
        self._c45_write_addr(pad, dad, reg)
        val = self._c45_read_val(pad, dad)
        self._flush()
        return val

    def read_c45_dword_register(self, pad: int, dad: int, reg: int):
        """ Read 32-bit reg in CLAUSE45.
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
        """
        self._c45_write_addr(pad, dad, reg & 0xFFFF)
        self._c45_write_addr(pad, dad, reg >> 16)
        val_lsb = self._c45_read_val(pad, dad)
        val_msb = self._c45_read_val(pad, dad)
        self._flush()
        return (val_msb << 16) & (val_lsb & 0xFFFF)

    def write_c22_register(self, pad: int, reg: int, val: int):
        """ Write reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
                val (int): 16-bit register value
        """
        # Send preamble/header
        self._cmd(MDIO.C22_FRAME, MDIO.OP_C22_WR, pad, reg)
        # Send the turnaround (10)
        self._write_bits(2, 2)
        # Send 16-bit value
        self._write_bits(val, 16)
        self._flush()

    def write_c45_register(self, pad: int, dad: int, reg: int, val: int):
        """ Write reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
                val (int): 16-bit register value
        """
        self._c45_write_addr(pad, dad, reg)
        rst = self._c45_write_val(pad, dad, val)
        self._flush()
        return rst

    def write_c45_dword_register(self, pad: int, dad: int, reg: int, val: int):
        """ Write 32-bit reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit LSB reg]
            [00|00|5-bit pad|5-bit dad|01|16-bit MSB reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit LSB val]
            [00|01|5-bit pad|5-bit dad|01|16-bit MSB val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 32-bit register address
                val (int): 32-bit register value
        """
        self._c45_write_addr(pad, dad, reg & 0xFFFF)
        self._c45_write_addr(pad, dad, reg >> 16)
        rst = self._c45_write_val(pad, dad, val & 0xFFFF)
        rst |= self._c45_write_val(pad, dad, val >> 16)
        self._flush()
        return rst

    def read_c22_registers(self, pad: int, regs: List[int]):
        """ Read multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        """
        return [self.read_c22_register(pad, reg) for reg in regs]

    def read_c45_registers(self, pad: int, dad: int, regs: List[int]):
        """ Read multiple registers in CLAUSE45.
            NOTE: C45 supports read and addr++ but not sure if supported.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        """
        return [self.read_c45_register(pad, dad, reg) for reg in regs]

    def read_c45_dword_registers(self, pad: int, dad: int, regs: List[int]):
        """ Read multiple dword registers in CLAUSE45.
            NOTE: C45 supports read and addr++ but not sure if supported.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 32-bit register addreses
            Return:
                List[int]: List of 32-bit register values
        """
        return [self.read_c45_dword_register(pad, dad, reg) for reg in regs]

    def write_c22_registers(self, pad: int, regs: List[int], vals: List[int]):
        """ Write multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
                vals (List[int]): List of 16-bit register values
        """
        return [self.write_c22_register(pad, reg, val) for reg, val in zip(regs, vals)]

    def write_c45_registers(self, pad: int, dad: int, regs: List[int], vals: List[int]):
        """ Write multiple registers in CLAUSE45.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
                vals (List[int]): List of 16-bit register values
        """
        return [self.write_c45_register(pad, dad, reg, val) for reg, val in zip(regs, vals)]

    def write_c45_dword_registers(self, pad: int, dad: int, regs: List[int], vals: List[int]):
        """ Write multiple dword registers in CLAUSE45.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 32-bit register addreses
                vals (List[int]): List of 32-bit register values
        """
        return [self.write_c45_dword_register(pad, dad, reg, val) for reg, val in zip(regs, vals)]


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

    def __init__(self, path: str = '/dev/spidev0.0'):
        """
            SPI-based MDIO interface.
            Args:
                path: spidev bus path
        """
        self.path: str = path
        self._bus: Optional[SPI]

    def open(self, speed_hz: int = 5000):
        """ Open mdio bus. """
        self._bus = SPI(self.path, 0, speed_hz, extra_flags=SPI.SPI_3WIRE)

    def close(self):
        """ Close mdio bus. """
        self._bus.close()

    def mdio_flush(self):
        """ Flush bus by sending 32 1's """
        self._bus.transfer(tx_data=(0xFFFFFFFF).to_bytes(4, byteorder='big'), cs_change=False)

    def mdio_xfer(self, st: int, op: int, pad: int, dad: int, tat: int = 0x2, val: int = 0xFFFF):
        """ Perform low-level 32-bit frame transfer.
            Args:
                st (int): 2-bit start field
                op (int): 2-bit operation field
                pad (int): 5-bit physical address
                dad (int): 5-bit register address / device type
                tat (int): 2-bit turn around field
                val (int): 16-bit write value
        """
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
        """ Read reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
            Returns:
                int: 16-bit register value
        """
        val = self.mdio_xfer(MDIOSPI.C22_FRAME, MDIOSPI.OP_C22_RD, pad=pad, dad=reg)
        return val

    def read_c45_register(self, pad: int, dad: int, reg: int):
        """ Read reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|XX|16-bit reg]
            [00|11|5-bit pad|5-bit dad|XX|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
            Returns:
                int: 16-bit register value
        """
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_AD, pad=pad, dad=dad, val=reg)
        val = self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_RD, pad=pad, dad=dad)
        return val

    def write_c22_register(self, pad: int, reg: int, val: int):
        """ Write reg in CLAUSE22. [01|01|5-bit pad|5-bit reg|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                reg (int): 5-bit register address
                val (int): 16-bit register value
        """
        self.mdio_xfer(MDIOSPI.C22_FRAME, MDIOSPI.OP_C22_WR, pad=pad, dad=reg, val=val)

    def write_c45_register(self, pad: int, dad: int, reg: int, val: int):
        """ Write reg in CLAUSE45.
            [00|00|5-bit pad|5-bit dad|01|16-bit reg]
            [00|01|5-bit pad|5-bit dad|01|16-bit val]
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                reg (int): 16-bit register address
                val (int): 16-bit register value
        """
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_AD, pad=pad, dad=dad, val=reg)
        self.mdio_xfer(MDIOSPI.C45_FRAME, MDIOSPI.OP_C45_RD, pad=pad, dad=dad, val=val)

    def read_c22_registers(self, pad: int, regs: List[int]):
        """ Read multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        """
        return [self.read_c22_register(pad, reg) for reg in regs]

    def read_c45_registers(self, pad: int, dad: int, regs: List[int]):
        """ Read multiple registers in CLAUSE45.
            NOTE: C45 supports read and addr++ but not sure if supported.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
            Return:
                List[int]: List of 16-bit register values
        """
        return [self.read_c45_register(pad, dad, reg) for reg in regs]

    def write_c22_registers(self, pad: int, regs: List[int], vals: List[int]):
        """ Write multiple registers in CLAUSE22.
            Args:
                pad (int): 5-bit physical address
                regs (List[int]): List of 5-bit register addreses
                vals (List[int]): List of 16-bit register values
        """
        return [self.write_c22_register(pad, reg, val) for reg, val in zip(regs, vals)]

    def write_c45_registers(self, pad: int, dad: int, regs: List[int], vals: List[int]):
        """ Write multiple registers in CLAUSE45.
            Args:
                pad (int): 5-bit physical address
                dad (int): 5-bit device type
                regs (List[int]): List of 16-bit register addreses
                vals (List[int]): List of 16-bit register values
        """
        return [self.write_c45_register(pad, dad, reg, val) for reg, val in zip(regs, vals)]
