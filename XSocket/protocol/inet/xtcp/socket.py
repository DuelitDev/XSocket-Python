# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from asyncio import AbstractEventLoop, get_running_loop
from socket import socket
from XSocket.core.socket import ISocket
from XSocket.protocol.inet.net import IPAddressInfo

__all__ = [
    "XTCPSocket"
]


class XTCPSocket(ISocket):
    """
    Implements XTCP sockets interface.
    """

    def __init__(self, socket_: socket):
        self._socket: socket = socket_
        self._event_loop: AbstractEventLoop = get_running_loop()

    @property
    def get_raw_socket(self) -> socket:
        """
        Get a low-level socket.

        :return: Low-level socket
        """
        return self._socket

    @property
    def local_address(self) -> IPAddressInfo:
        """
        Gets the local IP address info.

        :return: IPAddressInfo
        """
        return IPAddressInfo(*self._socket.getsockname())

    @property
    def remote_address(self) -> IPAddressInfo:
        """
        Gets the local IP address info.

        :return: IPAddressInfo
        """
        return IPAddressInfo(*self._socket.getpeername())

    def close(self):
        """
        Close the socket.
        """
        self._socket.close()

    async def send(self, data: bytearray):
        """
        Sends data to a connected Socket.

        :param data: Data to send
        """
        return await self._event_loop.sock_sendall(self._socket, data)

    async def receive(self, length: int, exactly: bool = False) -> bytearray:
        """
        Receives data from a bound Socket.

        :param length: The number of bytes to receive
        :param exactly: weather to read exactly
        :return: Received data
        """
        buffer = bytearray()
        while len(buffer) != length:
            buffer += await self._event_loop.sock_recv(
                self._socket, length - len(buffer))
            if not exactly:
                break
        return buffer
