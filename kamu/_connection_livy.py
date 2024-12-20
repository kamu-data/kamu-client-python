import logging
import os
import re

import livy

from ._connection import KamuConnection

_logger = logging.getLogger(__package__)


def _maybe_int(value):
    if value:
        return int(value)
    return None


LIVY_DEFAULT_SESSION_PARAMS = {
    "executor_cores": _maybe_int(os.environ.get("KAMU_CLIENT_LIVY_EXECUTOR_CORES")),
    "executor_memory": os.environ.get("KAMU_CLIENT_LIVY_EXECUTOR_MEMORY"),
    "driver_cores": _maybe_int(os.environ.get("KAMU_CLIENT_LIVY_DRIVER_CORES")),
    "driver_memory": os.environ.get("KAMU_CLIENT_LIVY_DRIVER_MEMORY"),
    "heartbeat_timeout": _maybe_int(
        os.environ.get("KAMU_CLIENT_LIVY_HEARTBEAT_TIMEOUT")
    ),
}

UNRESOLVED_TABLE_RE = re.compile(r"UnresolvedRelation \[([^\]]+)\],")

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

    def __init__(self, url, auto_import_datasets=True, **livy_session_params):
        super().__init__()

        self._auto_import_datasets = auto_import_datasets

        livy_session_params_final = dict(LIVY_DEFAULT_SESSION_PARAMS)
        livy_session_params_final.update(livy_session_params)

        _logger.debug(
            "Creating Livy connection",
            extra={"url": url, "livy_session_params": livy_session_params_final},
        )

        self._url = url
        self._livy = livy.LivySession.create(self._url, **livy_session_params_final)
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
            if not self._auto_import_datasets or not self._is_table_not_found_error(
                err
            ):
                raise
            datasets = self._parse_unresolved_tables(err)

        # Attempt to import dataset corresponding to missing table names
        _logger.debug(
            "Attempt to import dataset corresponding to missing table names",
            extra={"datasets": datasets},
        )

        for dataset in datasets:
            self._import_dataset(dataset)

        # Re-run the original query
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

    def _is_table_not_found_error(self, err):
        return (
            err.ename == "AnalysisException"
            and "[TABLE_OR_VIEW_NOT_FOUND]" in err.evalue
        )

    def _parse_unresolved_tables(self, err):
        return [m.group(1) for m in UNRESOLVED_TABLE_RE.finditer(err.evalue)]

    def _import_dataset(self, name):
        self._livy.run(
            f"spark.read.parquet(resolve_dataset_ref('{name}')).createOrReplaceTempView('`{name}`')"
        )
