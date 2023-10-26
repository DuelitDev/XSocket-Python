from pyeventlib import EventArgs


__all__ = [
    "OnOpenEventArgs",
    "OnCloseEventArgs",
    "OnAcceptEventArgs",
    "OnMessageEventArgs",
    "OnErrorEventArgs"
]


class OnOpenEventArgs(EventArgs):
    pass


class OnCloseEventArgs(EventArgs):
    pass


class OnAcceptEventArgs(EventArgs):
    def __init__(self, client: "Client"):
        self._client = client

    @property
    def client(self) -> "Client":
        return self._client


class OnMessageEventArgs(EventArgs):
    def __init__(self, data: list[bytearray]):
        self._data = data

    @property
    def data(self) -> bytearray:
        return self._data[0]


class OnErrorEventArgs(EventArgs):
    def __init__(self, exception: Exception):
        self._exception = exception

    @property
    def exception(self) -> Exception:
        return self._exception
