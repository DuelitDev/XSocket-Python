# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from abc import ABCMeta, abstractmethod
from asyncio import AbstractEventLoop
from typing import Any, Generator, List, Optional
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.core.socket import Socket
from XSocket.protocol.protocol import ProtocolType

__all__ = [
    "Handle"
]


class Handle(metaclass=ABCMeta):
    """
    Provides client connections for network services.
    """
    def __init__(self, *args, **kwargs):
        self._socket: Optional[Socket] = None
        self._address: Optional[AddressInfo] = None
        self._event_loop: Optional[AbstractEventLoop] = None
        self._closed: bool = False

    @property
    def closed(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Handle has been closed.

        :return: bool
        """
        return self._closed

    @property
    @abstractmethod
    def local_address(self) -> AddressInfo:
        """
        Gets the local endpoint.

        :return: AddressInfo
        """
        pass

    @property
    @abstractmethod
    def remote_address(self) -> AddressInfo:
        """
        Gets the remote endpoint.

        :return: AddressInfo
        """
        pass

    @property
    @abstractmethod
    def address_family(self) -> AddressFamily:
        """
        Gets the address family of the Socket.

        :return: AddressFamily
        """
        pass

    @property
    @abstractmethod
    def protocol_type(self) -> ProtocolType:
        """
        Gets the protocol type of the Handle.

        :return: ProtocolType
        """
        pass

    @staticmethod
    @abstractmethod
    def pack(data: bytearray,
             *args, **kwargs) -> Generator[bytearray, None, None]:
        """
        Generates a packet to be transmitted.

        :param data: Data to send
        :return: Packet generator
        """
        pass

    @staticmethod
    @abstractmethod
    def unpack(packets: List[bytearray],
               *args, **kwargs) -> Generator[Any, None, None]:
        """
        Read the header of the received packet and get the data.

        :param packets: Received packet
        :return: See docstring
        """
        pass

    @abstractmethod
    async def send(self, *args, **kwargs):
        """
        Sends data to a connected Socket.
        """
        pass

    @abstractmethod
    async def receive(self) -> bytearray:
        """
        Receives data from a bound Socket.

        :return: Received data
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Closes the Socket connection.
        """
        pass
