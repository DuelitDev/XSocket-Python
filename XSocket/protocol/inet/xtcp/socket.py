from asyncio import AbstractEventLoop, get_running_loop
from socket import SOCK_STREAM, SOL_SOCKET, SO_LINGER, SO_REUSEADDR, socket
from struct import pack
from XSocket.core.socket import ISocket
from XSocket.exception import SocketClosedException
from XSocket.protocol.inet.net import IPAddressInfo

__all__ = [
    "XTCPSocket"
]


class XTCPSocket(ISocket):
    """
    Implements XTCP sockets interface.
    """

    def __init__(self, sock: socket):
        self._socket: socket = sock
        self._local_address: IPAddressInfo = IPAddressInfo(*sock.getsockname())
        self._remote_address: IPAddressInfo = IPAddressInfo(*sock.getpeername())
        self._event_loop: AbstractEventLoop = get_running_loop()
        self._closed: bool = False

    @staticmethod
    async def create(address: IPAddressInfo) -> "XTCPSocket":
        """
        Create a new XTCPSocket with the address info.

        :param address: IPAddressInfo
        :return: XTCPSocket
        """
        loop = get_running_loop()
        sock = socket(address.address_family, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_LINGER, pack("ii", 1, 0))
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setblocking(False)
        await loop.sock_connect(sock, (*address,))
        return XTCPSocket(sock)

    @property
    def closed(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Socket has been closed.

        :return: bool
        """
        return self._closed

    @property
    def get_raw_socket(self) -> socket:
        """
        Get a low-level socket.

        :return: Low-level socket
        """
        if self._closed:
            raise SocketClosedException()
        return self._socket

    @property
    def local_address(self) -> IPAddressInfo:
        """
        Gets the local IP address info.

        :return: IPAddressInfo
        """
        return self._local_address

    @property
    def remote_address(self) -> IPAddressInfo:
        """
        Gets the local IP address info.

        :return: IPAddressInfo
        """
        return self._remote_address

    def close(self):
        """
        Close the socket.
        """
        if self._closed:
            return
        self._socket.close()
        self._closed = True

    async def send(self, data: bytearray):
        """
        Sends data to a connected Socket.

        :param data: Data to send
        """
        if self._closed:
            raise SocketClosedException()
        return await self._event_loop.sock_sendall(self._socket, data)

    async def receive(self, length: int, exactly: bool = False) -> bytearray:
        """
        Receives data from a bound Socket.

        :param length: The number of bytes to receive
        :param exactly: weather to read exactly
        :return: Received data
        """
        if self._closed:
            raise SocketClosedException()
        buffer = bytearray()
        while len(buffer) != length:
            buffer += await self._event_loop.sock_recv(
                self._socket, length - len(buffer))
            if not exactly:
                break
        return buffer
