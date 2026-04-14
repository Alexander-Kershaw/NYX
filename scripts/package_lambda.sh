#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build/lambda_package"
ZIP_PATH="$ROOT_DIR/build/nyx_lambda_consumer.zip"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
rm -f "$ZIP_PATH"

python -m pip install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --implementation cp \
  --python-version 3.11 \
  --target "$BUILD_DIR" \
  "pydantic>=2.0,<3.0"

cp -r "$ROOT_DIR/src/cloud" "$BUILD_DIR/"
cp -r "$ROOT_DIR/src/simulator" "$BUILD_DIR/"

cd "$BUILD_DIR"
zip -r "$ZIP_PATH" . >/dev/null

echo "Created Lambda package: $ZIP_PATH"