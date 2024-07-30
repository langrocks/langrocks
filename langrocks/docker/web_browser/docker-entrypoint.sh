#!/bin/sh

set -e

# Start redis server if RUNNER_REDIS_HOST is not set or is set to localhost
if [ -z "$RUNNER_REDIS_HOST" ] || [ "$RUNNER_REDIS_HOST" = "localhost" ] || [ "$RUNNER_REDIS_HOST" = "127.0.0.1" ]; then
    echo "Starting redis server"
    redis-server --daemonize yes --protected-mode no
fi

if [ "x$ENABLE_PLAYWRIGHT_WS" != 'xoff' ]; then
    echo "Starting playwright server on port ${PLAYWRIGHT_WS_PORT:-50053}"
    playwright run-server --port ${PLAYWRIGHT_WS_PORT:-50053} &
fi


# Start langrocks server with web browser
echo "Starting langrocks server with web browser"
langrocks-server --with-streaming-web-browser --wss-hostname=${RUNNER_WSS_HOSTNAME:-localhost} --redis-host=${RUNNER_REDIS_HOST:-localhost}