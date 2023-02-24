class InvalidParameterException(Exception):
    pass


class InvalidOperationException(RuntimeError):
    pass


class ConnectionAbortedException(ConnectionAbortedError):
    pass


class ConnectionResetException(ConnectionResetError):
    pass


class BrokenPipeException(BrokenPipeError):
    pass
