import livy
import pandas

from ._connection import KamuConnection

SESSION_SETUP = r"""
import os

# spark.sparkContext._jvm.org.datasyslab.geosparksql.utils.GeoSparkSQLRegistrator.registerAll(sc._jvm.SQLContext(sc._jsc.sc()))

def resolve_dataset_ref(dataset_ref):
    if "/" not in dataset_ref:
        # Single-tenant
        data_path = os.path.join(dataset_ref, "data")
        if os.path.exists(data_path):
            return os.path.join(data_path, "*")
    else:
        # Multi-tenant
        # Assumptions:
        # - Layout of the data directory is `<account_name>/<dataset_id>/info/alias`
        # - Alias file contains `<account_name>/<dataset_name>`
        #   - Note there is a bug where alias may conain just `<dataset_name>` so we account for that too
        account_name, dataset_name = dataset_ref.split("/", 1)
        if os.path.isdir(account_name):
            for dataset_id in os.listdir(account_name):
                alias_path = os.path.join(account_name, dataset_id, "info", "alias")
                if not os.path.exists(alias_path):
                    continue
                with open(alias_path) as f:
                    alias = f.read().strip()
                if alias != dataset_ref and alias != dataset_name:
                    continue
                return os.path.join(account_name, dataset_id, "data", "*")

    raise Exception(f"Dataset {dataset_ref} not found")
"""


class KamuConnectionLivy(KamuConnection):
    """
    `KamuConnection` implementation using Spark Livy HTTP gateway protocol.

    This connection type is deprecated and should not be used in production. It does
    not support proper auth and has issues correctly representing certain data types.
    Livy gateway will be replaced in the near future with ADBC + FlightSQL based implementation.
    """

    def __init__(self, url):
        super().__init__()

        self._url = url
        self._livy = livy.LivySession.create(self._url)
        self._livy.wait()
        self._livy.run(SESSION_SETUP)

    def url(self):
        return self._url

    def query(self, sql):
        try:
            # Try to run query
            self._livy.run(f"_df = spark.sql(r'''{sql}''')")
            return self._livy.download("_df")
        except livy.models.SparkRuntimeError as err:
            # Catch "table does not exist" errors
            table = self._is_table_not_found_error(err)
            if not table:
                raise

        # Attempt to import dataset corresponding to missing table's name
        self._import_dataset(table)
        self._livy.run(f"_df = spark.sql(r'''{sql}''')")
        return self._livy.download("_df")

    def as_adbc(self):
        return RuntimeError(
            "Spark engine connection does not yet support ADBC client interface"
        )

    def __enter__(self):
        self._livy.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._livy.__exit__(exc_type, exc_value, traceback)

    def close(self):
        self._livy.close()

    def _is_table_not_found_error(self, err) -> str:
        if err.ename != "AnalysisException" or not err.evalue.startswith(
            "[TABLE_OR_VIEW_NOT_FOUND]"
        ):
            return None
        s = err.evalue.find("`")
        e = err.evalue.rfind("`")
        return err.evalue[s + 1 : e]

    def _import_dataset(self, name):
        self._livy.run(
            f"spark.read.parquet(resolve_dataset_ref('{name}')).createOrReplaceTempView('`{name}`')"
        )
