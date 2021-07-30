""" Direct HW Linux I2C Interface """

import fcntl
import ctypes
from typing import Optional, IO, List
from .types import I2CBase, I2CError, I2CMessage

class _CI2CMessage(ctypes.Structure):
    _fields_ = [
        ("addr", ctypes.c_ushort),
        ("flags", ctypes.c_ushort),
        ("len", ctypes.c_ushort),
        ("buf", ctypes.POINTER(ctypes.c_ubyte)),
    ]

class _CI2CIocTransfer(ctypes.Structure):
    _fields_ = [
        ("msgs", ctypes.POINTER(_CI2CMessage)),
        ("nmsgs", ctypes.c_uint),
    ]

class I2C(I2CBase):
    """ Controller to handle an I2C bus """
    I2C_SLAVE = 0x0703
    # Constants scraped from <linux/i2c-dev.h> and <linux/i2c.h>
    _I2C_IOC_FUNCS = 0x705
    _I2C_IOC_RDWR = 0x707
    _I2C_FUNC_I2C = 0x1
    _I2C_M_TEN = 0x0010
    _I2C_M_RD = 0x0001
    _I2C_M_STOP = 0x8000
    _I2C_M_NOSTART = 0x4000
    _I2C_M_REV_DIR_ADDR = 0x2000
    _I2C_M_IGNORE_NAK = 0x1000
    _I2C_M_NO_RD_ACK = 0x0800
    _I2C_M_RECV_LEN = 0x0400

    def __init__(self, path: str = '/dev/i2c-1'):
        """Create an i2c bus with 7-bit addressing

        Args:
            path (str, optional): I2C descriptor file path. Defaults to '/dev/i2c-1'.
        """
        self.path: str = path
        self._address = 0x0
        self._bus: Optional[IO[bytes]] = None

    def open(self):
        """
        Open the i2c bus
        """
        if not self._bus:
            self._bus = open(self.path, 'r+b', buffering=0)  # pylint: disable=consider-using-with
            self._address = 0x0

    def close(self):
        """
        Close the i2c bus
        """
        if self._bus:
            self._bus.close()
            self._bus = None

    def set_address(self, address: int):
        """
        Set the i2c bus address if it has changed

        Args:
            address (int): address of i2c device

        Raises:
            I2CError: Bus is not open
        """
        if self._bus is None:
            raise I2CError(f'Bus: {self.path} is not open')
        if address != self._address:
            fcntl.ioctl(self._bus.fileno(), I2C.I2C_SLAVE, address & 0x7F)
            self._address = address

    def read(self, length: int = 1) -> bytes:
        """
        Read amount of bytes back from i2c bus

        Args:
            length (int, optional): Number of bytes to read. Defaults to 1.

        Raises:
            I2CError: Bus is not open

        Returns:
            bytes: read from i2c bus
        """
        if self._bus is None:
            raise I2CError(f'Bus: {self.path} is not open')
        return self._bus.read(length)

    def write(self, data: bytes):
        """
        Write amount of bytes on i2c bus

        Args:
            data (bytes): bytes written on the bus

        Raises:
            I2CError: Bus is not open
        """
        if self._bus is None:
            raise I2CError(f'Bus: {self.path} is not open')
        self._bus.write(data)

    def read_write(self, data: bytes, length: int = 1) -> bytes:
        """
        Perform read write operation to get information back from device on bus

        Args:
            data (bytes): command to send device
            length (int, optional): number of bytes to read back. Defaults to 1.

        Raises:
            I2CError: Bus is not open

        Returns:
            bytes: infromation read back from device on bus
        """
        if self._bus is None:
            raise I2CError(f'Bus: {self.path} is not open')
        self._bus.write(data)
        return self._bus.read(length)

    def transfer(self, address: int, messages: List[I2CMessage]):
        """Transfer `messages` to the specified I2C `address`. Modifies the
        `messages` array with the results of any read transactions.
        Args:
            address (int): I2C address.
            messages (list): list of I2C.Message messages.
        Raises:
            I2CError: if an I/O or OS error occurs.
            TypeError: if `messages` type is not list.
            ValueError: if `messages` length is zero, or if message data is not valid bytes.
        """
        if not isinstance(messages, list):
            raise TypeError("Invalid messages type, should be list of I2C.Message.")
        if len(messages) == 0:
            raise ValueError("Invalid messages data, should be non-zero length.")

        # Convert I2C.Message messages to _CI2CMessage messages
        cmessages = (_CI2CMessage * len(messages))()
        for i, message in enumerate(messages):
            # Convert I2C.Message data to bytes
            if isinstance(message.data, bytes):
                data = message.data
            elif isinstance(message.data, bytearray):
                data = bytes(message.data)
            elif isinstance(message.data, list):
                data = bytes(bytearray(messages[i].data))
            else:
                raise ValueError('Invalid data type')

            cmessages[i].addr = address
            cmessages[i].flags = message.flags | (I2C._I2C_M_RD if message.read else 0)
            cmessages[i].len = len(data)
            cmessages[i].buf = ctypes.cast(ctypes.create_string_buffer(data, len(data)), ctypes.POINTER(ctypes.c_ubyte))

        # Prepare transfer structure
        i2c_xfer = _CI2CIocTransfer()
        i2c_xfer.nmsgs = len(cmessages)
        i2c_xfer.msgs = cmessages

        # Transfer
        try:
            fcntl.ioctl(self._bus, I2C._I2C_IOC_RDWR, i2c_xfer, False)
        except (OSError, IOError) as e:
            raise I2CError(e.errno, "I2C transfer: " + e.strerror) from e

        # Update any read I2C.Message messages
        for i, message in enumerate(messages):
            if message.read:
                data = [cmessages[i].buf[j] for j in range(cmessages[i].len)]
                # Convert read data to type used in I2C.Message messages
                if isinstance(messages[i].data, list):
                    message.data = data
                elif isinstance(messages[i].data, bytearray):
                    message.data = bytearray(data)
                elif isinstance(messages[i].data, bytes):
                    message.data = bytes(bytearray(data))

    def detect(self, first: int = 0x03, last: int = 0x77, data: Optional[bytes] = None, length: int = 1) -> List[int]:
        """
        Scans bus looking for devices.

        Args:
            first (int, optional): first address (inclusive). Defaults to 0x03
            last  (int, optional): last address (inclusive). Defaults to 0x77
            data (bytes, optional): Attempt to write given data. Defaults to None
            length (int, optional): Number of bytes to read. Defaults to 1

        Returns:
            List[int]: List of device base-10 addresses that responded.
        """
        addresses = []
        for i in range(first, last+1):
            try:
                self.set_address(i)
                if data is not None:
                    self.read_write(data=data, length=length)
                else:
                    self.read(length=length)
                addresses.append(i)
            except Exception:
                pass
        return addresses
