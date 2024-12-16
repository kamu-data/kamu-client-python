import contextlib
import sys

import adbc_driver_flightsql.dbapi
import adbc_driver_manager


class KamuConnection(contextlib.ExitStack):
    def __init__(self, url):
        super().__init__()

        self.url = url

        self._adbc = adbc_driver_flightsql.dbapi.connect(
            self.url,
            db_kwargs={
                adbc_driver_manager.DatabaseOptions.USERNAME.value: "kamu",
                adbc_driver_manager.DatabaseOptions.PASSWORD.value: "kamu",
            },
            autocommit=True,
        )

    def as_adbc(self):
        """
        Returns the underlying ADBC connection.

        Use this method when working with libraries that expect ADBC connection.

        Examples
        --------
        >>> import pandas
        >>> import kamu
        >>>
        >>> with kamu.connect() as con:
        >>>     pandas.read_sql("select 1", con.as_adbc())
        """
        return self._adbc

    def __enter__(self):
        super().__enter__()

        try:
            self.enter_context(self._adbc)
        except:
            if not self.__exit__(*sys.exc_info()):
                raise

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
