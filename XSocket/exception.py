__all__ = [
    "InvalidParameterException",
    "InvalidOperationException",
    "ClosedException",
    "SocketClosedException",
    "HandleClosedException",
    "ListenerClosedException",
    "ServerClosedException",
    "ClientClosedException",
    "ConnectionAbortedException"
]


class InvalidParameterException(Exception):
    """
    The exception that is thrown when
    an invalid parameter is passed to a method.
    """


class InvalidOperationException(RuntimeError):
    """
    The exception that is thrown when a method call is invalid
    for the object's current state.
    """


class ClosedException(Exception):
    """
    The exception that is thrown when closed object is used.
    """


class SocketClosedException(ClosedException):
    """
    The exception that is thrown when closed socket is used.
    """


class HandleClosedException(ClosedException):
    """
    The exception that is thrown when closed handle is used.
    """


class ListenerClosedException(ClosedException):
    """
    The exception that is thrown when closed listener is used.
    """


class ServerClosedException(ClosedException):
    """
    The exception that is thrown when closed server is used.
    """


class ClientClosedException(ClosedException):
    """
    The exception that is thrown when closed client is used.
    """


class ConnectionAbortedException(ConnectionAbortedError):
    """
    The exception that is thrown when connection is aborted.
    """
