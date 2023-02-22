from abc import ABCMeta, abstractmethod
from typing import Generator, List, Union
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
    def unpack(self, packets: List[bytearray]) -> Generator[int, None, None]:
        """
        Read the header of the received packet and get the data.

        :param packets: Received packet
        :return: See docstring
        """

    @abstractmethod
    async def send(self, data: Union[bytes, bytearray],
                   opcode: OPCode = OPCode.Data):
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
