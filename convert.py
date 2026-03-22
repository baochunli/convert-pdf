import argparse
import contextlib
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

import opendataloader_pdf


DEFAULT_BACKEND_HOST = "127.0.0.1"
DEFAULT_BACKEND_STARTUP_TIMEOUT = 120.0
DEFAULT_HYBRID_TIMEOUT_MS = "180000"


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((DEFAULT_BACKEND_HOST, 0))
        return sock.getsockname()[1]


def _backend_health_url(port):
    return f"http://{DEFAULT_BACKEND_HOST}:{port}/health"


def _backend_url(port):
    return f"http://{DEFAULT_BACKEND_HOST}:{port}"


def _backend_command(port, enrich_formula):
    executable = shutil.which("opendataloader-pdf-hybrid")
    if executable:
        command = [executable]
    else:
        command = [sys.executable, "-m", "opendataloader_pdf.hybrid_server"]

    command.extend(["--host", DEFAULT_BACKEND_HOST, "--port", str(port)])
    if enrich_formula:
        command.append("--enrich-formula")
    return command


@contextlib.contextmanager
def managed_backend(enrich_formula, startup_timeout=DEFAULT_BACKEND_STARTUP_TIMEOUT):
    port = _find_free_port()
    health_url = _backend_health_url(port)
    command = _backend_command(port, enrich_formula)

    process = subprocess.Popen(command)
    try:
        deadline = time.monotonic() + startup_timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(
                    f"Hybrid backend exited during startup with code {process.returncode}."
                )
            try:
                with urlopen(health_url, timeout=1) as response:
                    if response.status == 200:
                        yield _backend_url(port)
                        break
            except URLError:
                pass
            time.sleep(0.5)
        else:
            raise TimeoutError(
                f"Timed out waiting for hybrid backend to start at {health_url}."
            )
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Convert one or more PDF files or folders with OpenDataLoader PDF."
    )
    parser.add_argument(
        "input_paths",
        nargs="+",
        help="PDF files and/or folders to convert.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./",
        help="Directory for converted output. Default: ./",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="markdown",
        help="Output format to generate. Default: markdown",
    )
    parser.add_argument(
        "--enrich-formula",
        action="store_true",
        default=True,
        help=(
            "Enable formula enrichment support. Default: on. Requires a hybrid "
            "backend started with formula enrichment."
        ),
    )
    parser.add_argument(
        "--no-enrich-formula",
        action="store_false",
        dest="enrich_formula",
        help="Disable formula enrichment support.",
    )
    parser.add_argument(
        "--hybrid-timeout",
        default=DEFAULT_HYBRID_TIMEOUT_MS,
        help="Hybrid backend timeout in milliseconds. Default: 180000.",
    )
    parser.add_argument(
        "--hybrid-fallback",
        action="store_true",
        default=True,
        help="Fall back to Java processing if the hybrid backend fails (default: on).",
    )
    parser.add_argument(
        "--no-hybrid-fallback",
        action="store_false",
        dest="hybrid_fallback",
        help="Disable Java fallback if the hybrid backend fails.",
    )
    parser.add_argument(
        "--backend-startup-timeout",
        type=float,
        default=DEFAULT_BACKEND_STARTUP_TIMEOUT,
        help=(
            "Seconds to wait for the auto-started hybrid backend to become healthy. "
            "Default: 120."
        ),
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    input_path = args.input_paths[0] if len(args.input_paths) == 1 else args.input_paths

    with managed_backend(
        enrich_formula=args.enrich_formula,
        startup_timeout=args.backend_startup_timeout,
    ) as hybrid_url:
        convert_kwargs = {
            "input_path": input_path,
            "output_dir": args.output_dir,
            "hybrid": "docling-fast",
            "hybrid_mode": "full",
            "hybrid_url": hybrid_url,
            "hybrid_timeout": args.hybrid_timeout,
            "format": args.format,
        }
        if args.hybrid_fallback:
            convert_kwargs["hybrid_fallback"] = True

        opendataloader_pdf.convert(**convert_kwargs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
