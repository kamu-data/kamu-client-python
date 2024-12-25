import logging
import os
import socket
import subprocess
import tempfile
import time

from ._connection import KamuConnection

_logger = logging.getLogger(__package__)


class KamuConnectionSubprocess(KamuConnection):
    """
    This special `KamuConnection` implementation is created for `file://` URLs
    and will attempt to run local [`kamu-cli`](https://github.com/kamu-data/kamu-cli)
    binary to serve the data from local FS workspace.
    """

    def __init__(
        self,
        url,
        connection_factory,
        engine,
        kamu_binary="kamu",
        start_timeout=30,
        **connection_params,
    ):
        super().__init__()

        self._url = url

        assert url.startswith("file://")
        cwd = url[len("file://") :] or "."

        # Start and wait for subprocess
        self._proc = KamuSqlServerProcess(
            bin=kamu_binary, cwd=cwd, engine=engine, start_timeout=start_timeout
        )

        # Form new URL
        if engine == "spark":
            engine_url = f"http://localhost:{self._proc.port()}"
        else:
            engine_url = f"grpc://localhost:{self._proc.port()}"

        # Connect to subprocess
        try:
            self._con = connection_factory(
                url=engine_url, engine=engine, connection_params=connection_params
            )
        except Exception:
            self._proc.stop()
            raise

    def __repr__(self):
        return f"KamuConnectionSubprocess(url='{self._url}, inner={repr(self._con)}')"

    def url(self):
        return self._url

    def inner_connection(self) -> KamuConnection:
        return self._con

    def query(self, sql):
        return self._con.query(sql)

    def as_adbc(self):
        return self._con.as_adbc

    def __enter__(self):
        self._con.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._con.__exit__(exc_type, exc_value, traceback)
        self._proc.stop()

    def close(self):
        self._con.close()
        self._proc.stop()


class KamuSqlServerProcess:
    def __init__(self, bin="kamu", cwd=".", engine="datafusion", start_timeout=15):
        self._proc = None

        if not self.find_workspace(cwd):
            raise FileNotFoundError(f"Kamu workspace not found at {cwd}")

        self._port = self.find_free_port()

        stdout = self.get_temp_file("kamu-client-supbrocess-", ".stdout.txt")
        stderr = self.get_temp_file("kamu-client-supbrocess-", ".stderr.txt")

        cmd = [
            bin,
            "-v",
            "sql",
            "server",
            "--engine",
            engine,
            "--port",
            str(self._port),
        ]

        if engine == "spark":
            cmd.append("--livy")

        _logger.debug("Starting server", extra={"cmd": str(cmd)})

        try:
            self._proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                # shell=True,
                stdout=stdout,
                stderr=stderr,
                close_fds=True,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Kamu CLI binary '{bin}' not found. If the tool is installed consider specifying the full path"
            ) from e

        deadline = time.time() + start_timeout
        while True:
            try:
                status = self._proc.wait(1)
                raise Exception(
                    f"Kamu failed to start with status code: {status}\n"
                    f"See logs for details:\n"
                    f"- {stdout.name}\n"
                    f"- {stderr.name}"
                )
            except subprocess.TimeoutExpired:
                pass

            if self.is_port_open(self._port):
                break

            if time.time() >= deadline:
                self._proc.terminate()
                self._proc = None
                raise Exception(
                    f"Kamu failed to start within {start_timeout} seconds\n"
                    f"See logs for details:\n"
                    f"- {stdout.name}\n"
                    f"- {stderr.name}"
                )

    def port(self):
        return self._port

    def __del__(self):
        self.stop()

    def stop(self):
        if self._proc:
            self._proc.terminate()
            self._proc.wait()
            self._proc = None

    def find_workspace(self, cwd):
        current_path = os.path.abspath(cwd)

        # Stop when reaching the root directory
        while current_path != os.path.dirname(current_path):
            ws_path = os.path.join(current_path, ".kamu")
            if os.path.isdir(ws_path):
                return ws_path
            current_path = os.path.dirname(current_path)

        return None

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            free_port = s.getsockname()[1]
            return free_port

    def get_temp_file(self, prefix, extension):
        return tempfile.NamedTemporaryFile(
            prefix=prefix, suffix=extension, delete=False
        )

    def is_port_open(self, port):
        try:
            s = socket.create_connection(
                address=("127.0.0.1", port),
                timeout=0.1,
            )
        except socket.error:
            return False

        s.settimeout(1)

        try:
            read = s.recv(1)
        except TimeoutError:
            return True

        s.close()
        if len(read):
            return True

        return False
