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
        self._protocol_type: ProtocolType
        self._event_loop: asyncio.BaseEventLoop
        self._available: bool = False
        self._connected: bool = False
        self._closed: bool = False

    @property
    @abstractmethod
    def available(self) -> bool:
        pass

    @property
    @abstractmethod
    def connected(self) -> bool:
        pass

    @property
    @abstractmethod
    def closed(self) -> bool:
        pass

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

    @abstractmethod
    async def send(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    async def receive(self) -> typing.Any:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
