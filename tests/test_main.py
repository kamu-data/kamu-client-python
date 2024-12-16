import re

import pandas

import kamu


def test_version():
    assert re.fullmatch(
        r"\d\.\d\.\d", kamu.__version__
    ), "Version doesn't match the pattern"


def test_sql_query_minimal(container_mt):
    with kamu.connect(container_mt.url) as con:
        actual = pandas.read_sql_query("select 1 as value", con.as_adbc())
        expected = pandas.DataFrame({"value": [1]})
        pandas.testing.assert_frame_equal(expected, actual)


def test_sql_query_dataset(container_mt):
    with kamu.connect(container_mt.url) as con:
        actual = pandas.read_sql_query(
            r"""
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
            """,
            con.as_adbc(),
        )

        expected = pandas.DataFrame(
            {
                "offset": [0],
                "op": [0],
                "reported_date": ["2020-01-29T00:00:00Z"],
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
