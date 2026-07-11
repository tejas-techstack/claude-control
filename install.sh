#!/usr/bin/env bash
# claude-control installer / updater (Linux + macOS)
# One shot, idempotent, non-destructive: existing skills are backed up, never overwritten silently.
# Re-running updates an existing install in place (tools/manager/templates are refreshed, changed skills re-copied).
# Usage: ./install.sh [--symlink] [--uninstall] [--skills-dir DIR]
#                     [--with-external] [--external NAME[,NAME...]]
#                     [--yes] [--no-input]
#   --with-external   also clone+install every source in skill-sources.txt (needs git)
#   --external LIST   only those named sources (comma-separated), implies --with-external
#   --yes, -y         answer "yes" to every prompt (install missing deps, add to PATH)
#   --no-input        never prompt; report only (good for CI / curl | bash)
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
EXTERNAL=""            # "" = none, "all" = every source, or a comma list of names
ASSUME_YES=0; NO_INPUT=0
TS="$(date +%Y%m%d-%H%M%S)"

usage() { sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --symlink) MODE="symlink" ;;
    --uninstall) ACTION="uninstall" ;;
    --skills-dir) shift; SKILLS_DIR="$1" ;;
    --with-external) EXTERNAL="all" ;;
    --external) shift; EXTERNAL="$1" ;;
    --yes|-y) ASSUME_YES=1 ;;
    --no-input) NO_INPUT=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown flag: $1"; exit 1 ;;
  esac
  shift
done

# ---------- interactivity ----------
# ask "question" -> 0 (yes) / 1 (no). --yes forces yes; --no-input or no TTY forces no.
ask() {
  [ "$ASSUME_YES" = "1" ] && return 0
  [ "$NO_INPUT" = "1" ] && return 1
  local reply=""
  if [ -t 0 ]; then
    read -r -p "  [ ?  ] $1 [y/N] " reply
  elif [ -r /dev/tty ]; then
    read -r -p "  [ ?  ] $1 [y/N] " reply </dev/tty
  else
    return 1   # non-interactive and no tty: default to no
  fi
  case "$reply" in [Yy]*) return 0 ;; *) return 1 ;; esac
}

# ---------- package manager detection (for --> installing missing deps) ----------
PM=""; PM_INSTALL=""
if command -v brew >/dev/null 2>&1; then PM="brew"; PM_INSTALL="brew install"
elif command -v apt-get >/dev/null 2>&1; then PM="apt"; PM_INSTALL="sudo apt-get install -y"
elif command -v dnf >/dev/null 2>&1; then PM="dnf"; PM_INSTALL="sudo dnf install -y"
elif command -v pacman >/dev/null 2>&1; then PM="pacman"; PM_INSTALL="sudo pacman -S --noconfirm"
elif command -v zypper >/dev/null 2>&1; then PM="zypper"; PM_INSTALL="sudo zypper install -y"
elif command -v apk >/dev/null 2>&1; then PM="apk"; PM_INSTALL="sudo apk add"
fi

# Map a generic dep name to this PM's package name(s).
pkg_for() {
  case "$1:$PM" in
    node:apt|node:apk|node:pacman) echo "nodejs npm" ;;
    node:*)       echo "nodejs" ;;
    python3:brew) echo "python" ;;
    python3:*)    echo "python3" ;;
    docker:apt)   echo "docker.io" ;;
    docker:*)     echo "docker" ;;
    *)            echo "$1" ;;
  esac
}

# dep_offer <cmd> <description> <install-command>
# If <cmd> is missing, offer to run <install-command>. Empty command => manual-only.
dep_offer() {
  local c="$1" d="$2" cmd="$3"
  if command -v "$c" >/dev/null 2>&1; then ok "$c found — $d"; return; fi
  warn "$c missing — $d"
  if [ -z "$cmd" ]; then skip "no auto-install for $c on this system; install it manually"; return; fi
  if ask "Install $c now?  ($cmd)"; then
    echo "     \$ $cmd"
    if eval "$cmd"; then ok "installed $c"; else fail "install failed for $c — install it manually"; fi
  else
    skip "$c left uninstalled"
  fi
}

echo "${BOLD}claude-control :: $ACTION${RESET}"
echo "  repo   : $REPO_DIR"
echo "  skills : $SKILLS_DIR"
echo "  tools  : $CTRL_DIR"
[ -d "$CTRL_DIR/tools" ] && [ "$ACTION" = "install" ] && echo "  ${DIM}(existing install detected — this run will UPDATE it in place)${RESET}"
echo ""

# ---------- uninstall ----------
if [ "$ACTION" = "uninstall" ]; then
  if command -v python3 >/dev/null 2>&1 && [ -f "$CTRL_DIR/tools/skillsource.py" ]; then
    python3 "$CTRL_DIR/tools/skillsource.py" --skills-dir "$SKILLS_DIR" --ctrl-dir "$CTRL_DIR" \
      remove all >/dev/null 2>&1 && ok "removed external (gstack/etc.) skills"
  fi
  for d in "$REPO_DIR"/skills/*/; do
    name="$(basename "$d")"
    t="$SKILLS_DIR/$name"
    if [ -L "$t" ] || [ -d "$t" ]; then rm -rf "$t"; ok "removed skill $name"; else skip "$name not installed"; fi
  done
  [ -d "$CTRL_DIR" ] && rm -rf "$CTRL_DIR" && ok "removed $CTRL_DIR (incl. external/ clones)"
  echo ""; echo "Uninstalled. Backups (if any) were left in ~/.claude/skills-backup-*"
  echo "Note: graphify (if you installed it) is a separate pip package — remove with: pip uninstall graphifyy"
  echo "      any PATH line added to your shell rc was left in place; remove it by hand if you like."
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
    mv "$target" "$BACKUP_DIR/$name" && warn "$name changed — old copy backed up to $BACKUP_DIR/$name"
  fi
  if [ "$MODE" = "symlink" ]; then
    ln -s "$src" "$target" && ok "linked  $name"
  else
    cp -R "$src" "$target" && ok "copied  $name"
  fi
done

# ---------- 2. tools + templates + skill-sources manifest ----------
echo ""; echo "${BOLD}2) Installing tools${RESET}  ${DIM}(refreshed every run so updates land)${RESET}"
if [ "$MODE" = "symlink" ]; then
  rm -rf "$CTRL_DIR/tools" "$CTRL_DIR/templates"
  ln -sfn "$REPO_DIR/tools" "$CTRL_DIR/tools" && ok "linked tools/"
  ln -sfn "$REPO_DIR/templates" "$CTRL_DIR/templates" && ok "linked templates/"
  ln -sfn "$REPO_DIR/skill-sources.txt" "$CTRL_DIR/skill-sources.txt" && ok "linked skill-sources.txt"
else
  rm -rf "$CTRL_DIR/tools" "$CTRL_DIR/templates"
  cp -R "$REPO_DIR/tools" "$CTRL_DIR/tools" && ok "copied tools/"
  cp -R "$REPO_DIR/templates" "$CTRL_DIR/templates" && ok "copied templates/"
  # Don't clobber a manifest the user has edited; seed it once.
  if [ -f "$CTRL_DIR/skill-sources.txt" ]; then skip "skill-sources.txt kept (yours)"
  else cp "$REPO_DIR/skill-sources.txt" "$CTRL_DIR/skill-sources.txt" && ok "copied skill-sources.txt"; fi
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

# ---------- 3b. external skill sources (opt-in) ----------
echo ""; echo "${BOLD}3b) External skill sources${RESET}  ${DIM}(gstack, anthropic-skills, ...)${RESET}"
if [ -z "$EXTERNAL" ]; then
  skip "not fetched — re-run with --with-external, or use the skill manager's Sources panel"
elif ! command -v python3 >/dev/null 2>&1; then
  warn "skipped external skills: python3 not found"
elif ! command -v git >/dev/null 2>&1; then
  warn "skipped external skills: git not found"
else
  emode="symlink"; [ "$MODE" = "copy" ] && emode="copy"
  targets="all"; [ "$EXTERNAL" != "all" ] && targets="$(echo "$EXTERNAL" | tr ',' ' ')"
  for t in $targets; do
    python3 "$CTRL_DIR/tools/skillsource.py" --manifest "$CTRL_DIR/skill-sources.txt" \
      --skills-dir "$SKILLS_DIR" --ctrl-dir "$CTRL_DIR" --mode "$emode" sync "$t" \
      && ok "synced source: $t" || warn "sync had issues for: $t"
  done
fi

# ---------- 4. dependencies (interactive) ----------
echo ""; echo "${BOLD}4) Dependencies${RESET}  ${DIM}(missing ones are offered for install; nothing here blocks the install)${RESET}"
if [ -z "$PM" ] && [ "$NO_INPUT" != 1 ]; then
  warn "no supported package manager found (brew/apt/dnf/pacman/zypper/apk) — deps will be report-only"
fi
dep_offer python3 "tools + skill manager need Python 3.9+"  "${PM_INSTALL:+$PM_INSTALL $(pkg_for python3)}"
dep_offer git     "clone/update this repo and skill sources" "${PM_INSTALL:+$PM_INSTALL $(pkg_for git)}"
dep_offer node    "Claude Code runtime (Node 18+)"          "${PM_INSTALL:+$PM_INSTALL $(pkg_for node)}"

# claude CLI comes from npm, not the system package manager.
if command -v claude >/dev/null 2>&1; then
  ok "claude found — skills load in Claude Code; chat backend ready"
elif command -v npm >/dev/null 2>&1; then
  dep_offer claude "the Claude Code CLI" "npm install -g @anthropic-ai/claude-code"
else
  warn "claude missing — install Node first, then: npm install -g @anthropic-ai/claude-code"
fi

# graphify: the /graphify skill (deep dependency/knowledge graph). pip package, ships its own skill.
graphify_present() {
  command -v graphify >/dev/null 2>&1 || [ -f "$SKILLS_DIR/graphify/SKILL.md" ] || [ -f "$HOME/.claude/skills/graphify/SKILL.md" ]
}
PIP=""
if command -v pip3 >/dev/null 2>&1; then PIP="pip3"
elif command -v pip >/dev/null 2>&1; then PIP="pip"
elif command -v python3 >/dev/null 2>&1; then PIP="python3 -m pip"; fi
if graphify_present; then
  ok "graphify skill present — use /graphify . for a deep dependency graph"
  if [ -n "$PIP" ] && ask "Update graphify to the latest version?"; then
    eval "$PIP install --upgrade graphifyy" && ok "graphify updated" || warn "graphify update had issues"
  fi
else
  warn "graphify skill missing — deep dependency/knowledge graph (/graphify .), replaces the old graphify.py"
  if [ -z "$PIP" ]; then
    skip "need Python 3.10+/pip to install graphify — see https://github.com/safishamsi/graphify"
  elif ask "Install graphify now?  ($PIP install graphifyy && graphify install)"; then
    echo "     \$ $PIP install graphifyy"
    if eval "$PIP install graphifyy" || eval "$PIP install --user graphifyy"; then
      if command -v graphify >/dev/null 2>&1; then
        graphify install && ok "installed graphify — invoke it with /graphify . in Claude Code" \
          || warn "'graphify install' failed — run it manually once graphify is on PATH"
      else
        warn "graphify pip package installed but the 'graphify' command isn't on PATH."
        warn "add pip's bin dir to PATH (e.g. ~/.local/bin), then run: graphify install"
      fi
    else
      warn "pip install failed (externally-managed Python?). Try: pipx install graphifyy && graphify install"
    fi
  else
    skip "graphify left uninstalled — later: $PIP install graphifyy && graphify install"
  fi
fi

# optional tools
dep_offer docker "/isolate sandbox (optional)"          "${PM_INSTALL:+$PM_INSTALL $(pkg_for docker)}"
dep_offer gh     "/design can enable Pages via API (optional)" "${PM_INSTALL:+$PM_INSTALL $(pkg_for gh)}"

# ---------- 5. PATH (interactive) ----------
echo ""; echo "${BOLD}5) PATH${RESET}  ${DIM}(so 'skill-manager' works from any directory)${RESET}"
BIN_DIR="$CTRL_DIR/bin"
case ":${PATH}:" in
  *":$BIN_DIR:"*) skip "$BIN_DIR already on PATH" ;;
  *)
    # Pick the right rc file for the user's login shell.
    shell_name="$(basename "${SHELL:-sh}")"
    case "$shell_name" in
      zsh)  RC="$HOME/.zshrc" ;;
      bash) if [ "$(uname)" = "Darwin" ]; then RC="$HOME/.bash_profile"; else RC="$HOME/.bashrc"; fi ;;
      fish) RC="$HOME/.config/fish/config.fish" ;;
      *)    RC="$HOME/.profile" ;;
    esac
    if [ "$shell_name" = "fish" ]; then
      PATH_LINE="fish_add_path $BIN_DIR"
    else
      PATH_LINE="export PATH=\"\$PATH:$BIN_DIR\""
    fi
    if [ -f "$RC" ] && grep -qF "$BIN_DIR" "$RC" 2>/dev/null; then
      skip "PATH entry already present in $RC"
    elif ask "Add $BIN_DIR to your PATH in $RC?"; then
      mkdir -p "$(dirname "$RC")"
      printf '\n# added by claude-control installer (%s)\n%s\n' "$TS" "$PATH_LINE" >> "$RC" \
        && ok "added to $RC — run 'source $RC' or open a new terminal to pick it up"
    else
      skip "PATH not modified — add this yourself if you want it: $PATH_LINE"
    fi
    ;;
esac

# ---------- summary ----------
echo ""
echo "${BOLD}Done.${RESET}  warnings: $WARNINGS  failures: $FAILURES"
echo ""
echo "Next steps:"
echo "  * Restart Claude Code (or start it) — skills load from $SKILLS_DIR"
echo "  * Skill manager UI:   $CTRL_DIR/bin/skill-manager    then open http://127.0.0.1:8765"
echo "  * Per-project setup:  cp $CTRL_DIR/templates/CLAUDE.md <your-project>/CLAUDE.md"
echo "  * Deep repo graphs:   /graphify .   (install offered above; upstream: https://github.com/safishamsi/graphify)"
if [ -z "$EXTERNAL" ]; then
echo "  * Add more skills:    ./install.sh --with-external   (gstack + anthropic-skills)"
echo "                        or: python3 $CTRL_DIR/tools/skillsource.py sync all"
fi
echo "  * Re-run anytime:     ./install.sh   updates tools, manager, and changed skills in place"
exit 0
