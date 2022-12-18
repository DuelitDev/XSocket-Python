# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from asyncio import Task, create_task
from pyeventlib import EventHandler
from typing import Optional
from XSocket.core.handle import IHandle
from XSocket.core.listener import IListener
from XSocket.util import OperationControl

__all__ = [
    "Client"
]


class ClientEventHandler:
    def __init__(self, on_open: EventHandler, on_close: EventHandler,
                 on_message: EventHandler, on_error: EventHandler):
        self.on_open: EventHandler = on_open
        self.on_close: EventHandler = on_close
        self.on_message: EventHandler = on_message
        self.on_error: EventHandler = on_error


class Client:
    def __init__(self, listener: IListener):
        self._listener: IListener = listener
        self._handle: Optional[IHandle] = None
        self._closed: bool = False
        self._on_open: EventHandler = EventHandler()
        self._on_close: EventHandler = EventHandler()
        self._on_message: EventHandler = EventHandler()
        self._on_error: EventHandler = EventHandler()

    async def run(self):
        create_task(self._handler())

    async def close(self):
        self._closed = True
        tasks = Task.all_tasks()
        for task in tasks:
            await task

    async def _handler(self):
        self._handle = await self._listener.connect()
        await self._on_open(self)
        while not self._closed and not self._handle.closed:
            try:
                data = await self._handle.receive()
                await self._on_message(self, data)
            except OperationControl:
                pass
            except ConnectionError:
                break
            except Exception as e:
                await self._on_error(self, e)
                break
        await self._on_close(self)

    async def send(self, *args, **kwargs):
        await self._handle.send(*args, **kwargs)

    async def disconnect(self):
        await self._handle.close()

    @property
    def event(self) -> ClientEventHandler:
        return ClientEventHandler(self._on_open, self._on_close,
                                  self._on_message, self._on_error)
