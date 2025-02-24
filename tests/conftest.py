import os
import pathlib
import subprocess
import tempfile
from dataclasses import dataclass
from textwrap import dedent

import pytest


@dataclass
class Workspace:
    path: str
    url: str


@dataclass
class Server:
    port: int
    url: str
    workspace: Workspace


@pytest.fixture
def tempdir():
    d = tempfile.TemporaryDirectory("kamu-client-test-", delete=True)
    yield d.name


@pytest.fixture
def workspace_st(tempdir):
    subprocess.run(
        "kamu init", cwd=tempdir, shell=True, capture_output=True, check=True
    )
    yield Workspace(path=tempdir, url=pathlib.Path(tempdir).as_uri())


@pytest.fixture
def workspace_mt(tempdir):
    subprocess.run(
        "kamu init --multi-tenant",
        cwd=tempdir,
        shell=True,
        capture_output=True,
        check=True,
    )
    with open(os.path.join(tempdir, ".kamu", ".kamuconfig"), "w") as f:
        f.write(
            dedent(
                """
                kind: CLIConfig
                version: 1
                content:
                  users:
                    predefined:
                      - accountName: kamu
                        isAdmin: true
                        avatarUrl: https://avatars.githubusercontent.com/u/50896974?s=200&v=4
                        email: support+kamu@kamu.dev
                """
            )
        )
    yield Workspace(path=tempdir, url=pathlib.Path(tempdir).as_uri())
