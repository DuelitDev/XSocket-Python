# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from abc import ABCMeta, abstractmethod
from typing import Any
from XSocket.core.net import AddressInfo

__all__ = [
    "Socket"
]


class Socket(metaclass=ABCMeta):
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
    def get_raw_socket(self) -> Any:
        pass

    @abstractmethod
    async def send(self, data: bytearray):
        pass

    @abstractmethod
    async def receive(self, length: int, exactly: bool = False) -> bytearray:
        pass

    @abstractmethod
    def close(self):
        pass
