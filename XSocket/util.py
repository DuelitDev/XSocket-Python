# XSocket (version: 0.0.2a)
#
# Copyright 2022. DuelitDev all rights reserved.
#
# This Library is distributed under the LGPL-2.1 License.

from enum import IntEnum

__all__ = [
    "OPCode",
    "OperationControl"
]


class OPCode(IntEnum):
    """
    Specifies the data type.
    """
    Continuation = 0x0
    Data = 0x2
    ConnectionClose = 0x8


class OperationControl(BaseException):
    """
    Used to raise intentional exceptions.
    """
