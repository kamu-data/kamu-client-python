import pathlib

import pandas
import pytest

import kamu


def test_repr(workspace_st):
    with kamu.connect(workspace_st.url) as con:
        assert (
            repr(con)
            == f"KamuConnectionSubprocess(url='{workspace_st.url}, inner={repr(con.inner_connection())}')"
        )


def test_sql_query_minimal_datafusion(workspace_st):
    with kamu.connect(workspace_st.url, engine="datafusion") as con:
        actual = con.query("select 1 as value")
        expected = pandas.DataFrame({"value": [1]})
        pandas.testing.assert_frame_equal(expected, actual)


def test_sql_query_minimal_spark(workspace_st):
    with kamu.connect(workspace_st.url, engine="spark") as con:
        actual = con.query("select 1 as value")
        expected = pandas.DataFrame({"value": [1]})
        pandas.testing.assert_frame_equal(expected, actual)


def test_error_cli_not_installed(workspace_st):
    with pytest.raises(FileNotFoundError, match="Kamu CLI binary 'kamu-zzz' not found"):
        kamu.connect(workspace_st.url, connection_params=dict(kamu_binary="kamu-zzz"))


def test_error_workspace_not_found(tempdir):
    url = pathlib.Path(tempdir).as_uri()
    with pytest.raises(FileNotFoundError, match="Kamu workspace not found at"):
        kamu.connect(url)
