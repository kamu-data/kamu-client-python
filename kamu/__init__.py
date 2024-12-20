import os

from ._connection import KamuConnection

__version__ = "0.2.1"


def connect(url=None, engine=None, connection_config=None) -> KamuConnection:
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
    url = url or os.environ.get("KAMU_CLIENT_URL")
    if not url:
        raise ValueError("url is not specified")

    engine = (engine or "datafusion").lower()

    connection_config = connection_config or {}

    if engine == "datafusion":
        from . import _connection_flight_sql

        return _connection_flight_sql.KamuConnectionFlightSql(
            url=url, **connection_config
        )
    if engine == "spark":
        from . import _connection_livy

        return _connection_livy.KamuConnectionLivy(url=url, **connection_config)

    raise ValueError(f"Engine '{engine}' is not supported")
