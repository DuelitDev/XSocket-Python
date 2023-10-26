class InvalidParameterException(Exception):
    pass


class InvalidOperationException(RuntimeError):
    pass


class ClosedException(Exception):
    pass


class SocketClosedException(ClosedException):
    pass


class HandleClosedException(ClosedException):
    pass


class ListenerClosedException(ClosedException):
    pass


class ServerClosedException(ClosedException):
    pass


class ClientClosedException(ClosedException):
    pass


class ConnectionAbortedException(ConnectionAbortedError):
    pass
