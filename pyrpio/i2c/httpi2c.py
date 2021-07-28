""" I2C via HTTP Rest API """
import base64
import dataclasses
from typing import List, Optional
import httpx  # pylint: disable=import-error
from pyrpio.i2c.types import I2CBase, I2CMessage


class HttpI2C(I2CBase):
    ''' HTTP device based I2C. '''

    client: httpx.Client

    def __init__(self, base_url: str, path: str = 'i2c-1'):
        '''
        Create an i2c bus with 7-bit addressing

        Args:
            base_url: url path of Rest API
            path: path of i2c bus. Defaults to i2c-1.
        '''
        self.base_url = base_url
        self.path: str = path
        self._address = 0x0

    @property
    def bus_path(self) -> str:
        ''' Bus path url prefix. '''
        return f'/i2c/bus/{self.path}'

    def open(self):
        self.client = httpx.Client(base_url=self.base_url)
        r = self.client.post(f'{self.bus_path}/open')
        r.raise_for_status()

    def close(self):
        if self.client and not self.client.is_closed:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass

    def __del__(self):
        self.close()

    def set_address(self, address: int):
        # if address != self._address:
        r = self.client.post(f'{self.bus_path}/address/{address}')
        r.raise_for_status()
        self._address = address

    def read(self, length: int = 1) -> bytes:
        r = self.client.post(f'{self.bus_path}/read/{length}')
        r.raise_for_status()
        return base64.b64decode(r.content)

    def write(self, data: bytes):
        r = self.client.post(f'{self.bus_path}/write', params=dict(data=str(base64.b64encode(data), 'utf-8')))
        r.raise_for_status()

    def read_write(self, data: bytes, length: int = 1) -> bytes:
        r = self.client.post(
            f'{self.bus_path}/write_read/{length}', params=dict(data=str(base64.b64encode(data), 'utf-8'))
        )
        r.raise_for_status()
        return base64.b64decode(r.content)

    def transfer(self, address: int, messages: List[I2CMessage]):
        mdicts = [dataclasses.asdict(m) for m in messages]
        r = self.client.post(f'{self.bus_path}/transfer/{address}', data=mdicts)
        r.raise_for_status()

    def detect(self, first: int = 0x03, last: int = 0x77, data: Optional[bytes] = None, length: int = 1) -> List[int]:
        r = self.client.post(f'{self.bus_path}/detect')
        r.raise_for_status()
        addresses = list(filter(lambda a: first <= a <= last, r.json()))
        return addresses
