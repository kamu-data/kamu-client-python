import socket
import time
from dataclasses import dataclass

import docker
import pytest


@dataclass
class KamuContainer:
    port: int
    url: str

    def wait_for_port(self):
        while True:
            try:
                s = socket.create_connection(
                    address=("localhost", self.port),
                    timeout=0.1,
                )
            except Exception:
                time.sleep(0.1)
                continue

            s.settimeout(1)
            read = s.recv(1)
            s.close()

            if len(read):
                break

            time.sleep(0.1)


@pytest.fixture(scope="module")
def container_mt():
    client = docker.from_env()

    container = client.containers.run(
        image="ghcr.io/kamu-data/kamu-base:latest-with-data-mt",
        command="kamu -vv sql server --flight-sql --address 0.0.0.0 --port 50050",
        auto_remove=True,
        remove=True,
        ports={"50050/tcp": None},
        detach=True,
    )

    container.reload()
    port = container.ports["50050/tcp"][0]["HostPort"]

    kamu_container = KamuContainer(port=port, url=f"grpc://localhost:{port}")
    kamu_container.wait_for_port()
    yield kamu_container

    container.kill()
