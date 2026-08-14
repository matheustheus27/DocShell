# ==============================================================================
# DocShell Windows - Serve Web Documentation & RAG API
# ==============================================================================
param(
    [Alias("l")]
    [string]$Lang = "python",

    [Alias("p")]
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$normalizedLang = $Lang.ToLower().Trim()

switch ($normalizedLang) {
    { $_ -in @("py", "python") } {
        $python = Resolve-PythonCommand
        $server = Join-Path $RootDir "scripts\generators\python\serve_site.py"
        Write-Host "[DocShell] Starting Python server on port $Port..." -ForegroundColor Green
        & $python $server -p $Port
    }
    { $_ -in @("php") } {
        $php = Resolve-PhpCommand
        $server = Join-Path $RootDir "scripts\generators\php\serve_site.php"
        Write-Host "[DocShell] Starting PHP server on port $Port..." -ForegroundColor Green
        & $php $server $Port
    }
    { $_ -in @("js", "javascript", "node") } {
        $node = Resolve-NodeCommand
        $server = Join-Path $RootDir "scripts\generators\javascript\serve_site.js"
        Write-Host "[DocShell] Starting Node.js server on port $Port..." -ForegroundColor Green
        & $node $server -p $Port
    }
    default {
        $python = Resolve-PythonCommand
        $server = Join-Path $RootDir "scripts\generators\python\serve_site.py"
        & $python $server -p $Port
    }
}
