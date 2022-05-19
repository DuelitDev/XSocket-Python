import typing
import socket
from .. import ProtocolType
from ...base.address import *
from ...base.handle import *


__all__ = ["XTCPHandle"]


class XTCPHandle(Handle):
    def __init__(self, socket_: socket.socket) -> None:
        super().__init__()
        self._socket = socket_

    @property
    def local_address(self) -> AddressInfo:
        address, port = self._socket.getsockname()
        return IPAddressInfo(address, port)

    @property
    def remote_address(self) -> AddressInfo:
        address, port = self._socket.getpeername()
        return IPAddressInfo(address, port)

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
