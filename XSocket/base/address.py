import ipaddress
from enum import IntEnum
from abc import ABC, abstractmethod
from isinstancex import isinstancex
from pifields import fields, FieldMeta


__all__ = [
    "AddressFamily",
    "AddressInfo",
    "IPAddressInfo"
]


class AddressFamily(IntEnum):
    """
    Specifies the addressing scheme
    that a socket will use to resolve an address.
    """
    Unspecified = 0
    """Unspecified address family."""
    Unix = 1
    """Unix local to host address."""
    InterNetwork = 2
    """Address for IP version 4."""
    InterNetworkV6 = 23
    """Address for IP version 6."""


class AddressInfo(ABC):
    """
    Identifies a network address.
    """

    @property
    @abstractmethod
    def address_family(self) -> AddressFamily:
        """
        Gets the address family.

        :return: AddressFamily
        """
        pass


class IPAddressInfo(AddressInfo, FieldMeta):
    """
    Represents a network endpoint as an IP address and a port number.
    """

    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port

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
        Gets or sets the IP address of the AddressInfo.

        :return: String of ip address.
        """
        return self._address

    @property
    def port(self) -> int:
        """
        Gets or sets the port number of the AddressInfo.

        :return: AddressFamily
        """
        return self._port

    @property
    def address_family(self) -> AddressFamily:
        """
        Gets the address family.

        :return: AddressFamily
        """
        address = ipaddress.ip_address(self._address)
        return AddressFamily.InterNetwork if address.version == 4 \
            else AddressFamily.InterNetworkV6

    @address.setter
    def address(self, value: str) -> None:
        """
        Gets or sets the IP address of the AddressInfo.

        :return: String of ip address.
        """
        isinstancex(value, str)
        assert ipaddress.ip_address(value) is not None, "Address is invalid."
        self._address = value

    @port.setter
    def port(self, value: int) -> None:
        """
        Gets or sets the port number of the AddressInfo.

        :return: AddressFamily
        """
        isinstancex(value, int)
        assert 0 <= value <= 65535, "The port must be between 0 and 65535."
        self._port = value
