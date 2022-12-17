# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from abc import ABCMeta, abstractmethod
from asyncio import AbstractEventLoop
from typing import Optional
from XSocket.core.handle import Handle
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.core.socket import Socket
from XSocket.protocol.protocol import ProtocolType

__all__ = [
    "Listener"
]


class Listener(metaclass=ABCMeta):
    """
    Listens for connections from network clients.
    """
    def __init__(self, *args, **kwargs) -> None:
        self._socket: Optional[Socket] = None
        self._address: Optional[AddressInfo] = None
        self._event_loop: Optional[AbstractEventLoop] = None
        self._running: bool = False
        self._closed: bool = False

    @property
    def is_running(self) -> bool:
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
        Gets the protocol type of the Socket.

        :return: ProtocolType
        """

    @abstractmethod
    def run(self):
        """
        Starts listening for incoming connection requests.
        """

    @abstractmethod
    async def connect(self) -> Handle:
        """
        Establishes a connection to a remote host.

        :return: Handle
        """

    @abstractmethod
    async def accept(self) -> Handle:
        """
        Creates a new Handle for a newly created connection.

        :return: Handle
        """

    @abstractmethod
    def close(self):
        """
        Closes the listener.
        """
