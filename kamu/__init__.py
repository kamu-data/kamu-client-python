from . import _connection


__version__ = "0.1.2"


def connect(url):
    """
    Open connection to a Kamu node.

    Examples
    --------
    >>> import kamu
    >>>
    >>> # Connect to secure node
    >>> with kamu.connect("grpc+tls://node.demo.kamu.dev:50050") as con:
    >>>     pass
    >>>
    >>> # Connect to local insecure node
    >>> with kamu.connect("grpc://localhost:50050") as con:
    >>>     pass
    """
    return _connection.KamuConnection(url=url)
