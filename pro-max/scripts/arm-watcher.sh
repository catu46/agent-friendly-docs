#!/usr/bin/env bash
# arm-watcher.sh — arm the agent-friendly-docs reconciliation watcher on a tree.
#
# Agnostic: any local path (incl. a locally-synced SharePoint / OneDrive / Drive
# folder) or a git checkout, driven by ANY headless agent runner.
#
# Usage:  arm-watcher.sh <TARGET_DIR> [--runner "<cmd>"] [--cron "<expr>"] [--install]
# Defaults: --runner 'claude -p'   --cron '30 7 * * 1-5'   (07:30, weekdays)
# Examples:
#   arm-watcher.sh ~/SharePoint/ClientX
#   arm-watcher.sh ~/SharePoint/ClientX --runner "codex exec" --cron "0 * * * *" --install
set -euo pipefail

usage() {
  echo "usage: arm-watcher.sh <TARGET_DIR> [--runner \"<cmd>\"] [--cron \"<expr>\"] [--install]"
  echo "  --runner   headless agent command (default: 'claude -p'; e.g. 'codex exec', 'gemini -p')"
  echo "  --cron     cron schedule (default: '30 7 * * 1-5')"
  echo "  --install  write the line into your crontab (default: print only)"
}

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET=""; RUNNER="claude -p"; CRON="30 7 * * 1-5"; INSTALL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --runner) RUNNER="${2:?--runner needs a value}"; shift 2 ;;
    --cron)   CRON="${2:?--cron needs a value}"; shift 2 ;;
    --install) INSTALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "unknown option: $1" >&2; usage; exit 1 ;;
    *) TARGET="$1"; shift ;;
  esac
done
[ -n "$TARGET" ] || { usage; exit 1; }
[ -d "$TARGET" ] || { echo "not a directory: $TARGET" >&2; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"

mkdir -p "$TARGET/knowledge"
cp "$HERE/watcher-prompt.txt" "$TARGET/knowledge/watcher-prompt.txt"

LINE="$CRON  cd \"$TARGET\" && $RUNNER \"\$(cat knowledge/watcher-prompt.txt)\" >> knowledge/.watcher.log 2>&1"

echo "Prompt installed -> $TARGET/knowledge/watcher-prompt.txt"
echo "Runner          -> $RUNNER"
echo
echo "Cron line:"
echo "  $LINE"
echo

if [ "$INSTALL" -eq 1 ]; then
  TMP="$(mktemp)"
  crontab -l 2>/dev/null | grep -vF "cd \"$TARGET\" && " > "$TMP" || true
  echo "$LINE" >> "$TMP"
  crontab "$TMP"
  rm -f "$TMP"
  echo "Installed into crontab. Verify with: crontab -l"
else
  echo "Dry run — nothing installed. Re-run with --install, or paste the line via 'crontab -e'."
fi
