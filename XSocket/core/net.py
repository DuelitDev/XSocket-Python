# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from abc import ABCMeta, abstractmethod
from enum import IntEnum
from pyfieldlib import FieldMeta

__all__ = [
    "AddressFamily",
    "AddressInfo"
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

    @abstractmethod
    def __hash__(self) -> int:
        """
        Returns a hash code for the current object.

        :return: Hash code
        """
