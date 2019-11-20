import pytest
import pyrpio
from pyrpio.mdio import MDIO


def mock_mdio_open(clk_pin, data_pin):
    return 0


def mock_mdio_close(clk_pin, data_pin):
    return 0


def mock_mdio_c22_read(clk_pin, data_pin, pad, reg):
    return 0


def mock_mdio_c45_read(clk_pin, data_pin, pad, dad, reg):
    return 0


def mock_mdio_c45_read_dword(clk_pin, data_pin, pad, dad, reg):
    return 0


def mock_mdio_c22_write(clk_pin, data_pin, pad, reg, val):
    return 0


def mock_mdio_c45_write(clk_pin, data_pin, pad, dad, reg, val):
    return 0


def mock_mdio_c45_write_dword(clk_pin, data_pin, pad, dad, reg, val):
    return 0


# Override C extension definitions w/ mock routines
pyrpio.rpiolib.mdio_open = mock_mdio_open
pyrpio.rpiolib.mdio_close = mock_mdio_close
pyrpio.rpiolib.mdio_c22_read = mock_mdio_c22_read
pyrpio.rpiolib.mdio_c22_write = mock_mdio_c22_write
pyrpio.rpiolib.mdio_c45_read = mock_mdio_c45_read
pyrpio.rpiolib.mdio_c45_write = mock_mdio_c45_write
pyrpio.rpiolib.mdio_c45_read_dword = mock_mdio_c45_read_dword
pyrpio.rpiolib.mdio_c45_write_dword = mock_mdio_c45_write_dword


class TestMDIO:
    def test_open(self):
        m = MDIO(1, 2)
        rst = m.open()
        assert rst == 0
        rst = m.close()
        assert rst == 0

    def test_transfer(self):
        m = MDIO(1, 2)
        rst = m.open()
        m.write_c22_register(0x01, 0x02, 0x03)
        val = m.read_c22_register(0x01, 0x02)
        assert val == 0
