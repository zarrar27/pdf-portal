#!/usr/bin/env bash
# check-tools.sh — verifies that the tools this project needs are installed

set -euo pipefail

REQUIRED_TOOLS=("git" "brew" "python3" "code" "docker" )
MISSING=0

echo "Checking required tools..."

for tool in "${REQUIRED_TOOLS[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "  ✅ $tool found at $(command -v "$tool")"
  else
    echo "  ❌ $tool is NOT installed"
    MISSING=$((MISSING + 1))
  fi
done

if [ "$MISSING" -gt 0 ]; then
  echo "$MISSING tool(s) missing. Install them and run again."
  exit 1
fi

echo "All tools installed. Ready to go!"