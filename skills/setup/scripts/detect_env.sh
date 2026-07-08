#!/usr/bin/env bash
# detect_env.sh — one-shot environment probe for /setup. Prints OS, arch, package
# managers, shells, and versions of common toolchains, so setup plans install steps
# against what's actually here instead of guessing. Read-only; installs nothing.
# Usage: bash detect_env.sh   (works on Linux, macOS, and Git Bash/WSL on Windows)
set -u

line() { printf '%s\n' "----------------------------------------"; }
have() { command -v "$1" >/dev/null 2>&1; }
ver()  { have "$1" && printf "  %-12s %s\n" "$1" "$("$@" 2>&1 | head -1)" || printf "  %-12s (absent)\n" "$1"; }

echo "== system =="
echo "  os      : $(uname -s)  kernel $(uname -r 2>/dev/null)"
echo "  arch    : $(uname -m)"
if [ -r /etc/os-release ]; then . /etc/os-release; echo "  distro  : ${PRETTY_NAME:-unknown}"; fi
if [ "$(uname -s)" = "Darwin" ]; then echo "  macos   : $(sw_vers -productVersion 2>/dev/null)"; fi
echo "  shell   : ${SHELL:-?}   user: $(id -un 2>/dev/null)   home: $HOME"
echo "  sudo    : $(have sudo && echo available || echo 'not found (user-space installs only)')"

line; echo "== package managers (install route) =="
for pm in apt apt-get dnf yum pacman zypper apk brew port snap flatpak nix pipx npm pip pip3 cargo go gem; do
  have "$pm" && printf "  %-10s yes\n" "$pm"
done

line; echo "== language toolchains =="
ver python3 --version
ver node --version
ver deno --version
ver bun --version
ver go version
ver rustc --version
ver java -version
ver ruby --version
ver php --version
ver gcc --version

line; echo "== containers / vcs / cloud =="
ver docker --version
ver podman --version
ver git --version
ver gh --version
ver make --version

line; echo "== notes for /setup =="
have sudo || echo "  * no sudo — prefer pipx, npm --prefix ~/.local, ~/.local/bin, official user installers."
have brew && echo "  * Homebrew present — 'brew install X' is the fast path here."
have apt && echo "  * Debian/Ubuntu — 'sudo apt-get install -y X' (apt-get update first). Consent required for sudo."
have dnf && echo "  * Fedora/RHEL — 'sudo dnf install -y X'."
have pacman && echo "  * Arch — 'sudo pacman -S --noconfirm X'."
{ have docker || have podman; } || echo "  * no container runtime — /isolate needs one; install Docker/Podman if sandboxing is wanted."
echo "  * Always verify each install with the REAL command (e.g. 'docker run hello-world'), not just --version."
