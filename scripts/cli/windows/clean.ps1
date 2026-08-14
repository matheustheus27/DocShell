# ==============================================================================
# DocShell Windows - Cleanup Generated Artifacts
# ==============================================================================
. "$PSScriptRoot\common.ps1"

Write-Host "[DocShell] Cleaning up generated build artifacts..." -ForegroundColor Cyan

$pathsToRemove = @(
    (Join-Path $RootDir "dist"),
    (Join-Path $RootDir "publication\documento-completo.md"),
    (Join-Path $RootDir "publication\.pdf-meta.tex"),
    (Join-Path $RootDir "publication\search_index.json")
)

foreach ($p in $pathsToRemove) {
    if (Test-Path -LiteralPath $p) {
        Remove-Item -Recurse -Force -LiteralPath $p -ErrorAction SilentlyContinue
        Write-Host "  Removed: $p"
    }
}

Write-Host "  [OK] Cleanup completed successfully." -ForegroundColor Green
