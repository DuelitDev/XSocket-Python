import typing
import socket
import asyncio
from abc import ABCMeta, abstractmethod
from address import *
from ..protocol import ProtocolType


__all__ = ["Handle"]


class Handle(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        self._socket: socket.socket
        self._event_loop: asyncio.BaseEventLoop
        self._closed: bool = False

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    @abstractmethod
    def local_address(self) -> AddressInfo:
        pass

    @property
    @abstractmethod
    def remote_address(self) -> AddressInfo:
        pass

    @property
    @abstractmethod
    def address_family(self) -> AddressFamily:
        pass

    @property
    @abstractmethod
    def protocol_type(self) -> ProtocolType:
        pass

    @staticmethod
    @abstractmethod
    def pack(data: typing.Union[bytes, bytearray],
             *args, **kwargs) -> typing.Generator[bytearray]:
        pass

    @staticmethod
    @abstractmethod
    def unpack(packets: typing.List[typing.Union[bytes, bytearray]],
               *args, **kwargs) -> typing.Generator[bytearray, bool]:
        pass

    @abstractmethod
    async def send(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    async def receive(self) -> typing.Any:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
