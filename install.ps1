# claude-control installer / updater (Windows PowerShell 5.1+ / PowerShell 7)
# One shot, idempotent, non-destructive: existing skills are backed up, never overwritten silently.
# Re-running updates an existing install in place (tools/manager/templates refreshed, changed skills re-copied).
# Usage:  powershell -ExecutionPolicy Bypass -File install.ps1 [-Symlink] [-Uninstall] [-SkillsDir DIR]
#                    [-WithExternal] [-External NAME[,NAME...]] [-Yes] [-NoInput]
#   -WithExternal   also clone+install every source in skill-sources.txt (needs git + python)
#   -External LIST  only those named sources (comma-separated), implies -WithExternal
#   -Yes            answer "yes" to every prompt (install missing deps, add to PATH)
#   -NoInput        never prompt; report only
param(
    [switch]$Symlink,
    [switch]$Uninstall,
    [string]$SkillsDir = "$env:USERPROFILE\.claude\skills",
    [switch]$WithExternal,
    [string]$External = "",
    [switch]$Yes,
    [switch]$NoInput
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

# ---------- interactivity ----------
function Ask($q) {
    if ($Yes)     { return $true }
    if ($NoInput) { return $false }
    if (-not [Environment]::UserInteractive) { return $false }
    $r = Read-Host "  [ ?  ] $q [y/N]"
    return ($r -match '^[Yy]')
}

# ---------- package manager detection (winget preferred, choco fallback) ----------
$WinGet = Get-Command winget -ErrorAction SilentlyContinue
$Choco  = Get-Command choco  -ErrorAction SilentlyContinue

# Build an install command for a dep, or "" if no package manager is available.
function PkgCmd($wingetId, $chocoName) {
    if ($WinGet) { return "winget install -e --id $wingetId --accept-source-agreements --accept-package-agreements" }
    elseif ($Choco) { return "choco install $chocoName -y" }
    else { return "" }
}

# DepOffer <cmd> <description> <install-command>
function DepOffer($cmd, $desc, $installCmd) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { OK "$cmd found - $desc"; return }
    WARN "$cmd missing - $desc"
    if (-not $installCmd) { SKIP "no auto-install for $cmd on this system; install it manually"; return }
    if (Ask "Install $cmd now?  ($installCmd)") {
        Write-Host "     > $installCmd" -ForegroundColor DarkGray
        Invoke-Expression $installCmd
        if (Get-Command $cmd -ErrorAction SilentlyContinue) { OK "installed $cmd" }
        else { WARN "$cmd not on PATH yet - you may need to open a new terminal" }
    } else { SKIP "$cmd left uninstalled" }
}

# ---------- resolve python ----------
$Py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" }
      elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" }
      else { $null }

Write-Host "claude-control :: $(if ($Uninstall) {'uninstall'} else {'install'})" -ForegroundColor Cyan
Write-Host "  repo   : $RepoDir"
Write-Host "  skills : $SkillsDir"
Write-Host "  tools  : $CtrlDir"
if ((Test-Path "$CtrlDir\tools") -and (-not $Uninstall)) {
    Write-Host "  (existing install detected - this run will UPDATE it in place)" -ForegroundColor DarkGray
}
Write-Host ""

# ---------- uninstall ----------
if ($Uninstall) {
    if ($Py -and (Test-Path "$CtrlDir\tools\skillsource.py")) {
        & $Py "$CtrlDir\tools\skillsource.py" --skills-dir $SkillsDir --ctrl-dir $CtrlDir remove all *> $null
        OK "removed external (gstack/etc.) skills"
    }
    Get-ChildItem -Directory "$RepoDir\skills" | ForEach-Object {
        $t = Join-Path $SkillsDir $_.Name
        if (Test-Path $t) { Remove-Item -Recurse -Force $t; OK "removed skill $($_.Name)" }
        else { SKIP "$($_.Name) not installed" }
    }
    if (Test-Path $CtrlDir) { Remove-Item -Recurse -Force $CtrlDir; OK "removed $CtrlDir (incl. external\ clones)" }
    Write-Host "`nUninstalled. Backups (if any) remain in $env:USERPROFILE\.claude\skills-backup-*"
    Write-Host "Note: graphify (if installed) is a separate pip package - remove with: pip uninstall graphifyy"
    Write-Host "      any PATH entry added to your user environment was left in place."
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
        WARN "$name changed - old copy backed up to $BackupDir\$name"
    }
    Install-Tree $src $target $name
}

# ---------- 2. tools + templates + skill-sources manifest ----------
Write-Host "`n2) Installing tools  (refreshed every run so updates land)" -ForegroundColor Cyan
Install-Tree "$RepoDir\tools"     "$CtrlDir\tools"     "tools\"
Install-Tree "$RepoDir\templates" "$CtrlDir\templates" "templates\"
if ($Symlink) {
    if (Test-Path "$CtrlDir\skill-sources.txt") { Remove-Item -Force "$CtrlDir\skill-sources.txt" }
    try { New-Item -ItemType SymbolicLink -Path "$CtrlDir\skill-sources.txt" -Target "$RepoDir\skill-sources.txt" -ErrorAction Stop | Out-Null; OK "linked skill-sources.txt" }
    catch { Copy-Item "$RepoDir\skill-sources.txt" "$CtrlDir\skill-sources.txt"; OK "copied skill-sources.txt" }
} elseif (Test-Path "$CtrlDir\skill-sources.txt") { SKIP "skill-sources.txt kept (yours)" }
else { Copy-Item "$RepoDir\skill-sources.txt" "$CtrlDir\skill-sources.txt"; OK "copied skill-sources.txt" }

# ---------- 3. skill manager ----------
Write-Host "`n3) Installing skill manager" -ForegroundColor Cyan
Install-Tree "$RepoDir\skill-manager" "$CtrlDir\skill-manager" "skill-manager\"
New-Item -ItemType Directory -Force -Path "$CtrlDir\bin" | Out-Null
$launchPy = if ($Py) { $Py } else { "python" }
@"
@echo off
$launchPy "%USERPROFILE%\.claude\claude-control\skill-manager\server.py" %*
"@ | Set-Content -Encoding ASCII "$CtrlDir\bin\skill-manager.cmd"
OK "launcher: $CtrlDir\bin\skill-manager.cmd"

# ---------- 3b. external skill sources (opt-in) ----------
Write-Host "`n3b) External skill sources  (gstack, anthropic-skills, ...)" -ForegroundColor Cyan
if ($External) { $WithExternal = $true }
if (-not $WithExternal) {
    SKIP "not fetched - re-run with -WithExternal, or use the skill manager's Sources panel"
} elseif (-not $Py) {
    WARN "skipped external skills: python not found"
} elseif (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    WARN "skipped external skills: git not found"
} else {
    $emode = if ($Symlink) { "symlink" } else { "copy" }
    $targets = if ($External) { $External -split "," } else { @("all") }
    foreach ($t in $targets) {
        $tn = $t.Trim()
        & $Py "$CtrlDir\tools\skillsource.py" --manifest "$CtrlDir\skill-sources.txt" `
            --skills-dir $SkillsDir --ctrl-dir $CtrlDir --mode $emode sync $tn
        if ($LASTEXITCODE -eq 0) { OK "synced source: $tn" } else { WARN "sync had issues for: $tn" }
    }
}

# ---------- 4. dependencies (interactive) ----------
Write-Host "`n4) Dependencies  (missing ones are offered for install; nothing here blocks the install)" -ForegroundColor Cyan
if ((-not $WinGet) -and (-not $Choco) -and (-not $NoInput)) {
    WARN "no package manager found (winget/choco) - deps will be report-only"
}

# python is special (may be 'python' or 'py')
if ($Py) { OK "python found - tools + skill manager will run" }
else { DepOffer "python" "tools + skill manager need Python 3.9+ (tick 'Add to PATH')" (PkgCmd "Python.Python.3.12" "python") }

DepOffer "git"  "clone/update this repo and skill sources" (PkgCmd "Git.Git" "git")
DepOffer "node" "Claude Code runtime (Node 18+)"           (PkgCmd "OpenJS.NodeJS.LTS" "nodejs-lts")

# claude CLI comes from npm.
if (Get-Command claude -ErrorAction SilentlyContinue) {
    OK "claude found - skills load in Claude Code; chat backend ready"
} elseif (Get-Command npm -ErrorAction SilentlyContinue) {
    DepOffer "claude" "the Claude Code CLI" "npm install -g @anthropic-ai/claude-code"
} else {
    WARN "claude missing - install Node first, then: npm install -g @anthropic-ai/claude-code"
}

# graphify: the /graphify skill (deep dependency/knowledge graph). pip package + its own skill.
$GraphifyPresent = (Get-Command graphify -ErrorAction SilentlyContinue) `
    -or (Test-Path "$SkillsDir\graphify\SKILL.md") `
    -or (Test-Path "$env:USERPROFILE\.claude\skills\graphify\SKILL.md")
$PipCmd = if ($Py) { "$Py -m pip" } else { $null }
if ($GraphifyPresent) {
    OK "graphify skill present - use /graphify . for a deep dependency graph"
    if ($PipCmd -and (Ask "Update graphify to the latest version?")) {
        Invoke-Expression "$PipCmd install --upgrade graphifyy"
        if ($LASTEXITCODE -eq 0) { OK "graphify updated" } else { WARN "graphify update had issues" }
    }
} else {
    WARN "graphify skill missing - deep dependency/knowledge graph (/graphify .), replaces the old graphify.py"
    if (-not $PipCmd) {
        SKIP "need Python 3.10+/pip to install graphify - see https://github.com/safishamsi/graphify"
    } elseif (Ask "Install graphify now?  ($PipCmd install graphifyy && graphify install)") {
        Write-Host "     > $PipCmd install graphifyy" -ForegroundColor DarkGray
        Invoke-Expression "$PipCmd install graphifyy"
        if (Get-Command graphify -ErrorAction SilentlyContinue) {
            graphify install
            OK "installed graphify - invoke it with /graphify . in Claude Code"
        } else {
            WARN "graphify pip package installed but the 'graphify' command isn't on PATH."
            WARN "open a new terminal (or add Python's Scripts dir to PATH), then run: graphify install"
        }
    } else {
        SKIP "graphify left uninstalled - later: $PipCmd install graphifyy && graphify install"
    }
}

# optional tools
DepOffer "docker" "/isolate sandbox (optional)"              (PkgCmd "Docker.DockerDesktop" "docker-desktop")
DepOffer "gh"     "/design can enable Pages via API (optional)" (PkgCmd "GitHub.cli" "gh")

# ---------- 5. PATH (interactive) ----------
Write-Host "`n5) PATH  (so 'skill-manager' works from any directory)" -ForegroundColor Cyan
$BinDir = "$CtrlDir\bin"
$UserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (($UserPath -split ';') -contains $BinDir) {
    SKIP "$BinDir already on your user PATH"
} elseif (Ask "Add $BinDir to your user PATH?") {
    $newPath = ($UserPath.TrimEnd(';') + ';' + $BinDir)
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
    $env:Path += ";$BinDir"
    OK "added to user PATH - open a new terminal to pick it up"
} else {
    SKIP "PATH not modified - add $BinDir yourself if you want 'skill-manager' everywhere"
}

# ---------- summary ----------
Write-Host ""
Write-Host "Done.  warnings: $script:Warnings  failures: $script:Failures" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  * Restart Claude Code - skills load from $SkillsDir"
Write-Host "  * Skill manager UI:   $CtrlDir\bin\skill-manager.cmd    then open http://127.0.0.1:8765"
Write-Host "  * Per-project setup:  copy $CtrlDir\templates\CLAUDE.md into your project as CLAUDE.md"
Write-Host "  * Deep repo graphs:   /graphify .   (install offered above; upstream: https://github.com/safishamsi/graphify)"
if (-not $WithExternal) {
Write-Host "  * Add more skills:    install.ps1 -WithExternal   (gstack + anthropic-skills)"
Write-Host "                        or: $launchPy $CtrlDir\tools\skillsource.py sync all"
}
Write-Host "  * Re-run anytime:     install.ps1   updates tools, manager, and changed skills in place"
Write-Host "  * Note: bash-based skill scripts (deploy, isolate) need Git Bash or WSL on Windows."
exit 0
