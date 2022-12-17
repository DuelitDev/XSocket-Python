# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from asyncio import AbstractEventLoop, get_running_loop
from socket import socket
from XSocket.core.net import IPAddressInfo
from XSocket.core.socket import Socket

__all__ = [
    "XTCPSocket"
]


class XTCPSocket(Socket):
    def __init__(self, socket_: socket):
        self._socket: socket = socket_
        self._event_loop: AbstractEventLoop = get_running_loop()

    @property
    def local_address(self) -> IPAddressInfo:
        return IPAddressInfo(*self._socket.getsockname())

    @property
    def remote_address(self) -> IPAddressInfo:
        return IPAddressInfo(*self._socket.getpeername())

    @property
    def get_raw_socket(self) -> socket:
        return self._socket

    async def send(self, data: bytearray):
        return await self._event_loop.sock_sendall(self._socket, data)

    async def receive(self, length: int, exactly: bool = False) -> bytearray:
        buffer = bytearray()
        while len(buffer) != length:
            buffer += await self._event_loop.sock_recv(
                self._socket, length - len(buffer))
            if not exactly:
                break
        return buffer

    def close(self):
        self._socket.close()
