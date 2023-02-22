from enum import Enum

__all__ = [
    "ProtocolType"
]


class ProtocolType(Enum):
    """
    Specifies the protocol scheme.
    """
    Unspecified = 0
    """Unspecified protocol."""
    Xtcp = 1
    """Extend TCP protocol."""
