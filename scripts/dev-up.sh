#!/usr/bin/env bash
# dev-up.sh — start the local stack with fresh temporary AWS credentials

set -euo pipefail

cd "$(dirname "$0")/.."

if ! aws sts get-caller-identity >/dev/null 2>&1; then
  echo "Not logged in to AWS. Run: aws login" >&2
  exit 1
fi

eval "$(aws configure export-credentials --format env)"
: "${AWS_SESSION_TOKEN:?Could not get temporary AWS credentials. Run: aws login}"

exec docker compose up --build "$@"
