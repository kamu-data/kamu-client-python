import subprocess

import pandas
import pytest

import kamu
from kamu._connection_subprocess import KamuSqlServerProcess

from .conftest import Server


@pytest.fixture
def server_livy_st(workspace_st):
    proc = KamuSqlServerProcess(cwd=workspace_st.path, engine="spark")
    url = f"http://127.0.0.1:{proc.port()}"
    yield Server(port=proc.port(), url=url, workspace=workspace_st)
    proc.stop()


@pytest.fixture
def server_livy_mt(workspace_mt):
    proc = KamuSqlServerProcess(cwd=workspace_mt.path, engine="spark")
    url = f"http://127.0.0.1:{proc.port()}"
    yield Server(port=proc.port(), url=url, workspace=workspace_mt)
    proc.stop()


def pull_test_data(cwd, account=None):
    account = "" if not account else f"--account {account}"

    subprocess.run(
        f"kamu {account} pull odf+https://node.demo.kamu.dev/kamu/covid19.british-columbia.case-details.hm",
        cwd=cwd,
        shell=True,
        capture_output=True,
        check=True,
    )

    subprocess.run(
        f"kamu {account} pull odf+https://node.demo.kamu.dev/kamu/covid19.alberta.case-details.hm",
        cwd=cwd,
        shell=True,
        capture_output=True,
        check=True,
    )


def test_repr(server_livy_st):
    with kamu.connect(server_livy_st.url, engine="spark") as con:
        assert repr(con) == f"KamuConnectionLivy(url='{server_livy_st.url}')"


def test_url_scheme_check():
    with pytest.raises(ValueError):
        kamu.connect("grpc+tls://example.com", engine="spark")


def test_query_st(server_livy_st):
    pull_test_data(server_livy_st.workspace.path)

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
    pull_test_data(server_livy_mt.workspace.path, account="kamu")

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
