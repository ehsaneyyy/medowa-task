#!/usr/bin/env bash
set -o errexit

cd "$(dirname "$0")/backend"

exec bash ./build.sh
