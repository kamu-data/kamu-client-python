from ._connection import KamuConnection

__version__ = "0.2.0"


def connect(url, engine=None):
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
    engine = (engine or "datafusion").lower()
    if engine == "datafusion":
        from . import _connection_flight_sql

        return _connection_flight_sql.KamuConnectionFlightSql(url=url)
    elif engine == "spark":
        from . import _connection_livy

        return _connection_livy.KamuConnectionLivy(url=url)
    else:
        raise NotImplementedError(f"Engine '{engine}' is not supported")
