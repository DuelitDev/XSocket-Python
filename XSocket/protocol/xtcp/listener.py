# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from asyncio import get_running_loop
from typing import Union, Tuple
from socket import SOCK_STREAM, SOL_SOCKET, SO_LINGER, socket
from struct import pack
from XSocket.core.listener import Listener
from XSocket.core.net import AddressFamily, IPAddressInfo
from XSocket.protocol.protocol import ProtocolType
from XSocket.protocol.xtcp.handle import XTCPHandle
from XSocket.protocol.xtcp.socket import XTCPSocket

__all__ = [
    "XTCPListener"
]


class XTCPListener(Listener):
    """
    Listens for connections from TCP network clients.
    """

    def __init__(self, address: Union[IPAddressInfo, Tuple[str, int]]):
        """
        Listens for connections from TCP network clients.

        :param address: Local address
        """
        super().__init__()
        if isinstance(address, tuple):
            address = IPAddressInfo(address[0], address[1])
        self._address = address

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
        Gets the protocol type of the Socket.

        :return: ProtocolType
        """
        return ProtocolType.Xtcp

    def run(self):
        """
        Starts listening for incoming connection requests.
        """
        self._event_loop = get_running_loop()
        self._socket = socket(self.address_family, SOCK_STREAM)
        self._socket.setsockopt(SOL_SOCKET, SO_LINGER, pack("ii", 1, 0))
        self._socket.setblocking(False)
        self._socket.bind((*self._address,))
        self._socket.listen()
        self._running = True

    async def connect(self) -> XTCPHandle:
        """
        Establishes a connection to a remote host.

        :return: XTCPHandle
        """
        self._event_loop = get_running_loop()
        sock = socket(self.address_family, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_LINGER, pack("ii", 1, 0))
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

    def close(self):
        """
        Closes the listener.
        """
        self._socket.close()
        self._running = False
        self._closed = True
