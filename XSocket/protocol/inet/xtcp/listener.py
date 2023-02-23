from asyncio import AbstractEventLoop, get_running_loop
from typing import Optional, Tuple, Union
from select import select
from socket import SOCK_STREAM, SOL_SOCKET, SO_LINGER, SO_REUSEADDR, socket
from struct import pack
from XSocket.core.listener import IListener
from XSocket.core.net import AddressFamily
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

    def __init__(self, address: Union[IPAddressInfo, Tuple[str, int]]):
        """
        Listens for connections from TCP network clients.

        :param address: Local address
        """
        super().__init__()
        self._socket: Optional[socket] = None
        self._event_loop: Optional[AbstractEventLoop] = None
        if isinstance(address, tuple):
            address = IPAddressInfo(address[0], address[1])
        self._address: IPAddressInfo = address
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

    @property
    def pending(self) -> bool:
        """
        Determines if there are pending connection requests.

        :return: bool
        """
        return bool(select([self._socket], [], [], 0)[0])

    def run(self):
        """
        Starts listening for incoming connection requests.
        """
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
        self._socket.close()
        self._running = False
        self._closed = True

    async def connect(self) -> XTCPHandle:
        """
        Establishes a connection to a remote host.

        :return: XTCPHandle
        """
        self._event_loop = get_running_loop()
        sock = socket(self.address_family, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_LINGER, pack("ii", 1, 0))
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setblocking(False)
        await self._event_loop.sock_connect(sock, (*self._address,))
        return XTCPHandle(XTCPSocket(sock))

    async def accept(self) -> XTCPHandle:
        """
        Creates a new XTCPHandle for a newly created connection.

        :return: XTCPHandle
        """
        sock, addr = await self._event_loop.sock_accept(self._socket)
        sock.setblocking(False)
        return XTCPHandle(XTCPSocket(sock))
