""" SPI Types """
from abc import ABC, abstractmethod
from typing import Union, List, Optional

ByteLike = Union[bytes, bytearray, List[int]]

class SPIError(IOError):
    """Base class for SPI errors."""
    ...

class SPIBase(ABC):
    """ Abstract base class for SPI. """
    def open(self):
        """Open SPI interface
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    def close(self):
        """Close interface
        """
        raise NotImplementedError()

    @property
    def fd(self) -> str:
        """Get SPI file-like descriptor
        Returns:
            str: Descriptor
        """
        raise NotImplementedError()

    @property
    def devpath(self) -> str:
        """Path to SPI interface.
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_mode(self):
        ...

    @abstractmethod
    def _set_mode(self, mode: int):
        ...

    mode = property(_get_mode, _set_mode)
    """Get or set the SPI mode. Can be 0, 1, 2, 3.

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `mode` type is not int.
        ValueError: if `mode` value is invalid.

    :type: int
    """

    @abstractmethod
    def _get_max_speed(self):
        ...

    @abstractmethod
    def _set_max_speed(self, max_speed: Union[int, float]):
        ...

    max_speed = property(_get_max_speed, _set_max_speed)
    """Get or set the maximum speed in Hertz.

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `max_speed` type is not int or float.

    :type: int, float
    """

    @abstractmethod
    def _get_bit_order(self):
        ...

    @abstractmethod
    def _set_bit_order(self, bit_order: str):
        ...

    bit_order = property(_get_bit_order, _set_bit_order)
    """Get or set the SPI bit order. Can be "msb" or "lsb".

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `bit_order` type is not str.
        ValueError: if `bit_order` value is invalid.

    :type: str
    """

    @abstractmethod
    def _get_extra_flags(self):
        ...

    @abstractmethod
    def _set_extra_flags(self, extra_flags: int):
        ...

    extra_flags = property(_get_extra_flags, _set_extra_flags)
    """Get or set the spidev extra flags. Extra flags are bitwise-ORed with the SPI mode.

    Raises:
        SPIError: if an I/O or OS error occurs.
        TypeError: if `extra_flags` type is not int.
        ValueError: if `extra_flags` value is invalid.

    :type: int
    """
