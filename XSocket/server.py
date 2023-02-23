from asyncio import Lock, create_task, gather, all_tasks
from isinstancex import tryinstance
from pyeventlib import EventHandler, EventArgs
from typing import Dict, Union
from XSocket.client import Client
from XSocket.core.listener import IListener
from XSocket.core.net import AddressFamily, AddressInfo
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
    def __init__(self,
                 on_open: EventHandler, on_close: EventHandler,
                 on_accept: EventHandler, on_error: EventHandler):
        self.on_open: EventHandler = on_open
        self.on_close: EventHandler = on_close
        self.on_accept: EventHandler = on_accept
        self.on_error: EventHandler = on_error


class Server:
    def __init__(self, listener: IListener):
        tryinstance(listener, IListener)
        self._listener: IListener = listener
        self._clients: Dict[int, Client] = {}
        self._wrapper_lock: Lock = Lock()
        self._collector_lock: Lock = Lock()
        self._running: bool = False
        self._closed: bool = False
        self._on_open: EventHandler = EventHandler()
        self._on_close: EventHandler = EventHandler()
        self._on_accept: EventHandler = EventHandler()
        self._on_error: EventHandler = EventHandler()
        self._event_wrapper: ServerEventWrapper = ServerEventWrapper(
            self._on_open, self._on_close, self._on_accept, self._on_error)

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
        return self._event_wrapper

    async def run(self):
        if self._running or self._closed:
            raise RuntimeError("Server is already running or closed.")
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
        await self._on_open(self, OnOpenEventArgs())
        while not self._closed:
            try:
                handle = await self._listener.accept()
                client = Client(handle)
                client.event.on_close += self._collector
                async with self._wrapper_lock:
                    cid = id(client)
                    self._clients[cid] = client
                await client.run()
                await self._on_accept(self, OnAcceptEventArgs(client))
            except Exception as e:
                await self._on_error(self, OnErrorEventArgs(e))
        await self._on_close(self, OnCloseEventArgs())

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
