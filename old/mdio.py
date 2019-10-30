import os
from typing import List, Optional
import ctypes
from ctypes import cdll

class MDIOError(Structure):
    _fields_=[('c_errno', ctypes.c_int), ('errmsg', ctypes.c_char * 96)]
class MDIOHandle(Structure):
    _fields_=[("io", ctypes.c_uint8), ("clk", ctypes.c_uint8), ("error", MDIOError)]

def load_mdio_library(cmdio=None):
    lib_path = ctypes.util.find_library("mdio")
    cmdio = ctypes.LibraryLoader(ctypes.cdll).LoadLibrary(lib_path)
    cmdio.mdio_new.restype = ctypes.POINTER(MDIOHandle)
    cmdio.mdio_open.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8]
    cmdio.mdio_open.restype = ctypes.c_int
    cmdio.mdio_close.argtypes = [ctypes.c_void_p]
    cmdio.mdio_read_reg.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint16]
    cmdio.mdio_read_reg.restype = ctypes.c_uint16
    cmdio.mdio_write_reg.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint16]
    cmdio.mdio_write_reg.restype = ctypes.c_int
    return cmdio

class MDIO:
    def __init__(self, bus: str = 'mdio:/23/34'):
        self._mdio_lib = load_mdio_library()
        bus_parts = bus.split('/')
        self.clk_pin = int(bus_parts[-2])
        self.io_pin = int(bus_parts[-1])
        self._bus = self._cmdio.mdio_new()

    def open(self):
        self._mdio_lib.mdio_open(self._bus, clk_pin, io_pin)

    def close(self):
        self._mdio_lib.mdio_close(self._bus)

    def read(self, address: int, register: int, bshift: int = 0, nbits: int = 16):
        dev_addr = (0x1F0000 & register) >> 16
        reg_addr =  0x00FFFF & register
        value = self._mdio_lib.mdio_read_reg(self._bus, address, dev_addr, reg_addr)
        value = (value >> bshift) & pow(2,nbits-1)
        return value

    def write(self, address: int, register: int, value: int, bshift: int = 0, nbits: int = 16):
        dev_addr = (0x1F0000 & register) >> 16
        reg_addr =  0x00FFFF & register
        if nbits < 16:
            mask = 0xFFFF - (pow(2, nbits-1) << bshift)
            pvalue = self.read(address, register)
        value = ((value >> bshift) & pow(2,nbits-1)) + pvalue
        self._mdio_lib.mdio_write_reg(self._bus, address, dev_addr, reg_addr, value)
        return value

    def read_burst(self, address: int, registers: List[int]):
        values = [self.read(address, register) for register in registers]
        return 0

    def write_burst(self, address: int, registers: List[int], values: List[int]):
        for register, value in zip(registers, values):
            self.write(address, register, value)