from enum import IntEnum


__all__ = [
    "ProtocolType"
]


class ProtocolType(IntEnum):
    """
    Specifies the protocol scheme.
    """
    Unspecified = 0
    """Unspecified protocol."""
    Xtcp = 1
    """Extend TCP protocol."""
