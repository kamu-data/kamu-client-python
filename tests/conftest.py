import socket
import time
from dataclasses import dataclass

import docker
import pytest


@dataclass
class Server:
    port: int
    url: str

    def wait_for_port(self):
        while True:
            try:
                s = socket.create_connection(
                    address=("127.0.0.1", self.port),
                    timeout=0.1,
                )
            except Exception:
                time.sleep(0.1)
                continue

            s.settimeout(1)

            try:
                read = s.recv(1)
            except TimeoutError:
                break

            s.close()

            if len(read):
                break

            time.sleep(0.1)


@pytest.fixture(scope="module")
def docker_client():
    return docker.from_env()


@pytest.fixture(scope="module")
def server_flightsql_mt(docker_client):
    container = docker_client.containers.run(
        image="ghcr.io/kamu-data/kamu-base:latest-with-data-mt",
        command="kamu -vv sql server --flight-sql --address 0.0.0.0 --port 50050",
        auto_remove=True,
        remove=True,
        ports={"50050/tcp": None},
        detach=True,
    )

    container.reload()
    port = container.ports["50050/tcp"][0]["HostPort"]

    server = Server(port=port, url=f"grpc://127.0.0.1:{port}")
    server.wait_for_port()
    yield server

    container.kill()


@pytest.fixture(scope="module")
def server_livy_st():
    import subprocess

    port = 50050

    proc = subprocess.Popen(
        f"kamu -vv sql server --livy --port {port}",
        shell=True,
        cwd="../kamu-cli/examples/covid",
    )

    server = Server(port=port, url=f"http://127.0.0.1:{port}")
    server.wait_for_port()
    yield server

    proc.terminate()
    proc.wait()


@pytest.fixture(scope="module")
def server_livy_mt():
    import subprocess

    port = 50051

    # proc = subprocess.Popen(
    #     f"kamu -vv sql server --livy --port {port}",
    #     shell=True,
    #     cwd="../kamu-cli/examples/covid-mt",
    # )

    server = Server(port=port, url=f"http://127.0.0.1:{port}")
    # server.wait_for_port()
    yield server

    # proc.terminate()
    # proc.wait()
