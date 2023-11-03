from asyncio import AbstractEventLoop, get_running_loop
from struct import pack, unpack
from typing import Any, Generator
from XSocket.core.handle import IHandle
from XSocket.core.net import AddressFamily
from XSocket.exception import (ConnectionAbortedException,
                               HandleClosedException,
                               InvalidOperationException)
from XSocket.protocol.protocol import ProtocolType
from XSocket.protocol.inet.net import IPAddressInfo
from XSocket.protocol.inet.xtcp.socket import XTCPSocket
from XSocket.util import OPCode

__all__ = [
    "XTCPHandle"
]


class XTCPHandle(IHandle):
    """
    Provides client connections for TCP network services.
    """

    def __init__(self, socket: XTCPSocket):
        """
        Provides client connections for TCP network services.

        :param socket: Socket to handle
        """
        self._socket: XTCPSocket = socket
        self._event_loop: AbstractEventLoop = get_running_loop()
        self._closed: bool = False

    @property
    def closed(self) -> bool:
        """
        Gets a value indicating whether
        the Socket for a Handle has been closed.

        :return: bool
        """
        return self._closed

    @property
    def local_address(self) -> IPAddressInfo:
        """
        Gets the local ip endpoint.

        :return: IPAddressInfo
        """
        return self._socket.local_address

    @property
    def remote_address(self) -> IPAddressInfo:
        """
        Gets the remote ip endpoint.

        :return: IPAddressInfo
        """
        return self._socket.remote_address

    @property
    def address_family(self) -> AddressFamily:
        """
        Gets the address family of the Socket.

        :return: AddressFamily
        """
        return self.local_address.address_family

    @property
    def protocol_type(self) -> ProtocolType:
        """
        Gets the protocol type of the Handle.

        :return: ProtocolType
        """
        return ProtocolType.Xtcp

    @staticmethod
    async def create(address: IPAddressInfo) -> "XTCPHandle":
        """
        Create a new XTCPHandle with the IP address info.

        :param address: IPAddressInfo
        :return: XTCPHandle
        """
        return XTCPHandle(await XTCPSocket.create(address))

    async def close(self):
        """
        Closes the Socket connection.
        """
        if self._closed:
            return
        await self._close(_close_socket=False)
        self._closed = True

    async def _close(self, _close_socket: bool):
        """
        Sends a connection close signal to the peer and closes the socket.

        :param _close_socket: Whether to close the socket
        """
        if _close_socket:
            self._socket.close()
            return
        await self.send(bytearray(), OPCode.ConnectionClose)

    @staticmethod
    def pack(data: bytearray, opcode: OPCode) -> Generator[bytearray, Any, Any]:
        """
        Generates a packet to be transmitted.

        :param data: Data to send
        :param opcode: Data type
        :return: Packet generator
        """
        fin = 128
        if len(data) <= 125:
            header = bytearray([fin | opcode, len(data)])
            yield header + data
        elif len(data) <= 65535:
            header = bytearray([fin | opcode, 126, *pack("!H", len(data))])
            yield header + data
        else:
            for index in range(0, len(data), 65535):
                segment = data[index:index + 65535]
                header = bytearray([
                    opcode if index == 0 else OPCode.Continuation, 126,
                    *pack("!H", len(segment))])
                yield header + segment
            yield bytearray([fin | OPCode.Continuation, 0])

    @staticmethod
    def unpack(packets: list[bytearray]) -> Generator[int, Any, Any]:
        """
        Read the header of the received packet and get the data.

        If generator yields an integer, It must receive an integer size of data
        from the socket and append it to the bytearray of the list.

        If generator yields a tuple, It must empty the bytearray of the list.
        Also, tuple contains OPCode and data.

        :param packets: Received packet, bytearray in list must be empty
        :return: See docstring
        """
        for packet in packets:
            yield 2
            fin = packet[0] >> 7
            rsv = ((127 & packet[0]) >> 4) + (packet[1] >> 7)
            opcode = OPCode(15 & packet[0])
            size = 127 & packet[1]
            extend = size == 126
            if rsv != 0:
                raise InvalidOperationException()
            if extend:
                yield 2
                size = unpack("!H", packet[2:])[0]
            else:
                yield 0
            packet.clear()
            yield size
            yield opcode
            if fin:
                break

    async def send(self, data: bytes | bytearray, opcode: OPCode):
        """
        Sends data to a connected Socket.

        :param data: Data to send
        :param opcode: Operation Code
        """
        if self._closed:
            raise HandleClosedException()
        for packet in self.pack(bytearray(data), opcode):
            await self._socket.send(packet)

    async def receive(self) -> bytearray:
        """
        Receives data from a bound Socket.

        :return: Received data
        """
        if self._closed:
            raise HandleClosedException()
        opcode = None
        temp = [bytearray()]
        counter = 0
        for packet in self.unpack(temp):
            counter += 1
            if counter % 4 != 0:
                temp[-1] += await self._socket.receive(packet, exactly=True)
                continue
            if opcode is None:
                opcode = packet
            if opcode == OPCode.ConnectionClose or self._closed:
                await self._close(True)
                raise ConnectionAbortedException()
            elif opcode == OPCode.Continuation:
                raise InvalidOperationException()
            temp.append(bytearray())
        return bytearray(b"".join(temp))
