# ==============================================================================
# DocShell Windows - Automated Dependency Installer
# Downloads and installs required runtimes, compilers, and libraries
# ==============================================================================
$ErrorActionPreference = "Continue"
. "$PSScriptRoot\common.ps1"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "[DocShell] Automated Dependency Installer (Windows)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

function Refresh-SessionPath {
    $machine = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = @($machine, $user, $env:Path) -join ";"
}

# 1. Check for winget package manager
$wingetCmd = Resolve-WingetCommand
if (-not $wingetCmd) {
    Write-Host "[ERROR] 'winget' was not found on your system." -ForegroundColor Red
    Write-Host "[HINT] Install Microsoft 'App Installer' from Microsoft Store or update Windows 10/11." -ForegroundColor Yellow
    exit 1
}

$packages = @(
    @{ Name = "Python 3.12"; Id = "Python.Python.3.12"; Cmd = "python" },
    @{ Name = "Pandoc (PDF Engine)"; Id = "JohnMacFarlane.Pandoc"; Cmd = "pandoc" },
    @{ Name = "MiKTeX (XeLaTeX / PDF)"; Id = "MiKTeX.MiKTeX"; Cmd = "xelatex" },
    @{ Name = "Node.js (LTS)"; Id = "OpenJS.NodeJS"; Cmd = "node" },
    @{ Name = "PHP CLI"; Id = "PHP.PHP"; Cmd = "php" },
    @{ Name = "Taskfile CLI"; Id = "Task.Task"; Cmd = "task" },
    @{ Name = "Git"; Id = "Git.Git"; Cmd = "git" },
    @{ Name = "Ollama (Local AI)"; Id = "Ollama.Ollama"; Cmd = "ollama" }
)

Write-Host "`n[1/2] Checking system tools...`n" -ForegroundColor Yellow

foreach ($pkg in $packages) {
    Refresh-SessionPath
    $exists = $null -ne (Get-Command $pkg.Cmd -ErrorAction SilentlyContinue)
    
    if ($exists) {
        Write-Host "  [OK] $($pkg.Name) is already installed." -ForegroundColor Green
    } else {
        Write-Host "  [+] Installing $($pkg.Name) (ID: $($pkg.Id))..." -ForegroundColor Cyan
        try {
            & winget install --id $pkg.Id --exact --accept-source-agreements --accept-package-agreements --silent
            Refresh-SessionPath
            Write-Host "  [OK] $($pkg.Name) installation completed." -ForegroundColor Green
        } catch {
            Write-Host "  [WARN] Failed to auto-install $($pkg.Name): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

# 2. Install Python packages from requirements.txt
Write-Host "`n[2/2] Installing Python libraries (pip)...`n" -ForegroundColor Yellow
Refresh-SessionPath
$python = Resolve-PythonCommand

if (($null -ne (Get-Command $python -ErrorAction SilentlyContinue)) -or (Test-Path -LiteralPath $python)) {
    $reqFile = Join-Path $RootDir "scripts\requirements.txt"
    if (Test-Path $reqFile) {
        Write-Host "Executing: $python -m pip install -r scripts/requirements.txt" -ForegroundColor Cyan
        & $python -m pip install --upgrade pip --quiet
        & $python -m pip install -r $reqFile
        Write-Host "  [OK] Python dependencies installed successfully!" -ForegroundColor Green
    }
} else {
    Write-Host "[WARN] Python not detected in current session. Restart terminal to refresh environment variables." -ForegroundColor Yellow
}

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "[DONE] Installation process completed!" -ForegroundColor Green
Write-Host "[HINT] If newly installed tools are not recognized immediately," -ForegroundColor Cyan
Write-Host "       please restart your terminal/PowerShell window." -ForegroundColor Cyan
Write-Host "=================================================================`n" -ForegroundColor Cyan
