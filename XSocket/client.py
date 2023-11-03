from asyncio import Task, create_task
from pyeventlib import EventHandler
from XSocket.core.handle import IHandle
from XSocket.core.listener import IListener
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.events import (OnOpenEventArgs,
                            OnCloseEventArgs,
                            OnMessageEventArgs,
                            OnErrorEventArgs)
from XSocket.exception import (InvalidOperationException,
                               ClientClosedException)
from XSocket.protocol.protocol import ProtocolType
from XSocket.util import OPCode, OperationControl

__all__ = [
    "Client"
]


class ClientEventWrapper:
    """
    Represents the method that will handle an events.
    """
    def __init__(self):
        self.on_open: EventHandler = EventHandler()
        self.on_close: EventHandler = EventHandler()
        self.on_message: EventHandler = EventHandler()
        self.on_error: EventHandler = EventHandler()


class Client:
    """
    Provides client connections for network services.
    """
    def __init__(self, initializer: IListener | IHandle):
        self._listener: IListener | None = None
        self._handle: IHandle | None = None
        if isinstance(initializer, IListener):
            self._listener = initializer
        elif isinstance(initializer, IHandle):
            self._handle = initializer
        self._task: Task | None = None
        self._running: bool = False
        self._closed: bool = False
        self._event: ClientEventWrapper = ClientEventWrapper()

    @property
    def running(self) -> bool:
        """
        Gets a value indicating whether Client is running.

        :return: bool
        """
        return self._running

    @property
    def closed(self) -> bool:
        """
        Gets a value indicating whether Client has been closed.

        :return: bool
        """
        return self._closed

    @property
    def local_address(self) -> AddressInfo:
        """
        Gets the local endpoint.

        :return: AddressInfo
        """
        if not self._handle:
            return self._listener.local_address
        return self._handle.local_address

    @property
    def remote_address(self) -> AddressInfo:
        """
        Gets the remote ip endpoint.

        :return: AddressInfo
        """
        if not self._running:
            raise InvalidOperationException("Client is not connected.")
        return self._handle.remote_address

    @property
    def address_family(self) -> AddressFamily:
        """
        Gets the address family of the Socket.

        :return: AddressFamily
        """
        if not self._handle:
            return self._listener.address_family
        return self._handle.address_family

    @property
    def protocol_type(self) -> ProtocolType:
        """
        Gets the protocol type of the Listener.

        :return: ProtocolType
        """
        if not self._handle:
            return self._listener.protocol_type
        return self._handle.protocol_type

    @property
    def event(self) -> ClientEventWrapper:
        """
        Represents the method that will handle an events.

        :return: ClientEventWrapper
        """
        return self._event

    async def run(self):
        """
        Establishes a connection to a remote host.
        """
        if self._running or self._closed:
            return
        self._running = True
        self._task = create_task(self._handler())

    async def close(self):
        """
        Close the connection.
        """
        if not self._running or self._closed:
            return
        await self._handle.close()
        await self._task
        self._closed = True
        self._running = False

    async def _handler(self):
        if not self._handle:
            self._handle = await self._listener.connect()
            await self.event.on_open(self, OnOpenEventArgs())
        while not self._closed:
            try:
                data = [await self._handle.receive()]
                await self.event.on_message(self, OnMessageEventArgs(data))
            except OperationControl:
                pass
            except ConnectionError:
                break
            except Exception as e:
                await self.event.on_error(self, OnErrorEventArgs(e))
                break
        await self.event.on_close(self, OnCloseEventArgs())

    async def send(self, data: bytes | bytearray):
        """
        Send data to server.

        :param data: Data to send
        """
        if not self._running or self._closed:
            raise ClientClosedException()
        await self._handle.send(data, OPCode.Data)

    async def send_string(self, string: str, encoding: str = "UTF-8"):
        """
        Send string to server.

        :param string: String to send
        :param encoding: String encoding
        """
        await self.send(string.encode(encoding))
