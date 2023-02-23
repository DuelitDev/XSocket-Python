from asyncio import create_task, gather, all_tasks
from isinstancex import tryinstance
from pyeventlib import EventHandler, EventArgs
from typing import Union, Optional, List
from XSocket.core.handle import IHandle
from XSocket.core.listener import IListener
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.protocol.protocol import ProtocolType
from XSocket.util import OperationControl, OPCode

__all__ = [
    "Client"
]


class OnOpenEventArgs(EventArgs):
    pass


class OnCloseEventArgs(EventArgs):
    pass


class OnMessageEventArgs(EventArgs):
    def __init__(self, data: List[bytearray]):
        self._data = data

    @property
    def data(self) -> bytearray:
        return self._data[0]


class OnErrorEventArgs(EventArgs):
    def __init__(self, exception: Exception):
        self._exception = exception

    @property
    def exception(self) -> Exception:
        return self._exception


class ClientEventWrapper:
    def __init__(self, on_open: EventHandler, on_close: EventHandler,
                 on_message: EventHandler, on_error: EventHandler):
        self.on_open: EventHandler = on_open
        self.on_close: EventHandler = on_close
        self.on_message: EventHandler = on_message
        self.on_error: EventHandler = on_error


class Client:
    def __init__(self, initializer: Union[IListener, IHandle]):
        self._listener: Optional[IListener] = None
        self._handle: Optional[IHandle] = None
        tryinstance(initializer, (IListener, IHandle))
        if isinstance(initializer, IListener):
            self._listener = initializer
        elif isinstance(initializer, IHandle):
            self._handle = initializer
        self._running: bool = False
        self._closed: bool = False
        self._on_open: EventHandler = EventHandler()
        self._on_close: EventHandler = EventHandler()
        self._on_message: EventHandler = EventHandler()
        self._on_error: EventHandler = EventHandler()
        self._event_wrapper: ClientEventWrapper = ClientEventWrapper(
            self._on_open, self._on_close, self._on_message, self._on_error)

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
            raise RuntimeError("Client is not connected.")
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
        return self._event_wrapper

    async def run(self):
        if self._running or self._closed:
            raise RuntimeError("Client is already running or closed.")
        self._running = True
        create_task(self._handler())

    async def close(self):
        if self._closed:
            return
        await self._handle.close()
        await gather(*all_tasks())
        self._closed = True
        self._running = False

    async def _handler(self):
        if not self._handle:
            self._handle = await self._listener.connect()
            await self._on_open(self, OnOpenEventArgs())
        while not self._closed:
            try:
                data = [await self._handle.receive()]
                await self._on_message(self, OnMessageEventArgs(data))
            except OperationControl:
                pass
            except ConnectionError:
                break
            except Exception as e:
                await self._on_error(self, OnErrorEventArgs(e))
                break
        await self._on_close(self, OnCloseEventArgs())

    async def send(self, data: Union[bytes, bytearray],
                   opcode: OPCode = OPCode.Data):
        tryinstance(data, (bytes, bytearray)) and tryinstance(opcode, OPCode)
        await self._handle.send(data, opcode)
