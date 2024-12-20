import re

import adbc_driver_manager
import pandas
import pytest

import kamu


def test_version():
    assert re.fullmatch(
        r"\d\.\d\.\d", kamu.__version__
    ), "Version doesn't match the pattern"


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


def test_sql_query_pandas_interop(server_flightsql_mt):
    with kamu.connect(server_flightsql_mt.url) as con:
        actual = pandas.read_sql_query("select 1 as value", con.as_adbc())
        expected = pandas.DataFrame({"value": [1]})
        pandas.testing.assert_frame_equal(expected, actual)


def test_sql_query_datafusion(server_flightsql_mt):
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


def test_sql_query_spark_st(server_livy_st):
    with kamu.connect(server_livy_st.url, engine="spark") as con:
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
            from `covid19.british-columbia.case-details.hm`
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
                # TODO: should be int32
                "op": "int64",
                # TODO: should be datetime64[ms, UTC]
                "reported_date": "object",
                "id": "int64",
            }
        )

        pandas.testing.assert_frame_equal(expected, actual)


def test_sql_query_spark_mt(server_livy_mt):
    with kamu.connect(server_livy_mt.url, engine="spark") as con:
        actual = con.query(
            """
            select * from (
                (
                    select
                        offset,
                        op,
                        reported_date,
                        id,
                        gender
                    from `kamu/covid19.alberta.case-details.hm`
                    order by offset
                    limit 1
                )
                union all
                (
                    select
                        offset,
                        op,
                        reported_date,
                        id,
                        gender
                    from `kamu/covid19.british-columbia.case-details.hm`
                    order by offset
                    limit 1
                )
            )
            order by reported_date
            """
        )

        expected = pandas.DataFrame(
            {
                "offset": [0, 0],
                "op": [0, 0],
                "reported_date": [
                    "2020-01-29T00:00:00.000Z",
                    "2020-03-05T00:00:00.000Z",
                ],
                "id": [1, 505748],
                "gender": ["M", "F"],
            }
        ).astype(
            dtype={
                "offset": "int64",
                # TODO: should be int32
                "op": "int64",
                # TODO: should be datetime64[ms, UTC]
                "reported_date": "object",
                "id": "int64",
            }
        )

        pandas.testing.assert_frame_equal(expected, actual)


def test_sql_query_spark_gis_extensions(server_livy_mt):
    with kamu.connect(server_livy_mt.url, engine="spark") as con:
        actual = con.query(
            """
            select st_asgeojson(st_point(1, 2)) as point
            """
        )

        expected = pandas.DataFrame(
            {
                "point": ['{"type":"Point","coordinates":[1.0,2.0]}'],
            }
        )

        pandas.testing.assert_frame_equal(expected, actual)
