from abc import ABCMeta, abstractmethod
from typing import Any, Generator
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.core.socket import ISocket
from XSocket.protocol.protocol import ProtocolType
from XSocket.util import OPCode

__all__ = [
    "IHandle"
]


class IHandle(metaclass=ABCMeta):
    """
    Provides client connections for network services.
    """

    @staticmethod
    @abstractmethod
    async def create(address: AddressInfo) -> "IHandle":
        """
        Create a new Handle with the address info.

        :param address: AddressInfo
        :return: IHandle
        """

    @property
    @abstractmethod
    def closed(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Handle has been closed.

        :return: bool
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

    @abstractmethod
    async def close(self):
        """
        Closes the Socket connection.
        """

    @staticmethod
    @abstractmethod
    def pack(data: bytearray, opcode: OPCode) -> Generator[bytearray, Any, Any]:
        """
        Generates a packet to be transmitted.

        :param data: Data to send
        :param opcode: Operation code
        :return: Packet generator
        """

    @staticmethod
    @abstractmethod
    def unpack(packets: list[bytearray]) -> Generator[int, Any, Any]:
        """
        Read the header of the received packet and get the data.

        :param packets: Received packet
        :return: See docstring
        """

    @abstractmethod
    async def send(self, data: bytes | bytearray, opcode: OPCode):
        """
        Sends data to a connected Socket.

        :param data: Data to send
        :param opcode: Operation Code
        """

    @abstractmethod
    async def receive(self) -> bytearray:
        """
        Receives data from a bound Socket.

        :return: Received data
        """
