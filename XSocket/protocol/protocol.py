# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

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
