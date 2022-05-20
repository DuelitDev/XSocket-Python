import asyncio
import struct
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

    @staticmethod
    async def pack(data: typing.Union[bytes, bytearray],
                   opcode: OPCode = OPCode.Continuation,
                   *args, **kwargs) -> typing.List[bytearray]:
        fin, payload_length = 128, (125, 65535)
        data = bytearray(data)
        packets = []
        if len(data) <= payload_length[0]:
            header = bytearray([fin | opcode, len(data)])
            packets.append(header + data)
        elif len(data) <= payload_length[1]:
            header = bytearray([fin | opcode, 126,
                                *struct.pack("!H", len(data))])
            packets.append(header + data)
        else:
            header = bytearray([fin | opcode, 126,
                                *struct.pack("!H", payload_length[1])])
            packets.append(header + data[:payload_length[1]])
            packets.extend(await XTCPHandle.pack(data[payload_length[1]:]))
        return packets

    @staticmethod
    async def unpack(data: typing.Union[bytes, bytearray],
                   opcode: OPCode = OPCode.Continuation,
                   *args, **kwargs) -> typing.List[bytearray]:
        pass

    async def send(self, *args, **kwargs) -> None:
        pass

    async def receive(self) -> typing.Any:
        pass

    def close(self) -> None:
        self._socket.close()
        self._closed = True
