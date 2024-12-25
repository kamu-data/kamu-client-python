import os

from ._connection import KamuConnection

__version__ = "0.5.0"


def connect(url=None, engine=None, connection_params=None) -> KamuConnection:
    """
    Open connection to a Kamu node.

    Examples
    --------
    >>> import kamu
    >>>
    >>> # Prefer using in a context manager
    >>> with kamu.connect("...") as con:
    >>>     pass
    >>>
    >>> # Connect to secure node
    >>> kamu.connect("grpc+tls://node.demo.kamu.dev:50050")
    >>>
    >>> # Connect to local insecure node
    >>> kamu.connect("grpc://localhost:50050")
    >>>
    >>> # Connect to Spark engine
    >>> kamu.connect("http://livy-host:8998", engine="spark")
    >>>
    >>> # Start a local SQL server in a workspace and connect to it:
    >>> kamu.connect("file:///path/to/workspace")
    """
    url = url or os.environ.get("KAMU_CLIENT_URL")
    if not url:
        raise ValueError("url is not specified")

    engine = (engine or "datafusion").lower()

    connection_params = connection_params or {}

    if url.startswith("file://"):
        from . import _connection_subprocess

        return _connection_subprocess.KamuConnectionSubprocess(
            url=url, connection_factory=connect, engine=engine, **connection_params
        )

    if engine == "datafusion":
        from . import _connection_flight_sql

        if not url.startswith("grpc"):
            raise ValueError(
                "DataFusion engine expects URLs with 'grpc://' or 'grpc+tls://' schemes. "
                "If you are seeing this message when running `kamu notebook` CLI command "
                "- restart the notebook with `--engine datafusion` argument."
            )

        return _connection_flight_sql.KamuConnectionFlightSql(
            url=url, **connection_params
        )
    if engine == "spark":
        from . import _connection_livy

        if not url.startswith("http"):
            raise ValueError(
                "Spark engine expects a Livy HTTP server URL with 'http://' or 'https://' "
                "schemes. If you are seeing this message when running `kamu notebook` CLI command "
                "- restart the notebook with `--engine spark` argument."
            )

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
