import adbc_driver_flightsql.dbapi
import adbc_driver_manager
import pandas

from ._connection import KamuConnection


class KamuConnectionFlightSql(KamuConnection):
    """
    `KamuConnection` implementation using ADBC client protocol
    """

    def __init__(self, url):
        super().__init__()

        self._url = url

        self._adbc = adbc_driver_flightsql.dbapi.connect(
            self._url,
            db_kwargs={
                adbc_driver_manager.DatabaseOptions.USERNAME.value: "kamu",
                adbc_driver_manager.DatabaseOptions.PASSWORD.value: "kamu",
            },
            autocommit=True,
        )

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
