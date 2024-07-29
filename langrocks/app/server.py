import argparse
import logging
import subprocess
from concurrent import futures

import redis
from grpc import server as grpc_server
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from langrocks.common.display import VirtualDisplayPool
from langrocks.common.models.tools_pb2_grpc import add_ToolsServicer_to_server
from langrocks.tools.handler import ToolHandler

logger = logging.getLogger(__name__)


def _parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Langrocks server CLI")
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run the server on",
        default=50051,
    )
    parser.add_argument(
        "--host",
        type=str,
        help="Host to run the server on",
        default="0.0.0.0",
    )
    parser.add_argument(
        "--with-streaming-web-browser",
        type=bool,
        default=True,
        help="Enable streaming web browser with a display",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--max-displays",
        type=int,
        help="Maximum number of virtual displays to use",
        default=5,
    )
    parser.add_argument(
        "--start-display",
        type=int,
        help="Start display number number",
        default=99,
    )
    parser.add_argument(
        "--display-res",
        type=str,
        help="Display resolution for virtual displays to be used with browser",
        default="1024x720x24",
    )
    parser.add_argument(
        "--rfb-start-port",
        type=int,
        help="RFB start port",
        default=12000,
    )
    parser.add_argument(
        "--redis-host",
        type=str,
        help=argparse.SUPPRESS,
        default="localhost",
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        help=argparse.SUPPRESS,
        default=6379,
    )
    parser.add_argument(
        "--redis-db",
        type=int,
        help=argparse.SUPPRESS,
        default=0,
    )
    parser.add_argument(
        "--redis-password",
        type=str,
        help=argparse.SUPPRESS,
        default=None,
    )
    parser.add_argument(
        "--hostname",
        type=str,
        help=argparse.SUPPRESS,
        default="localhost",
    )
    parser.add_argument(
        "--wss-hostname",
        type=str,
        help="Hostname for remote browser websocket",
        default="localhost",
    )
    parser.add_argument(
        "--wss-port",
        type=int,
        help="Port for remote browser websocket",
        default=50052,
    )
    parser.add_argument(
        "--wss-secure",
        type=bool,
        default=False,
        help="Secure remote browser websocket",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--log-level",
        type=str,
        help="Log level",
        default="INFO",
    )
    return parser.parse_args()


def run_server(args, display_pool):
    """
    Run the Langrocks server. Depending on the arguments, it can run in different modes.
    """
    server = grpc_server(
        futures.ThreadPoolExecutor(
            max_workers=10,
            thread_name_prefix="grpc_workers",
        ),
    )

    tool_handler = ToolHandler(
        display_pool=display_pool,
        wss_secure=args.wss_secure,
        wss_hostname=args.wss_hostname,
        wss_port=args.wss_port,
    )

    add_ToolsServicer_to_server(tool_handler, server)

    # Add health checking service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    # Set the health status to SERVING
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

    server.add_insecure_port(f"[::]:{args.port}")
    server.start()

    logger.info(f"Server running at http://[::]:{args.port}")
    server.wait_for_termination()


def main():
    # Parse command line arguments
    args = _parse_args()

    # Configure logger
    logging.basicConfig(level=args.log_level)

    websockify_process = None
    display_pool = None

    # If streaming web browser is enabled, start the required services
    if args.with_streaming_web_browser:
        # Connect and verify redis
        redis_client = redis.Redis(
            host=args.redis_host,
            port=args.redis_port,
            db=args.redis_db,
            password=args.redis_password,
        )
        redis_client.ping()

        # Create virtual display pool
        display_pool = VirtualDisplayPool(
            redis_client,
            hostname=args.hostname,
            max_displays=args.max_displays,
            start_display=args.start_display,
            display_res=args.display_res,
            rfb_start_port=args.rfb_start_port,
        )

        # Start websockify server
        websockify_process = subprocess.Popen(
            [
                "websockify",
                f"{args.wss_port}",
                "--web",
                "/usr/share/www/html",
                "--token-plugin=langrocks.common.websockify.token.TokenRedis",
                f'--token-source={args.redis_host}:{args.redis_port}:{args.redis_db}{f":{args.redis_password}" if args.redis_password else ""}',
                "-v",
                "--auth-plugin=langrocks.common.websockify.auth.BasicHTTPAuthWithRedis",
                f'--auth-source={args.redis_host}:{args.redis_port}:{args.redis_db}{f":{args.redis_password}" if args.redis_password else ""}',
            ],
            close_fds=True,
        )

    # Run the server and block
    run_server(args, display_pool)

    # Stop websockify server and empty the display pool
    if websockify_process:
        websockify_process.kill()

    if display_pool:
        display_pool.stop()

    logger.info("Server stopped")


if __name__ == "__main__":
    main()
