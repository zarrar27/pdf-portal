#!/usr/bin/env bash
# check-tools.sh — verifies that the tools this project needs are installed

set -euo pipefail

REQUIRED_TOOLS=("git" "brew" "python3" "code" "docker" "aws")
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

echo "Checking AWS credentials..."
if ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null); then
  echo "  ✅ Logged in to AWS account $ACCOUNT_ID (region: $(aws configure get region))"
else
  echo "  ❌ Not logged in to AWS. Run: aws login"
  exit 1
fi

echo "All checks passed. Ready to go!"