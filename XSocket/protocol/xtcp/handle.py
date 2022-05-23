import asyncio
from struct import pack, unpack
import typing
import socket
import enum
from .. import ProtocolType
from ...base.address import *
from ...base.handle import *


__all__ = ["XTCPHandle"]


class OPCode(enum.IntEnum):
    Continuation = 0x0
    Data = 0x2
    ConnectionClose = 0x8
    Ping = 0x9
    Pong = 0xA


class XTCPHandle(Handle):
    def __init__(self, socket_: socket.socket) -> None:
        super().__init__()
        self._socket = socket_
        self._event_loop = asyncio.get_running_loop()

    @property
    def local_address(self) -> AddressInfo:
        address, port = self._socket.getsockname()
        return IPAddressInfo(address, port)

    @property
    def remote_address(self) -> AddressInfo:
        address, port = self._socket.getpeername()
        return IPAddressInfo(address, port)

    @property
    def address_family(self) -> AddressFamily:
        return self.local_address.address_family

    @property
    def protocol_type(self) -> ProtocolType:
        return ProtocolType.Xtcp

# TODO: refactoring codes
    @staticmethod
    def pack(data: typing.Union[bytes, bytearray],
             opcode: OPCode = OPCode.Continuation,
             *args, **kwargs) -> typing.Generator[bytearray]:
        fin, con = 128, opcode.Continuation
        payload_length = (125, 65535)
        if len(data) <= payload_length[0]:
            header = bytearray([fin | opcode, len(data)])
            yield header + data
        elif len(data) <= payload_length[1]:
            header = bytearray([fin | opcode, 126, *pack("!H", len(data))])
            yield header + data
        else:
            for index in range(0, len(data), payload_length[1]):
                segment = data[index:index + payload_length[1]]
                header = bytearray([
                    opcode if not index else con,
                    126, *pack("!H", len(segment))])
                yield header + segment
            yield bytearray([fin | con, 0])  # finish packet

    @staticmethod
    def unpack(packets: typing.List[typing.Union[bytes, bytearray]],
               opcode: OPCode = OPCode.Continuation,
               *args, **kwargs) -> typing.Generator[int, bool]:
        pass

    async def send(self, data: typing.Union[bytes, bytearray]) -> None:
        for packet in self.pack(data, OPCode.Data):
            await self._event_loop.sock_sendall(self._socket, packet)

    async def receive(self) -> typing.Any:
        pass

    def close(self) -> None:
        self._socket.close()
        self._closed = True
