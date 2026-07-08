#!/usr/bin/env bash
# claude-control installer (Linux + macOS)
# One shot, idempotent, non-destructive: existing skills are backed up, never overwritten silently.
# Usage: ./install.sh [--symlink] [--uninstall] [--skills-dir DIR]
set -u

# ---------- pretty printing ----------
BOLD=$(tput bold 2>/dev/null || true); DIM=$(tput dim 2>/dev/null || true); RESET=$(tput sgr0 2>/dev/null || true)
ok()   { printf "  [ OK ] %s\n" "$1"; }
skip() { printf "  [SKIP] %s\n" "$1"; }
warn() { printf "  [WARN] %s\n" "$1"; WARNINGS=$((WARNINGS+1)); }
fail() { printf "  [FAIL] %s\n" "$1"; FAILURES=$((FAILURES+1)); }

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CTRL_DIR="$HOME/.claude/claude-control"
MODE="copy"; ACTION="install"; WARNINGS=0; FAILURES=0
TS="$(date +%Y%m%d-%H%M%S)"

while [ $# -gt 0 ]; do
  case "$1" in
    --symlink) MODE="symlink" ;;
    --uninstall) ACTION="uninstall" ;;
    --skills-dir) shift; SKILLS_DIR="$1" ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1"; exit 1 ;;
  esac
  shift
done

echo "${BOLD}claude-control :: $ACTION${RESET}"
echo "  repo   : $REPO_DIR"
echo "  skills : $SKILLS_DIR"
echo "  tools  : $CTRL_DIR"
echo ""

# ---------- uninstall ----------
if [ "$ACTION" = "uninstall" ]; then
  for d in "$REPO_DIR"/skills/*/; do
    name="$(basename "$d")"
    t="$SKILLS_DIR/$name"
    if [ -L "$t" ] || [ -d "$t" ]; then rm -rf "$t"; ok "removed skill $name"; else skip "$name not installed"; fi
  done
  [ -d "$CTRL_DIR" ] && rm -rf "$CTRL_DIR" && ok "removed $CTRL_DIR"
  echo ""; echo "Uninstalled. Backups (if any) were left in ~/.claude/skills-backup-*"
  exit 0
fi

# ---------- sanity ----------
[ -d "$REPO_DIR/skills" ] || { fail "skills/ not found next to install.sh — corrupt download?"; exit 1; }
mkdir -p "$SKILLS_DIR" "$CTRL_DIR"

# ---------- 1. skills ----------
echo "${BOLD}1) Installing skills${RESET}"
BACKUP_DIR="$HOME/.claude/skills-backup-$TS"
for d in "$REPO_DIR"/skills/*/; do
  name="$(basename "$d")"
  src="${d%/}"
  target="$SKILLS_DIR/$name"
  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ "$(readlink "$target" 2>/dev/null)" = "$src" ]; then skip "$name already symlinked"; continue; fi
    if diff -rq "$src" "$target" >/dev/null 2>&1; then skip "$name already up to date"; continue; fi
    mkdir -p "$BACKUP_DIR"
    mv "$target" "$BACKUP_DIR/$name" && warn "$name existed — backed up to $BACKUP_DIR/$name"
  fi
  if [ "$MODE" = "symlink" ]; then
    ln -s "$src" "$target" && ok "linked  $name"
  else
    cp -R "$src" "$target" && ok "copied  $name"
  fi
done

# ---------- 2. tools + templates ----------
echo ""; echo "${BOLD}2) Installing tools${RESET}"
if [ "$MODE" = "symlink" ]; then
  rm -rf "$CTRL_DIR/tools" "$CTRL_DIR/templates"
  ln -sfn "$REPO_DIR/tools" "$CTRL_DIR/tools" && ok "linked tools/"
  ln -sfn "$REPO_DIR/templates" "$CTRL_DIR/templates" && ok "linked templates/"
else
  rm -rf "$CTRL_DIR/tools" "$CTRL_DIR/templates"
  cp -R "$REPO_DIR/tools" "$CTRL_DIR/tools" && ok "copied tools/"
  cp -R "$REPO_DIR/templates" "$CTRL_DIR/templates" && ok "copied templates/"
fi

# ---------- 3. skill manager ----------
echo ""; echo "${BOLD}3) Installing skill manager${RESET}"
rm -rf "$CTRL_DIR/skill-manager"
if [ "$MODE" = "symlink" ]; then
  ln -sfn "$REPO_DIR/skill-manager" "$CTRL_DIR/skill-manager" && ok "linked skill-manager/"
else
  cp -R "$REPO_DIR/skill-manager" "$CTRL_DIR/skill-manager" && ok "copied skill-manager/"
fi
mkdir -p "$CTRL_DIR/bin"
cat > "$CTRL_DIR/bin/skill-manager" <<LAUNCH
#!/usr/bin/env bash
exec python3 "$CTRL_DIR/skill-manager/server.py" "\$@"
LAUNCH
chmod +x "$CTRL_DIR/bin/skill-manager" && ok "launcher: $CTRL_DIR/bin/skill-manager"

# ---------- 4. dependency report ----------
echo ""; echo "${BOLD}4) Dependency check${RESET}  ${DIM}(nothing here blocks the install)${RESET}"
check() {
  if command -v "$1" >/dev/null 2>&1; then ok "$1 found — $2"
  else warn "$1 missing — $3"; fi
}
check python3 "tools + skill manager will run" "tools and skill manager need Python 3.9+ (https://python.org)"
check git     "version control ready"          "install git to clone/push this repo"
check node    "Claude Code runtime present"    "Claude Code needs Node 18+ (https://nodejs.org)"
check claude  "skills will load in Claude Code; chat backend ready" "install Claude Code: npm install -g @anthropic-ai/claude-code"
check docker  "/isolate sandbox available"     "/isolate needs Docker (or Podman) — optional"
check gh      "/design can enable Pages via API" "gh CLI is optional; /design falls back to manual steps"

# ---------- summary ----------
echo ""
echo "${BOLD}Done.${RESET}  warnings: $WARNINGS  failures: $FAILURES"
echo ""
echo "Next steps:"
echo "  * Restart Claude Code (or start it) — skills load from $SKILLS_DIR"
echo "  * Skill manager UI:   $CTRL_DIR/bin/skill-manager    then open http://127.0.0.1:8765"
echo "  * Per-project setup:  cp $CTRL_DIR/templates/CLAUDE.md <your-project>/CLAUDE.md"
echo "  * Optional PATH line (add yourself if you want 'skill-manager' everywhere):"
echo "      export PATH=\"\$PATH:$CTRL_DIR/bin\""
exit 0
