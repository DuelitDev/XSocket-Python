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
