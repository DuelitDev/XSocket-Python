from enum import IntEnum
from abc import ABCMeta, abstractmethod


__all__ = [
    # Classes
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


class AddressInfo(metaclass=ABCMeta):
    @property
    @abstractmethod
    def address_family(self) -> AddressFamily:
        """
        Gets the address family.

        :return: AddressFamily
        """
        pass
