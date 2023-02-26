from asyncio import Lock, create_task, gather, all_tasks
from isinstancex import tryinstance
from pyeventlib import EventHandler, EventArgs
from typing import Dict, Union
from XSocket.client import Client
from XSocket.core.listener import IListener
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.exception import *
from XSocket.protocol.protocol import ProtocolType
from XSocket.util import OPCode

__all__ = [
    "Server"
]


class OnOpenEventArgs(EventArgs):
    pass


class OnCloseEventArgs(EventArgs):
    pass


class OnAcceptEventArgs(EventArgs):
    def __init__(self, client: Client):
        self._client = client

    @property
    def client(self) -> Client:
        return self._client


class OnErrorEventArgs(EventArgs):
    def __init__(self, exception: Exception):
        self._exception = exception

    @property
    def exception(self) -> Exception:
        return self._exception


class ServerEventWrapper:
    def __init__(self):
        self._on_open: EventHandler = EventHandler()
        self._on_close: EventHandler = EventHandler()
        self._on_accept: EventHandler = EventHandler()
        self._on_error: EventHandler = EventHandler()

    @property
    def on_open(self) -> EventHandler:
        """
        An event handler that callback when the server is opened.

        :return: EventHandler
        """
        return self._on_open

    @property
    def on_close(self) -> EventHandler:
        """
        An event handler that callback when the server is closed.

        :return: EventHandler
        """
        return self._on_close

    @property
    def on_accept(self) -> EventHandler:
        """
        This is an event handler that callback
        when connection with client is established.

        :return: EventHandler
        """
        return self._on_accept

    @property
    def on_error(self) -> EventHandler:
        """
        An event handler that callback when error raised.

        :return: EventHandler
        """
        return self._on_error

    @on_open.setter
    def on_open(self, handler: EventHandler):
        """
        An event handler that callback when the server is opened.

        :return: EventHandler
        """
        tryinstance(handler, EventHandler, InvalidParameterException)
        self._on_open = handler

    @on_close.setter
    def on_close(self, handler: EventHandler):
        """
        An event handler that callback when the server is closed.

        :return: EventHandler
        """
        tryinstance(handler, EventHandler, InvalidParameterException)
        self._on_close = handler

    @on_accept.setter
    def on_accept(self, handler: EventHandler):
        """
        This is an event handler that callback
        when connection with client is established.

        :return: EventHandler
        """
        tryinstance(handler, EventHandler, InvalidParameterException)
        self._on_accept = handler

    @on_error.setter
    def on_error(self, handler: EventHandler):
        """
        An event handler that callback when error raised.

        :return: EventHandler
        """
        tryinstance(handler, EventHandler, InvalidParameterException)
        self._on_error = handler


class Server:
    def __init__(self, listener: IListener):
        tryinstance(listener, IListener)
        self._listener: IListener = listener
        self._clients: Dict[int, Client] = {}
        self._wrapper_lock: Lock = Lock()
        self._collector_lock: Lock = Lock()
        self._running: bool = False
        self._closed: bool = False
        self._event: ServerEventWrapper = ServerEventWrapper()

    @property
    def running(self) -> bool:
        """
        Gets a value indicating whether Server is running.

        :return: bool
        """
        return self._running

    @property
    def closed(self) -> bool:
        """
        Gets a value indicating whether Server has been closed.

        :return: bool
        """
        return self._closed

    @property
    def local_address(self) -> AddressInfo:
        """
        Gets the local endpoint.

        :return: AddressInfo
        """
        return self._listener.local_address

    @property
    def address_family(self) -> AddressFamily:
        """
        Gets the address family of the Socket.

        :return: AddressFamily
        """
        return self._listener.address_family

    @property
    def protocol_type(self) -> ProtocolType:
        """
        Gets the protocol type of the Listener.

        :return: ProtocolType
        """
        return self._listener.protocol_type

    @property
    def event(self) -> ServerEventWrapper:
        return self._event

    async def run(self):
        if self._running or self._closed:
            raise InvalidOperationException(
                "Server is already running or closed.")
        self._running = True
        self._listener.run()
        create_task(self._wrapper())

    async def close(self):
        if self._closed:
            return
        self._closed = True
        await gather(*all_tasks())
        await gather(*[client.close() for client in self._clients.values()])
        self._listener.close()
        self._running = False

    async def _wrapper(self):
        await self.event.on_open(self, OnOpenEventArgs())
        while not self._closed:
            try:
                handle = await self._listener.accept()
                client = Client(handle)
                client.event.on_close += self._collector
                async with self._wrapper_lock:
                    cid = id(client)
                    self._clients[cid] = client
                await client.run()
                await self.event.on_accept(self, OnAcceptEventArgs(client))
            except Exception as e:
                await self.event.on_error(self, OnErrorEventArgs(e))
        await self.event.on_close(self, OnCloseEventArgs())

    async def _collector(self, sender: Client, _):
        if self._closed:
            return
        async with self._collector_lock:
            del self._clients[id(sender)]

    async def broadcast(self, data: Union[bytes, bytearray],
                        opcode: OPCode = OPCode.Data):
        tryinstance(data, (bytes, bytearray)) and tryinstance(opcode, OPCode)
        tasks = [client.send(data, opcode) for client in self._clients.values()]
        await gather(*tasks)
