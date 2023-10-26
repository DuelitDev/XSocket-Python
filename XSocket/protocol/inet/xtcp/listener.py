from asyncio import AbstractEventLoop, get_running_loop
from select import select
from socket import SOCK_STREAM, SOL_SOCKET, SO_LINGER, SO_REUSEADDR, socket
from struct import pack
from XSocket.core.listener import IListener
from XSocket.core.net import AddressFamily
from XSocket.exception import ListenerClosedException
from XSocket.protocol.protocol import ProtocolType
from XSocket.protocol.inet.net import IPAddressInfo
from XSocket.protocol.inet.xtcp.handle import XTCPHandle
from XSocket.protocol.inet.xtcp.socket import XTCPSocket

__all__ = [
    "XTCPListener"
]


class XTCPListener(IListener):
    """
    Listens for connections from TCP network clients.
    """

    def __init__(self, address: IPAddressInfo | tuple[str, int]):
        """
        Listens for connections from TCP network clients.

        :param address: Local address
        """
        if isinstance(address, tuple):
            address = IPAddressInfo(address[0], address[1])
        self._address: IPAddressInfo = address
        self._socket: socket | None = None
        self._event_loop: AbstractEventLoop | None = None
        self._running: bool = False
        self._closed: bool = False

    @property
    def running(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Listener is running.

        :return: bool
        """
        return self._running

    @property
    def closed(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Listener has been closed.

        :return: bool
        """
        return self._closed

    @property
    def pending(self) -> bool:
        """
        Determines if there are pending connection requests.

        :return: bool
        """
        if not self._running or self._closed:
            raise ListenerClosedException()
        return bool(select([self._socket], [], [], 0)[0])

    @property
    def local_address(self) -> IPAddressInfo:
        """
        Gets the local endpoint.

        :return: AddressInfo
        """
        return self._address

    @property
    def address_family(self) -> AddressFamily:
        """
        Gets the address family of the Socket.

        :return: AddressFamily
        """
        return self._address.address_family

    @property
    def protocol_type(self) -> ProtocolType:
        """
        Gets the protocol type of the Listener.

        :return: ProtocolType
        """
        return ProtocolType.Xtcp

    def run(self):
        """
        Starts listening for incoming connection requests.
        """
        if self._running or self._closed:
            return
        self._event_loop = get_running_loop()
        self._socket = socket(self.address_family, SOCK_STREAM)
        self._socket.setsockopt(SOL_SOCKET, SO_LINGER, pack("ii", 1, 0))
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._socket.setblocking(False)
        self._socket.bind((*self._address,))
        self._socket.listen()
        self._running = True

    def close(self):
        """
        Closes the listener.
        """
        if not self._running or self._closed:
            return
        if self._socket:
            self._socket.close()
        self._running = False
        self._closed = True

    async def connect(self) -> XTCPHandle:
        """
        Establishes a connection to a remote host.

        :return: XTCPHandle
        """
        return await XTCPHandle.create(self._address)

    async def accept(self) -> XTCPHandle:
        """
        Creates a new XTCPHandle for a newly created connection.

        :return: XTCPHandle
        """
        if not self._running or self._closed:
            raise ListenerClosedException()
        sock, addr = await self._event_loop.sock_accept(self._socket)
        sock.setblocking(False)
        return XTCPHandle(XTCPSocket(sock))
