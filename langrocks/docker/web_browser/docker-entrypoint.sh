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

# Handle uBlock installation if enabled
UBLOCK_FLAG=""
ENABLE_UBLOCK=${ENABLE_UBLOCK:-true}
if [ "x$ENABLE_UBLOCK" = 'xtrue' ]; then
    echo "Setting up uBlock Origin..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    
    # Download latest uBlock release
    if ! wget -q "https://github.com/gorhill/uBlock/releases/download/1.60.0/uBlock0_1.60.0.chromium.zip" -O "$TEMP_DIR/ublock.zip"; then
        echo "Warning: Failed to download uBlock Origin"
    else
        # Extract the extension
        if ! unzip -q "$TEMP_DIR/ublock.zip" -d "$TEMP_DIR/ublock"; then
            echo "Warning: Failed to extract uBlock Origin"
        else
            UBLOCK_FLAG="--ublock-path=$TEMP_DIR/ublock/uBlock0.chromium"
            echo "Successfully prepared uBlock Origin"
        fi
    fi
fi

WSS_SECURE_FLAG="--no-wss-secure"
if [ "$RUNNER_WSS_SECURE" = "true" ]; then
  WSS_SECURE_FLAG="--wss-secure"
fi

exec langrocks-server \
  --with-streaming-web-browser \
  --wss-hostname="${RUNNER_WSS_HOSTNAME:-localhost}" \
  --redis-host="${RUNNER_REDIS_HOST:-localhost}" \
  --redis-port="${RUNNER_REDIS_PORT:-6379}" \
  --redis-db="${RUNNER_REDIS_DB:-0}" \
  --wss-port="${RUNNER_WSS_PORT:-50052}" \
  --port="${RUNNER_PORT:-50051}" \
  $WSS_SECURE_FLAG \
  $UBLOCK_FLAG