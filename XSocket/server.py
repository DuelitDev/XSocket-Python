from asyncio import Lock, Task, create_task, gather
from pyeventlib import EventHandler
from XSocket.client import Client
from XSocket.core.listener import IListener
from XSocket.core.net import AddressFamily, AddressInfo
from XSocket.events import (OnOpenEventArgs,
                            OnCloseEventArgs,
                            OnAcceptEventArgs,
                            OnErrorEventArgs)
from XSocket.exception import ServerClosedException
from XSocket.protocol.protocol import ProtocolType

__all__ = [
    "Server"
]


class ServerEventWrapper:
    def __init__(self):
        self.on_open: EventHandler = EventHandler()
        self.on_close: EventHandler = EventHandler()
        self.on_accept: EventHandler = EventHandler()
        self.on_error: EventHandler = EventHandler()


class Server:
    def __init__(self, listener: IListener):
        self._listener: IListener = listener
        self._clients: dict[int, Client] = {}
        self._wrapper_lock: Lock = Lock()
        self._collector_lock: Lock = Lock()
        self._task: Task | None = None
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
        """
        Represents the method that will handle an events.

        :return: ServerEventWrapper
        """
        return self._event

    async def run(self):
        """
        Starts listening for incoming connection requests.
        """
        if self._running or self._closed:
            return
        self._running = True
        self._listener.run()
        self._task = create_task(self._wrapper())

    async def close(self):
        """
        Close all client connections and server.
        """
        if not self._running or self._closed:
            return
        self._closed = True
        await self._task
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
        async with self._collector_lock:
            del self._clients[id(sender)]

    async def broadcast(self, data: bytes | bytearray):
        """
        Send data to all clients.

        :param data: Data to send
        """
        if not self._running or self._closed:
            raise ServerClosedException()
        tasks = [client.send(data) for client in self._clients.values()]
        await gather(*tasks)

    async def broadcast_string(self, string: str, encoding: str = "UTF-8"):
        """
        Send string to all clients.

        :param string: String to send
        :param encoding: String encoding
        """
        await self.broadcast(string.encode(encoding))
