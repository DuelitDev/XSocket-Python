from abc import ABCMeta, abstractmethod
from XSocket.core.handle import IHandle
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.protocol.protocol import ProtocolType

__all__ = [
    "IListener"
]


class IListener(metaclass=ABCMeta):
    """
    Listens for connections from network clients.
    """

    @property
    @abstractmethod
    def running(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Listener is running.

        :return: bool
        """

    @property
    @abstractmethod
    def closed(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Listener has been closed.

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
    def address_family(self) -> AddressFamily:
        """
        Gets the address family of the Socket.

        :return: AddressFamily
        """

    @property
    @abstractmethod
    def protocol_type(self) -> ProtocolType:
        """
        Gets the protocol type of the Listener.

        :return: ProtocolType
        """

    @property
    @abstractmethod
    def pending(self) -> bool:
        """
        Determines if there are pending connection requests.

        :return: bool
        """

    @abstractmethod
    def run(self):
        """
        Starts listening for incoming connection requests.
        """

    @abstractmethod
    def close(self):
        """
        Closes the listener.
        """

    @abstractmethod
    async def connect(self) -> IHandle:
        """
        Establishes a connection to a remote host.

        :return: Handle
        """

    @abstractmethod
    async def accept(self) -> IHandle:
        """
        Creates a new Handle for a newly created connection.

        :return: Handle
        """
