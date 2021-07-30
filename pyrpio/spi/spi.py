''' SPI interface.
Adapted from python-periphery (https://github.com/vsergeev/python-periphery/blob/master/periphery/spi.py)
Modified to support 3-wire mode (MOSI & MISO tied)
'''
import os
from typing import Optional
import fcntl
import array
import ctypes
from .types import SPIBase, SPIError, ByteLike


class _CSpiIocTransfer(ctypes.Structure):
    # pylint: disable=too-few-public-methods
    _fields_ = [
        ('tx_buf', ctypes.c_ulonglong),
        ('rx_buf', ctypes.c_ulonglong),
        ('len', ctypes.c_uint),
        ('speed_hz', ctypes.c_uint),
        ('delay_usecs', ctypes.c_ushort),
        ('bits_per_word', ctypes.c_ubyte),
        ('cs_change', ctypes.c_ubyte),
        ('tx_nbits', ctypes.c_ubyte),
        ('rx_nbits', ctypes.c_ubyte),
        ('pad', ctypes.c_ushort),
    ]


class SPI(SPIBase):
    ''' SPI class interface. '''
    SPI_3WIRE = 0x10
    # Constants scraped from <linux/spi/spidev.h>
    _SPI_CPHA = 0x1
    _SPI_CPOL = 0x2
    _SPI_LSB_FIRST = 0x8
    _SPI_IOC_WR_MODE = 0x40016b01
    _SPI_IOC_RD_MODE = 0x80016b01
    _SPI_IOC_WR_MAX_SPEED_HZ = 0x40046b04
    _SPI_IOC_RD_MAX_SPEED_HZ = 0x80046b04
    _SPI_IOC_WR_BITS_PER_WORD = 0x40016b03
    _SPI_IOC_RD_BITS_PER_WORD = 0x80016b03
    _SPI_IOC_MESSAGE_1 = 0x40206b00

    def __init__(self, devpath, mode, max_speed, bit_order="msb", bits_per_word=8, extra_flags=0):
        """Instantiate a SPI object and open the spidev device at the specified
        path with the specified SPI mode, max speed in hertz, and the defaults
        of "msb" bit order and 8 bits per word.

        Args:
            devpath (str): spidev device path.
            mode (int): SPI mode, can be 0, 1, 2, 3.
            max_speed (int, float): maximum speed in Hertz.
            bit_order (str): bit order, can be "msb" or "lsb".
            bits_per_word (int): bits per word.
            extra_flags (int): extra spidev flags to be bitwise-ORed with the SPI mode.

        Returns:
            SPI: SPI object.

        Raises:
            SPIError: if an I/O or OS error occurs.
            TypeError: if `devpath`, `mode`, `max_speed`, `bit_order`, `bits_per_word`, or `extra_flags` types are invalid.
            ValueError: if `mode`, `bit_order`, `bits_per_word`, or `extra_flags` values are invalid.

        """
        self._fd: Optional[int] = None
        self._devpath: str = ''
        self._open(devpath, mode, max_speed, bit_order, bits_per_word, extra_flags)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        self.close()

    def open(self):
        pass

    def _open(self, devpath, mode, max_speed, bit_order, bits_per_word, extra_flags):
        if not isinstance(devpath, str):
            raise TypeError("Invalid devpath type, should be string.")
        if not isinstance(mode, int):
            raise TypeError("Invalid mode type, should be integer.")
        if not isinstance(max_speed, (int, float)):
            raise TypeError("Invalid max_speed type, should be integer or float.")
        if not isinstance(bit_order, str):
            raise TypeError("Invalid bit_order type, should be string.")
        if not isinstance(bits_per_word, int):
            raise TypeError("Invalid bits_per_word type, should be integer.")
        if not isinstance(extra_flags, int):
            raise TypeError("Invalid extra_flags type, should be integer.")

        if mode not in [0, 1, 2, 3]:
            raise ValueError("Invalid mode, can be 0, 1, 2, 3.")
        if bit_order.lower() not in ["msb", "lsb"]:
            raise ValueError("Invalid bit_order, can be \"msb\" or \"lsb\".")
        if bits_per_word < 0 or bits_per_word > 255:
            raise ValueError("Invalid bits_per_word, must be 0-255.")
        if extra_flags < 0 or extra_flags > 255:
            raise ValueError("Invalid extra_flags, must be 0-255.")

        # Open spidev
        try:
            self._fd = os.open(devpath, os.O_RDWR)
        except OSError as e:
            raise SPIError(e.errno, "Opening SPI device: " + e.strerror) from e

        self._devpath = devpath

        bit_order = bit_order.lower()

        # Set mode, bit order, extra flags
        buf = array.array("B", [mode | (SPI._SPI_LSB_FIRST if bit_order == "lsb" else 0) | extra_flags])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_MODE, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Setting SPI mode: " + e.strerror) from e

        # Set max speed
        buf = array.array("I", [int(max_speed)])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_MAX_SPEED_HZ, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Setting SPI max speed: " + e.strerror) from e

        # Set bits per word
        buf = array.array("B", [bits_per_word])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_BITS_PER_WORD, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Setting SPI bits per word: " + e.strerror) from e

    # Methods
    def transfer(self,
            tx_data: Optional[ByteLike] = None,
            rx_data: Optional[ByteLike] = None,
            cs_change: bool = True
        ) -> ByteLike:
        """Shift out `data` and return shifted in data.
        Args:
            tx_data (bytes, bytearray, list): a byte array or list of 8-bit integers to shift out.
            rx_data (bytes, bytearray, list): a byte array or list of 8-bit integers to shift out.
            cs_change (bool): assert chip select
        Returns:
            bytes, bytearray, list: data shifted in.

        Raises:
            SPIError: if an I/O or OS error occurs.
            TypeError: if `data` type is invalid.
            ValueError: if data is not valid bytes.

        """
        if self._fd is None:
            raise SPIError('SPI bus is not open')
        if tx_data and not isinstance(tx_data, (bytes, bytearray, list)):
            raise TypeError("Invalid data type, should be bytes, bytearray, or list.")
        if rx_data and not isinstance(rx_data, (bytes, bytearray, list)):
            raise TypeError("Invalid data type, should be bytes, bytearray, or list.")
        if tx_data and rx_data and len(tx_data) != len(rx_data):
            raise ValueError("tx_data and rx_data must have same length if both supplied")

        # Create mutable array
        tx_buf, rx_buf = None, None
        tx_buf_addr, rx_buf_addr, buf_len = 0, 0, 0
        try:
            if tx_data:
                tx_buf = array.array('B', tx_data)
                tx_buf_addr, buf_len = tx_buf.buffer_info()
            if rx_data:
                rx_buf = array.array('B', rx_data)
                rx_buf_addr, buf_len = rx_buf.buffer_info()
        except OverflowError as err:
            raise ValueError("Invalid data bytes.") from err

        # Prepare transfer structure
        spi_xfer = _CSpiIocTransfer()
        spi_xfer.tx_buf = tx_buf_addr
        spi_xfer.rx_buf = rx_buf_addr
        spi_xfer.len = buf_len
        spi_xfer.cs_change = 1 if cs_change else 0

        # Transfer
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_MESSAGE_1, spi_xfer)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "SPI transfer: " + e.strerror) from e

        # Return shifted out data with the same type as shifted in data
        if rx_buf and isinstance(rx_data, bytes):
            return bytes(bytearray(rx_buf))
        if rx_buf and isinstance(tx_data, bytearray):
            return bytearray(rx_buf)
        if rx_buf and isinstance(tx_data, list):
            return rx_buf.tolist()
        return tx_data or [0]

    def close(self):
        """Close the spidev SPI device.

        Raises:
            SPIError: if an I/O or OS error occurs.

        """
        if self._fd is None:
            return

        try:
            os.close(self._fd)
        except OSError as e:
            raise SPIError(e.errno, "Closing SPI device: " + e.strerror) from e

        self._fd = None

    # Immutable properties

    @property
    def fd(self):
        """Get the file descriptor of the underlying spidev device.

        :type: int
        """
        return self._fd

    @property
    def devpath(self):
        """Get the device path of the underlying spidev device.

        :type: str
        """
        return self._devpath

    # Mutable properties
    def _get_mode(self):
        buf = array.array('B', [0])

        # Get mode
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_MODE, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Getting SPI mode: " + e.strerror) from e

        return buf[0] & 0x3

    def _set_mode(self, mode):
        if not isinstance(mode, int):
            raise TypeError("Invalid mode type, should be integer.")
        if mode not in [0, 1, 2, 3]:
            raise ValueError("Invalid mode, can be 0, 1, 2, 3.")

        # Read-modify-write mode, because the mode contains bits for other settings

        # Get mode
        buf = array.array('B', [0])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_MODE, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Getting SPI mode: " + e.strerror) from e

        buf[0] = (buf[0] & ~(SPI._SPI_CPOL | SPI._SPI_CPHA)) | mode

        # Set mode
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_MODE, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Setting SPI mode: " + e.strerror) from e

    mode = property(_get_mode, _set_mode)
    """Get or set the SPI mode. Can be 0, 1, 2, 3.

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `mode` type is not int.
        ValueError: if `mode` value is invalid.

    :type: int
    """

    def _get_max_speed(self):
        # Get max speed
        buf = array.array('I', [0])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_MAX_SPEED_HZ, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(
                e.errno, "Getting SPI max speed: " + e.strerror) from e

        return buf[0]

    def _set_max_speed(self, max_speed):
        if not isinstance(max_speed, (int, float)):
            raise TypeError("Invalid max_speed type, should be integer or float.")

        # Set max speed
        buf = array.array('I', [int(max_speed)])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_MAX_SPEED_HZ, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(
                e.errno, "Setting SPI max speed: " + e.strerror) from e

    max_speed = property(_get_max_speed, _set_max_speed)
    """Get or set the maximum speed in Hertz.

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `max_speed` type is not int or float.

    :type: int, float
    """

    def _get_bit_order(self):
        # Get mode
        buf = array.array('B', [0])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_MODE, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Getting SPI mode: " + e.strerror) from e

        if (buf[0] & SPI._SPI_LSB_FIRST) > 0:
            return "lsb"

        return "msb"

    def _set_bit_order(self, bit_order):
        if not isinstance(bit_order, str):
            raise TypeError("Invalid bit_order type, should be string.")
        if bit_order.lower() not in ["msb", "lsb"]:
            raise ValueError("Invalid bit_order, can be \"msb\" or \"lsb\".")

        # Read-modify-write mode, because the mode contains bits for other settings

        # Get mode
        buf = array.array('B', [0])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_MODE, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Getting SPI mode: " + e.strerror) from e

        bit_order = bit_order.lower()
        buf[0] = (buf[0] & ~SPI._SPI_LSB_FIRST) | (SPI._SPI_LSB_FIRST if bit_order == "lsb" else 0)

        # Set mode
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_MODE, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Setting SPI mode: " + e.strerror) from e

    bit_order = property(_get_bit_order, _set_bit_order)
    """Get or set the SPI bit order. Can be "msb" or "lsb".

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `bit_order` type is not str.
        ValueError: if `bit_order` value is invalid.

    :type: str
    """

    def _get_bits_per_word(self):
        # Get bits per word
        buf = array.array('B', [0])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_BITS_PER_WORD, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Getting SPI bits per word: " + e.strerror) from e

        return buf[0]

    def _set_bits_per_word(self, bits_per_word):
        if not isinstance(bits_per_word, int):
            raise TypeError("Invalid bits_per_word type, should be integer.")
        if bits_per_word < 0 or bits_per_word > 255:
            raise ValueError("Invalid bits_per_word, must be 0-255.")

        # Set bits per word
        buf = array.array('B', [bits_per_word])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_BITS_PER_WORD, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Setting SPI bits per word: " + e.strerror) from e

    bits_per_word = property(_get_bits_per_word, _set_bits_per_word)
    """Get or set the SPI bits per word.

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `bits_per_word` type is not int.
        ValueError: if `bits_per_word` value is invalid.

    :type: int
    """

    def _get_extra_flags(self):
        # Get mode
        buf = array.array('B', [0])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_MODE, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Getting SPI mode: " + e.strerror) from e

        return buf[0] & ~(SPI._SPI_LSB_FIRST | SPI._SPI_CPHA | SPI._SPI_CPOL)

    def _set_extra_flags(self, extra_flags):
        if not isinstance(extra_flags, int):
            raise TypeError("Invalid extra_flags type, should be integer.")
        if extra_flags < 0 or extra_flags > 255:
            raise ValueError("Invalid extra_flags, must be 0-255.")

        # Read-modify-write mode, because the mode contains bits for other settings

        # Get mode
        buf = array.array('B', [0])
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_RD_MODE, buf, True)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Getting SPI mode: " + e.strerror) from e

        buf[0] = (buf[0] & (SPI._SPI_LSB_FIRST | SPI._SPI_CPHA | SPI._SPI_CPOL)) | extra_flags

        # Set mode
        try:
            fcntl.ioctl(self._fd, SPI._SPI_IOC_WR_MODE, buf, False)
        except (OSError, IOError) as e:
            raise SPIError(e.errno, "Setting SPI mode: " + e.strerror) from e

    extra_flags = property(_get_extra_flags, _set_extra_flags)
    """Get or set the spidev extra flags. Extra flags are bitwise-ORed with the SPI mode.

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `extra_flags` type is not int.
        ValueError: if `extra_flags` value is invalid.

    :type: int
    """

    # String representation

    def __str__(self):
        return "SPI (device={:s}, fd={:d}, mode={:d}, max_speed={:d}, bit_order={:s}, bits_per_word={:d}, extra_flags=0x{:02x})" \
            .format(self.devpath, self.fd, self.mode, self.max_speed, self.bit_order, self.bits_per_word, self.extra_flags)
