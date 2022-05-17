import typing

from .. import ProtocolType
from ...base.address import AddressFamily, AddressInfo
from ...base.handle import *


class XTCPHandle(Handle):
    def __init__(self) -> None:
        pass

    @property
    def available(self) -> bool:
        pass

    @property
    def connected(self) -> bool:
        pass

    @property
    def closed(self) -> bool:
        pass

    @property
    def local_address(self) -> AddressInfo:
        pass

    @property
    def remote_address(self) -> AddressInfo:
        pass

    @property
    def address_family(self) -> AddressFamily:
        pass

    @property
    def protocol_type(self) -> ProtocolType:
        pass

    async def send(self, *args, **kwargs) -> None:
        pass

    async def receive(self) -> typing.Any:
        pass

    def close(self) -> None:
        pass
