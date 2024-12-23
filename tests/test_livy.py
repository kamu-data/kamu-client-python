import re

import adbc_driver_manager
import pandas
import pytest

import kamu


def test_repr(server_livy_st):
    with kamu.connect(server_livy_st.url, engine="spark") as con:
        assert repr(con) == f"KamuConnectionLivy(url='{server_livy_st.url}')"


def test_query_st(server_livy_st):
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


def test_query_mt(server_livy_mt):
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


def test_query_gis_extensions(server_livy_mt):
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
