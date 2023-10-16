class InvalidParameterException(Exception):
    pass


class InvalidOperationException(RuntimeError):
    pass


class HandleClosedException(Exception):
    pass


class ConnectionAbortedException(ConnectionAbortedError):
    pass
