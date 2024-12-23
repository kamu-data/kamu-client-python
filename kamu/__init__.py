import os

from ._connection import KamuConnection

__version__ = "0.4.2"


def connect(url=None, engine=None, connection_params=None) -> KamuConnection:
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

    connection_params = connection_params or {}

    if engine == "datafusion":
        from . import _connection_flight_sql

        return _connection_flight_sql.KamuConnectionFlightSql(
            url=url, **connection_params
        )
    if engine == "spark":
        from . import _connection_livy

        return _connection_livy.KamuConnectionLivy(url=url, **connection_params)

    raise ValueError(f"Engine '{engine}' is not supported")


def load_ipython_extension(ipython):
    """
    Called when running `%load_ext kamu` in Jupyter / IPython.
    """
    from . import _jupyter

    ipython.register_magics(_jupyter.KamuMagics)

    try:
        import autovizwidget.widget.utils

        autoviz = autovizwidget.widget.utils.display_dataframe
    except ImportError:
        autoviz = None

    if autoviz:
        ipython.display_formatter.ipython_display_formatter.for_type_by_name(
            "pandas.core.frame",
            "DataFrame",
            autoviz,
        )
