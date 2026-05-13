#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-codex}"

case "$TARGET" in
  claude)
    DEST=~/.claude/skills/
    ;;
  codex)
    DEST=~/.codex/skills/
    ;;
  -h|--help)
    echo "Usage: $0 [claude|codex]"
    echo "  claude  — rsync to ~/.claude/skills/"
    echo "  codex   — rsync to ~/.codex/skills/ (default)"
    exit 0
    ;;
  *)
    echo "Error: unknown target '$TARGET'. Use 'claude' or 'codex'." >&2
    exit 1
    ;;
esac

echo "Deploying datadata-api/ → $DEST"
rsync -avhP --no-perms --no-owner --no-group --delete ./datadata-api "$DEST"
