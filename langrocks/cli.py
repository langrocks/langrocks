import argparse
import os
import platform
import random
import re
import signal
import sys
import tempfile
import time

import requests
from python_on_whales import DockerClient


def stop(exit_code=0):
    """Stop Langrocks server"""
    print("Stopping Langrocks server...")
    docker_client = DockerClient(
        compose_project_name="langrocks",
    )
    docker_client.compose.down()
    sys.exit(exit_code)


def wait_for_server(langrocks_environment, timeout):
    """Wait for server to be up and open browser"""

    start_time = time.time()
    while True:
        try:
            print(
                "\nWaiting for Langrocks server to be up...",
                end="",
            )
            resp = requests.get(
                f'http://{langrocks_environment["LANGROCKS_HOST"]}:{langrocks_environment["LANGROCKS_PORT"]}',
            )
            if resp.status_code < 400:
                break

            time.sleep(2 + (random.randint(0, 1000) / 1000))

            # If we have waited for more than 3 minutes, exit
            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for Langrocks server to be up.")
        except TimeoutError:
            print(
                "\nFailed to connect to Langrocks server. Exiting...",
            )
            print_compose_logs(follow=False)
            stop(1)
        except Exception:
            time.sleep(2 + (random.randint(0, 1000) / 1000))
            continue

    print(
        f"Langrocks server is running at http://{langrocks_environment['LANGROCKS_HOST']}:{langrocks_environment['LANGROCKS_PORT']}"
    )


def print_compose_logs(follow=True, stream=True):
    """Get logs for Langrocks server"""
    docker_client = DockerClient(
        compose_project_name="langrocks",
    )

    if not docker_client.compose.ps():
        print("Langrocks server is not running.")
        sys.exit(0)

    logs = docker_client.compose.logs(follow=follow, stream=stream)
    for _, line in logs:
        print(line.decode("utf-8").strip())


def start(langrocks_environment):
    # Create a temp file with this environment variables to be used by docker-compose
    with tempfile.NamedTemporaryFile(mode="w") as f:
        for key in langrocks_environment:
            f.write(f"{key}={langrocks_environment[key]}\n")
        f.flush()

        # Start the containers
        docker_client = DockerClient(
            compose_files=[os.path.join(os.path.dirname(__file__), "docker-compose.yml")],
            compose_env_file=f.name,
        )

        # Start the containers
        docker_logs = docker_client.compose.up(detach=True, stream_logs=True, pull="missing")

        compose_output = []
        last_output_len = 0
        for _, line in docker_logs:
            output = line.decode("utf-8").strip()

            # If the output has a hash "26f9b446db9e Extracting  450.1MB/523.6M", replace in compose output
            if len(output.split(" ")) > 1:
                output_part = output.split(" ")[0]
                if len(output_part) == 12 and re.fullmatch(r"[0-9a-f]+", output_part):
                    for i, compose_output_part in enumerate(compose_output):
                        if output_part in compose_output_part:
                            compose_output.pop(i)
                            compose_output.append(output)

            # If the output is not already in compose_output, add it
            if output not in compose_output:
                compose_output.append(output)

            # Clear the previous output
            for _ in range(last_output_len - 1):
                print("\033[F\033[K", end="")

            print("\n".join(compose_output[-10:]), end="", flush=True)
            last_output_len = len(compose_output[-10:])


def main():
    """Main entry point for the application script"""

    def signal_handler(sig, frame):
        stop()

    # Setup CLI args
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--host", default="localhost", help="Host to bind to. Defaults to localhost.")
    parent_parser.add_argument("--port", default=3000, help="Port to bind to. Defaults to 3000.")
    parent_parser.add_argument("--quiet", default=False, action="store_true", help="Suppress output.")
    parent_parser.add_argument("--detach", default=False, action="store_true", help="Run in detached mode.")
    parent_parser.add_argument("--timeout", default=180, help=argparse.SUPPRESS)
    parent_parser.add_argument(
        "--registry",
        default="ghcr.io/langrocks/",
        help=argparse.SUPPRESS,
    )
    parent_parser.add_argument("--tag", default="v0.2.2", help=argparse.SUPPRESS)

    parser = argparse.ArgumentParser(description="Langrocks: A collection of tools for LLMs", parents=[parent_parser])
    subparsers = parser.add_subparsers(title="commands", help="Available commands", dest="command")

    subparsers.add_parser("start", help="Start Langrocks server", parents=[parent_parser])
    subparsers.add_parser("stop", help="Stop Langrocks server")
    subparsers.add_parser("logs", help="Get logs for Langrocks server")

    # Load CLI args
    args = parser.parse_args()

    if args.command == "stop":
        stop()
        return

    # Start the containers
    langrocks_environment = {}
    if not args.command or args.command == "start":
        if args.host is not None:
            langrocks_environment["LANGROCKS_HOST"] = args.host

        if args.port is not None:
            langrocks_environment["LANGROCKS_PORT"] = args.port
            os.environ["LANGROCKS_PORT"] = str(args.port)

        # Set registry and tag
        langrocks_environment["REGISTRY"] = args.registry

        if args.tag:
            langrocks_environment["TAG"] = args.tag

        start(langrocks_environment)

        print(
            f"\n\nLangrocks server is running at {langrocks_environment['LANGROCKS_HOST']}:{langrocks_environment['LANGROCKS_PORT']}."
        )

        # If running in detached mode, return
        if args.detach:
            print("Running in detached mode. Use `langrocks stop` to stop the server.")
            return

        print("Press Ctrl+C to stop the server.")

    # Register the signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    if not args.quiet or args.command == "logs":
        print_compose_logs()

    # Block the main thread until a signal is received
    if "windows" in platform.platform().lower():
        os.system("pause")
    else:
        signal.pause()

    # Stop the containers
    stop()


if __name__ == "__main__":
    main()
