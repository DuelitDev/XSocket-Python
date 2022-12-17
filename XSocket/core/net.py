# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from abc import ABCMeta, abstractmethod
from enum import IntEnum
from ipaddress import ip_address
from isinstancex import isinstancex
from pyfieldlib import FieldMeta, fields

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


class AddressInfo(metaclass=type("", (ABCMeta, FieldMeta), {})):
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

    @abstractmethod
    def __hash__(self) -> int:
        """
        Returns a hash code for the current object.

        :return: hash code
        """
        pass


class IPAddressInfo(AddressInfo):
    """
    Represents a network endpoint as an IP address and a port number.
    """

    def __init__(self, address: str, port: int) -> None:
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
        Gets or sets the IP address of the AddressInfo.

        :return: String of ip address.
        """
        return self._address

    @property
    def port(self) -> int:
        """
        Gets or sets the port number of the AddressInfo.

        :return: 0 ~ 65535
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

    def __hash__(self) -> int:
        """
        Returns a hash code for the current object.

        :return: hash code
        """
        return hash((self._address, self._port))
