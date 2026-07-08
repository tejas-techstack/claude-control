# claude-control installer (Windows PowerShell 5.1+ / PowerShell 7)
# One shot, idempotent, non-destructive: existing skills are backed up, never overwritten silently.
# Usage:  powershell -ExecutionPolicy Bypass -File install.ps1 [-Symlink] [-Uninstall] [-SkillsDir DIR]
param(
    [switch]$Symlink,
    [switch]$Uninstall,
    [string]$SkillsDir = "$env:USERPROFILE\.claude\skills"
)

$ErrorActionPreference = "Continue"
$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CtrlDir  = "$env:USERPROFILE\.claude\claude-control"
$Ts      = Get-Date -Format "yyyyMMdd-HHmmss"
$script:Warnings = 0
$script:Failures = 0

function OK($m)   { Write-Host "  [ OK ] $m" -ForegroundColor Green }
function SKIP($m) { Write-Host "  [SKIP] $m" -ForegroundColor DarkGray }
function WARN($m) { Write-Host "  [WARN] $m" -ForegroundColor Yellow; $script:Warnings++ }
function FAIL($m) { Write-Host "  [FAIL] $m" -ForegroundColor Red;    $script:Failures++ }

Write-Host "claude-control :: $(if ($Uninstall) {'uninstall'} else {'install'})" -ForegroundColor Cyan
Write-Host "  repo   : $RepoDir"
Write-Host "  skills : $SkillsDir"
Write-Host "  tools  : $CtrlDir"
Write-Host ""

# ---------- uninstall ----------
if ($Uninstall) {
    Get-ChildItem -Directory "$RepoDir\skills" | ForEach-Object {
        $t = Join-Path $SkillsDir $_.Name
        if (Test-Path $t) { Remove-Item -Recurse -Force $t; OK "removed skill $($_.Name)" }
        else { SKIP "$($_.Name) not installed" }
    }
    if (Test-Path $CtrlDir) { Remove-Item -Recurse -Force $CtrlDir; OK "removed $CtrlDir" }
    Write-Host "`nUninstalled. Backups (if any) remain in $env:USERPROFILE\.claude\skills-backup-*"
    exit 0
}

# ---------- sanity ----------
if (-not (Test-Path "$RepoDir\skills")) { FAIL "skills\ not found next to install.ps1 - corrupt download?"; exit 1 }
New-Item -ItemType Directory -Force -Path $SkillsDir, $CtrlDir | Out-Null

function Install-Tree($Src, $Dest, $Label) {
    if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
    if ($Symlink) {
        try {
            New-Item -ItemType SymbolicLink -Path $Dest -Target $Src -ErrorAction Stop | Out-Null
            OK "linked $Label"; return
        } catch {
            WARN "symlink for $Label failed (needs admin or Developer Mode) - copying instead"
        }
    }
    Copy-Item -Recurse -Force $Src $Dest
    OK "copied $Label"
}

# ---------- 1. skills ----------
Write-Host "1) Installing skills" -ForegroundColor Cyan
$BackupDir = "$env:USERPROFILE\.claude\skills-backup-$Ts"
Get-ChildItem -Directory "$RepoDir\skills" | ForEach-Object {
    $name   = $_.Name
    $src    = $_.FullName
    $target = Join-Path $SkillsDir $name
    if (Test-Path $target) {
        $diff = Compare-Object (Get-ChildItem -Recurse -File $src | Get-FileHash).Hash `
                               (Get-ChildItem -Recurse -File $target | Get-FileHash).Hash
        if (-not $diff) { SKIP "$name already up to date"; return }
        New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
        Move-Item $target (Join-Path $BackupDir $name)
        WARN "$name existed - backed up to $BackupDir\$name"
    }
    Install-Tree $src $target $name
}

# ---------- 2. tools + templates ----------
Write-Host "`n2) Installing tools" -ForegroundColor Cyan
Install-Tree "$RepoDir\tools"     "$CtrlDir\tools"     "tools\"
Install-Tree "$RepoDir\templates" "$CtrlDir\templates" "templates\"

# ---------- 3. skill manager ----------
Write-Host "`n3) Installing skill manager" -ForegroundColor Cyan
Install-Tree "$RepoDir\skill-manager" "$CtrlDir\skill-manager" "skill-manager\"
New-Item -ItemType Directory -Force -Path "$CtrlDir\bin" | Out-Null
$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" }
      elseif (Get-Command py -ErrorAction SilentlyContinue) { "py -3" }
      else { "python" }
@"
@echo off
$py "%USERPROFILE%\.claude\claude-control\skill-manager\server.py" %*
"@ | Set-Content -Encoding ASCII "$CtrlDir\bin\skill-manager.cmd"
OK "launcher: $CtrlDir\bin\skill-manager.cmd"

# ---------- 4. dependency report ----------
Write-Host "`n4) Dependency check  (nothing here blocks the install)" -ForegroundColor Cyan
function Check($cmd, $okMsg, $warnMsg) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { OK "$cmd found - $okMsg" }
    else { WARN "$cmd missing - $warnMsg" }
}
if ((Get-Command python -ErrorAction SilentlyContinue) -or (Get-Command py -ErrorAction SilentlyContinue)) {
    OK "python found - tools + skill manager will run"
} else {
    WARN "python missing - tools and skill manager need Python 3.9+ (https://python.org, tick 'Add to PATH')"
}
Check git    "version control ready"          "install git to clone/push this repo (https://git-scm.com)"
Check node   "Claude Code runtime present"    "Claude Code needs Node 18+ (https://nodejs.org)"
Check claude "skills will load in Claude Code; chat backend ready" "install Claude Code: npm install -g @anthropic-ai/claude-code"
Check docker "/isolate sandbox available"     "/isolate needs Docker Desktop - optional"
Check gh     "/design can enable Pages via API" "gh CLI is optional; /design falls back to manual steps"

# ---------- summary ----------
Write-Host ""
Write-Host "Done.  warnings: $script:Warnings  failures: $script:Failures" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  * Restart Claude Code - skills load from $SkillsDir"
Write-Host "  * Skill manager UI:   $CtrlDir\bin\skill-manager.cmd    then open http://127.0.0.1:8765"
Write-Host "  * Per-project setup:  copy $CtrlDir\templates\CLAUDE.md into your project as CLAUDE.md"
Write-Host "  * Note: bash-based skill scripts (deploy, isolate) need Git Bash or WSL on Windows."
exit 0
