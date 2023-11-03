from pyeventlib import EventArgs


__all__ = [
    "OnOpenEventArgs",
    "OnCloseEventArgs",
    "OnAcceptEventArgs",
    "OnMessageEventArgs",
    "OnErrorEventArgs"
]


class OnOpenEventArgs(EventArgs):
    """
    Contains state information and event data associated
    with socket open event.
    """
    pass


class OnCloseEventArgs(EventArgs):
    """
    Contains state information and event data associated
    with socket closed event.
    """
    pass


class OnAcceptEventArgs(EventArgs):
    """
    Contains state information and event data associated
    with event of client accepted from server.
    """
    def __init__(self, client):
        self._client = client

    @property
    def client(self):
        """
        Returns a client object.

        :return: Client
        """
        return self._client


class OnMessageEventArgs(EventArgs):
    """
    Contains state information and event data associated
    with message received event.
    """
    def __init__(self, data: list[bytearray]):
        self._data = data

    @property
    def data(self) -> bytearray:
        """
        Returns received message.

        :return: Data of bytes
        """
        return self._data[0]


class OnErrorEventArgs(EventArgs):
    """
    Contains state information and event data associated
    with error occurred event.
    """
    def __init__(self, exception: Exception):
        self._exception = exception

    @property
    def exception(self) -> Exception:
        """
        Returns occurred error object.

        :return: Exception
        """
        return self._exception
