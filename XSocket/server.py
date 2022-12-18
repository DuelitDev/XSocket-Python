# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from asyncio import Task, Lock, create_task
from pyeventlib import EventHandler
from typing import Dict
from XSocket.core.handle import IHandle
from XSocket.core.listener import IListener
from XSocket.util import OperationControl

__all__ = [
    "Server"
]


class ServerEventHandler:
    def __init__(self, on_open: EventHandler, on_close: EventHandler,
                 on_connect: EventHandler, on_disconnect: EventHandler,
                 on_message: EventHandler, on_error: EventHandler):
        self.on_open: EventHandler = on_open
        self.on_close: EventHandler = on_close
        self.on_connect: EventHandler = on_connect
        self.on_disconnect: EventHandler = on_disconnect
        self.on_message: EventHandler = on_message
        self.on_error: EventHandler = on_error


class Server:
    def __init__(self, listener: IListener):
        self._listener: IListener = listener
        self._handles: Dict[int, IHandle] = {}
        self._wrapper_lock: Lock = Lock()
        self._collector_lock: Lock = Lock()
        self._closed: bool = False
        self._on_open: EventHandler = EventHandler()
        self._on_close: EventHandler = EventHandler()
        self._on_connect: EventHandler = EventHandler()
        self._on_disconnect: EventHandler = EventHandler()
        self._on_message: EventHandler = EventHandler()
        self._on_error: EventHandler = EventHandler()

    async def run(self):
        self._listener.run()
        create_task(self._wrapper())

    async def close(self):
        self._closed = True
        tasks = Task.all_tasks()
        for task in tasks:
            await task

    async def _wrapper(self):
        await self._on_open(self)
        while not self._closed:
            handle = await self._listener.accept()
            cid = hash(handle)
            async with self._wrapper_lock:
                self._handles[cid] = handle
            create_task(self._handler(cid))
        await self._on_close(self)

    async def _handler(self, cid: int):
        handle = self._handles[cid]
        await self._on_connect(self, cid)
        while not self._closed and not handle.closed:
            try:
                data = await handle.receive()
                await self._on_message(self, cid, data)
            except OperationControl:
                pass
            except (ConnectionAbortedError, ConnectionResetError):
                break
            except Exception as e:
                await self._on_error(self, e)
                break
        await self._on_disconnect(self, cid)

    async def send(self, cid: int, *args, **kwargs):
        await self._handles[cid].send(*args, **kwargs)

    async def broadcast(self, *args, **kwargs):
        for cid in self._handles:
            await self.send(cid, *args, **kwargs)

    async def disconnect(self, cid: int):
        async with self._collector_lock:
            del self._handles[cid]

    @property
    def event(self) -> ServerEventHandler:
        return ServerEventHandler(self._on_open, self._on_close,
                                  self._on_connect, self._on_disconnect,
                                  self._on_message, self._on_error)
