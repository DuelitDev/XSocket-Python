import typing
import asyncio
from abc import ABCMeta, abstractmethod
from enum import IntEnum


__all__ = ["Handle"]


class Handle(metaclass=ABCMeta):
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
    def is_running(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_closed(self) -> bool:
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


class IListener(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @property
    @abstractmethod
    def local_address(self) -> AddressInfo:
        pass

    @property
    @abstractmethod
    def is_closed(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    async def serve(self) -> None:

    @abstractmethod
    async def connect(self) -> IHandle:

    @abstractmethod
    async def accept(self) -> IHandle:

    @abstractmethod
    def close(self) -> None:


class DataType(IntEnum):
    Text = 0b00000001
    Binary = 0b00000010
    ConnectionClose = 0b00001000

