#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
ZIP_PATH="$BUILD_DIR/nyx_telemetry_consumer.zip"

mkdir -p "$BUILD_DIR"

rm -f "$ZIP_PATH"

cd "$ROOT_DIR/src"

zip -r "$ZIP_PATH" cloud simulator >/dev/null

echo "CREATED LAMBDA PACKAGE: $ZIP_PATH"