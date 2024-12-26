import adbc_driver_flightsql.dbapi
import adbc_driver_manager
import pandas

from ._connection import KamuConnection


class KamuConnectionFlightSql(KamuConnection):
    """
    `KamuConnection` implementation using ADBC client protocol
    """

    def __init__(self, url, token=None, **connection_params):
        super().__init__()

        self._url = url

        if token:
            connection_params[
                adbc_driver_flightsql.DatabaseOptions.AUTHORIZATION_HEADER.value
            ] = f"Bearer {token}"
        else:
            # We don't allow fully non-authenticated access.
            # Anonymous users still have to go through basic auth procedure
            # so that server can reject new client, apply backpressure, or assign
            # a temporary session token that can be used to identify the client and
            # apply individual rate limiting strategies.
            connection_params[adbc_driver_manager.DatabaseOptions.USERNAME.value] = (
                "anonymous"
            )
            connection_params[adbc_driver_manager.DatabaseOptions.PASSWORD.value] = ""

        self._adbc = adbc_driver_flightsql.dbapi.connect(
            self._url,
            db_kwargs=connection_params,
            autocommit=True,
        )

    def __repr__(self):
        return f"KamuConnectionFlightSql(url='{self._url}')"

    def url(self):
        return self._url

    def query(self, sql):
        return pandas.read_sql(sql, self.as_adbc())

    def as_adbc(self):
        return self._adbc

    def __enter__(self):
        self._adbc.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._adbc.__exit__(exc_type, exc_value, traceback)

    def close(self):
        self._adbc.close()
