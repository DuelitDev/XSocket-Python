from ipaddress import ip_address
from isinstancex import isinstancex
from pyfieldlib import fields
from typing import Iterator, Union
from XSocket.core.net import AddressFamily, AddressInfo

__all__ = [
    "IPAddressInfo"
]


class IPAddressInfo(AddressInfo):
    """
    Represents a network endpoint as an IP address and a port number.
    """

    def __init__(self, address: str, port: int):
        isinstancex(address, str) and isinstancex(port, int)
        assert ip_address(address) is not None, "Address is invalid."
        assert 0 <= port <= 65535, "The port must be between 0 and 65535."
        self._address: str = address
        self._port: int = port

    @fields
    def max_port(self) -> int:
        """
        Specifies the maximum value that can be assigned to the Port property.
        This field is read-only.

        :return: 65535
        """
        return 65535

    @fields
    def min_port(self) -> int:
        """
        Specifies the minimum value that can be assigned to the Port property.
        This field is read-only.

        :return: 0
        """
        return 0

    @property
    def address(self) -> str:
        """
        Gets the IP address of the AddressInfo.

        :return: String of ip address
        """
        return self._address

    @property
    def port(self) -> int:
        """
        Gets the port number of the AddressInfo.

        :return: Port number
        """
        return self._port

    @property
    def address_family(self) -> AddressFamily:
        """
        Gets the address family.

        :return: AddressFamily
        """
        if ip_address(self._address).version == 4:
            return AddressFamily.InterNetwork
        else:
            return AddressFamily.InterNetworkV6

    def __iter__(self) -> Iterator[Union[str, int]]:
        """
        Gets the IP address and port number of the AddressInfo as an iterator.

        :return: IP Address, Port number
        """
        return iter((self._address, self._port))

    def __hash__(self) -> int:
        """
        Returns a hash code for the current object.

        :return: Hash code
        """
        return hash((self._address, self._port))
