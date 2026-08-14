# ==============================================================================
# DocShell Windows CLI - Common Utilities
# ==============================================================================

$Script:RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path

function Update-SessionPath {
    $machine = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = @($machine, $user, $env:Path) -join ";"
}

function Resolve-PythonCommand {
    Update-SessionPath
    if (Get-Command "python" -ErrorAction SilentlyContinue) { return "python" }
    if (Get-Command "py" -ErrorAction SilentlyContinue) { return "py" }
    if (Get-Command "python3" -ErrorAction SilentlyContinue) { return "python3" }
    
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "$env:ProgramFiles\Python*\python.exe",
        "${env:ProgramFiles(x86)}\Python*\python.exe",
        "C:\Python*\python.exe"
    )
    foreach ($pattern in $candidates) {
        $matches = @(Get-Item -Path $pattern -ErrorAction SilentlyContinue)
        if ($matches.Count -gt 0) {
            return $matches[0].FullName
        }
    }
    return "python"
}

function Resolve-NodeCommand {
    Update-SessionPath
    if (Get-Command "node" -ErrorAction SilentlyContinue) { return "node" }
    $candidates = @(
        "$env:ProgramFiles\nodejs\node.exe",
        "${env:ProgramFiles(x86)}\nodejs\node.exe"
    )
    foreach ($pattern in $candidates) {
        $matches = @(Get-Item -Path $pattern -ErrorAction SilentlyContinue)
        if ($matches.Count -gt 0) {
            return $matches[0].FullName
        }
    }
    return "node"
}

function Resolve-PhpCommand {
    Update-SessionPath
    if (Get-Command "php" -ErrorAction SilentlyContinue) { return "php" }
    $candidates = @(
        "C:\PHP 8.4\php.exe",
        "C:\TEKNISA\apache\php74\php.exe",
        "$env:LOCALAPPDATA\Programs\php\php.exe",
        "C:\php\php.exe",
        "$env:ProgramFiles\php\php.exe"
    )
    foreach ($pattern in $candidates) {
        $matches = @(Get-Item -Path $pattern -ErrorAction SilentlyContinue)
        if ($matches.Count -gt 0) {
            return $matches[0].FullName
        }
    }
    return "php"
}

function Resolve-WingetCommand {
    Update-SessionPath
    if (Get-Command "winget" -ErrorAction SilentlyContinue) { return "winget" }
    $candidates = @(
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\winget.exe",
        "$env:ProgramFiles\WindowsApps\Microsoft.DesktopAppInstaller_*\winget.exe"
    )
    foreach ($pattern in $candidates) {
        $matches = @(Get-Item -Path $pattern -ErrorAction SilentlyContinue)
        if ($matches.Count -gt 0) {
            return $matches[0].FullName
        }
    }
    return $null
}
