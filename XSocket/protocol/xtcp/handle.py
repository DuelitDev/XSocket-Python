import enum
import struct
import socket
import asyncio
from typing import Generator, Tuple, List, Union
from XSocket.protocol import ProtocolType
from XSocket.base import *


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
    def pack(data: bytearray, opcode: OPCode = OPCode.Continuation,
             *args, **kwargs) -> Generator[bytearray, None, None]:
        fin, con = 128, opcode.Continuation
        payload_length = (125, 65535)
        if len(data) <= payload_length[0]:
            header = bytearray([fin | opcode, len(data)])
            yield header + data
        elif len(data) <= payload_length[1]:
            header = bytearray([
                fin | opcode, payload_length[0] + 1,
                *struct.pack("!H", len(data))])
            yield header + data
        else:
            for index in range(0, len(data), payload_length[1]):
                segment = data[index:index + payload_length[1]]
                header = bytearray([
                    opcode if not index else con, payload_length[0] + 1,
                    *struct.pack("!H", len(segment))])
                yield header + segment
            yield bytearray([fin | con, 0])  # finish packet

    @staticmethod
    def unpack(packets: List[bytearray], *args, **kwargs
               ) -> Generator[Union[int, Tuple[OPCode, bytearray]], None, None]:
        for packet in packets:
            payload_length = (125, 65535)
            yield 2
            fin = (255 & packet[0]) >> 7
            op = OPCode(15 & packet[0])
            size = 127 & packet[1]
            if size == payload_length[0] + 1:
                yield 2
                size = struct.unpack("!H", packet[2:])[0]
            yield size
            yield op, packet[2 + (size > payload_length[0]) * 2:]
            if fin:
                break

    async def send(self, data: Union[bytes, bytearray],
                   opcode: OPCode = OPCode.Data) -> None:
        for packet in self.pack(bytearray(data), opcode):
            await self._event_loop.sock_sendall(self._socket, packet)

    async def receive(self) -> bytes:
        packets = []
        opcode = None
        temp = [bytearray()]
        for packet in self.unpack(temp):
            if isinstance(packet, int):
                recv = []
                while len(recv) != packet:
                    recv = await self._event_loop.sock_recv(
                        self._socket, packet - len(recv))
                temp[-1].extend(recv)
            elif isinstance(packet, tuple):
                if not opcode:
                    opcode = packet[0]
                if opcode == OPCode.Ping:
                    await self.send(packet[1], OPCode.Pong)
                elif opcode == OPCode.Data:
                    packets.append(packet[1])
        return b"".join(packets)

    def close(self) -> None:
        self._socket.close()
        self._closed = True
