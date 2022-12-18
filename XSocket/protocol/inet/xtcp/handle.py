# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from asyncio import AbstractEventLoop, get_running_loop
from struct import pack, unpack
from typing import Generator, List, Union
from XSocket.core.handle import Handle
from XSocket.core.net import AddressFamily
from XSocket.protocol.protocol import ProtocolType
from XSocket.protocol.inet.net import IPAddressInfo
from XSocket.protocol.inet.xtcp.socket import XTCPSocket
from XSocket.util import OPCode, OperationControl

__all__ = [
    "XTCPHandle"
]


class XTCPHandle(Handle):
    """
    Provides client connections for TCP network services.
    """
    def __init__(self, socket: XTCPSocket):
        """
        Provides client connections for TCP network services.

        :param socket: Socket to handle
        """
        super().__init__()
        self._socket: XTCPSocket = socket
        self._event_loop: AbstractEventLoop = get_running_loop()

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
    def pack(data: bytearray, opcode: OPCode = OPCode.Data, *args, **kwargs
             ) -> Generator[bytearray, None, None]:
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
    def unpack(packets: List[bytearray], *args, **kwargs
               ) -> Generator[Union[int, tuple], None, None]:
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
                raise ValueError("header is invalid.")
            if extend:
                yield 2
                size = unpack("!H", packet[2:])[0]
            yield size
            yield opcode, packet[2 + extend * 2:]
            if fin:
                break

    async def send(self, data: Union[bytes, bytearray],
                   opcode: OPCode = OPCode.Data):
        """
        Sends data to a connected Socket.

        :param data: Data to send
        :param opcode: Operation Code
        """
        for packet in self.pack(bytearray(data), opcode):
            await self._socket.send(packet)

    async def receive(self) -> bytearray:
        """
        Receives data from a bound Socket.

        :return: Received data
        """
        packets = bytearray()
        opcode = None
        temp = [bytearray()]
        for packet in self.unpack(temp):
            if isinstance(packet, int):
                temp[-1] += await self._socket.receive(packet, exactly=True)
                continue
            if opcode is None:
                opcode = packet[0]
            if opcode == OPCode.ConnectionClose or self._closed:
                if self._closed and opcode == OPCode.ConnectionClose:
                    await self._close(True)
                    raise ConnectionAbortedError(
                        "Connection was aborted by peer.")
                await self._close(False)
                raise OperationControl()
            elif opcode == OPCode.Continuation:
                raise ConnectionResetError("Connection was reset by peer.")
            elif opcode == OPCode.Data:
                packets += packet[1]
            temp.append(bytearray())
        return packets

    async def close(self):
        """
        Closes the Socket connection.
        """
        await self._close(_close_socket=False)

    async def _close(self, _close_socket: bool):
        """
        Sends a connection close signal to the peer and closes the socket.

        :param _close_socket: Whether to close the socket
        """
        if _close_socket:
            return self._socket.close()
        await self.send(bytearray(), OPCode.ConnectionClose)
        self._closed = True
