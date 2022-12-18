# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from abc import ABCMeta, abstractmethod
from typing import Any, Generator, List
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.protocol.protocol import ProtocolType
from XSocket.util import OPCode

__all__ = [
    "IHandle"
]


class IHandle(metaclass=ABCMeta):
    """
    Provides client connections for network services.
    """

    @property
    @abstractmethod
    def local_address(self) -> AddressInfo:
        """
        Gets the local endpoint.

        :return: AddressInfo
        """

    @property
    @abstractmethod
    def remote_address(self) -> AddressInfo:
        """
        Gets the remote endpoint.

        :return: AddressInfo
        """

    @property
    @abstractmethod
    def address_family(self) -> AddressFamily:
        """
        Gets the address family of the Socket.

        :return: AddressFamily
        """

    @property
    @abstractmethod
    def protocol_type(self) -> ProtocolType:
        """
        Gets the protocol type of the Handle.

        :return: ProtocolType
        """

    @property
    @abstractmethod
    def closed(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Handle has been closed.

        :return: bool
        """

    @abstractmethod
    def pack(self, data: bytearray, opcode: OPCode
             ) -> Generator[bytearray, None, None]:
        """
        Generates a packet to be transmitted.

        :param data: Data to send
        :param opcode: Operation code
        :return: Packet generator
        """

    @abstractmethod
    def unpack(self, packets: List[bytearray], *args, **kwargs
               ) -> Generator[Any, None, None]:
        """
        Read the header of the received packet and get the data.

        :param packets: Received packet
        :return: See docstring
        """

    @abstractmethod
    async def send(self, *args, **kwargs):
        """
        Sends data to a connected Socket.
        """

    @abstractmethod
    async def receive(self) -> bytearray:
        """
        Receives data from a bound Socket.

        :return: Received data
        """

    @abstractmethod
    async def close(self):
        """
        Closes the Socket connection.
        """
