import re

import adbc_driver_manager
import pandas
import pytest

import kamu


def test_version():
    assert re.fullmatch(
        r"\d\.\d\.\d", kamu.__version__
    ), "Version doesn't match the pattern"


def test_repr(server_flightsql_mt):
    with kamu.connect(server_flightsql_mt.url) as con:
        assert repr(con) == f"KamuConnectionFlightSql(url='{server_flightsql_mt.url}')"


def test_sql_query_minimal(server_flightsql_mt):
    with kamu.connect(server_flightsql_mt.url) as con:
        actual = con.query("select 1 as value")
        expected = pandas.DataFrame({"value": [1]})
        pandas.testing.assert_frame_equal(expected, actual)


def test_use_after_close(server_flightsql_mt):
    con = kamu.connect(server_flightsql_mt.url)
    actual = con.query("select 1 as value")
    expected = pandas.DataFrame({"value": [1]})
    pandas.testing.assert_frame_equal(expected, actual)
    con.close()
    with pytest.raises(adbc_driver_manager.ProgrammingError):
        con.query("select 1 as value")


def test_query_pandas_interop(server_flightsql_mt):
    with kamu.connect(server_flightsql_mt.url) as con:
        actual = pandas.read_sql_query("select 1 as value", con.as_adbc())
        expected = pandas.DataFrame({"value": [1]})
        pandas.testing.assert_frame_equal(expected, actual)


def test_query(server_flightsql_mt):
    with kamu.connect(server_flightsql_mt.url) as con:
        actual = con.query(
            """
            select
                offset,
                op,
                reported_date,
                id,
                gender,
                age_group,
                location
            from 'kamu/covid19.british-columbia.case-details.hm'
            order by offset
            limit 1
            """
        )

        expected = pandas.DataFrame(
            {
                "offset": [0],
                "op": [0],
                "reported_date": ["2020-01-29T00:00:00.000Z"],
                "id": [1],
                "gender": ["M"],
                "age_group": ["40s"],
                "location": ["Out of Canada"],
            }
        ).astype(
            dtype={
                "offset": "int64",
                "op": "int32",
                "reported_date": "datetime64[ms, UTC]",
                "id": "int64",
            }
        )

        pandas.testing.assert_frame_equal(expected, actual)
