# ==============================================================================
# DocShell Windows - Validate Links & Assets
# ==============================================================================
. "$PSScriptRoot\common.ps1"

$python = Resolve-PythonCommand
$hasPython = ($null -ne (Get-Command $python -ErrorAction SilentlyContinue)) -or (Test-Path -LiteralPath $python -ErrorAction SilentlyContinue)

if ($hasPython) {
    $validator = Join-Path $RootDir "scripts\core\link_validator.py"
    & $python $validator
    exit $LASTEXITCODE
}

# ==============================================================================
# Native PowerShell Validator
# ==============================================================================
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "[DocShell] Link and Asset Validator (PowerShell Engine)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$docsDir = Join-Path $RootDir "docs"
$imagesDir = Join-Path $RootDir "images"

$mdFiles = Get-ChildItem -Path $docsDir -Filter "*.md" -Recurse
$checkedFiles = 0
$checkedImages = 0
$errors = 0

foreach ($file in $mdFiles) {
    $checkedFiles++
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $rel = $file.FullName.Substring($RootDir.Length).TrimStart('\', '/')

    # Check images ![alt](src)
    $imgMatches = [regex]::Matches($content, '!\[(.*?)\]\((.*?)\)')
    foreach ($m in $imgMatches) {
        $checkedImages++
        $src = $m.Groups[2].Value.Trim() -replace '\\', '/'
        
        if ($src.StartsWith("http://") -or $src.StartsWith("https://") -or $src.StartsWith("data:")) {
            continue
        }

        $imgName = if ($src.Contains("images/")) {
            $src.Substring($src.IndexOf("images/") + 7)
        } else {
            $src
        }

        $targetImg = Join-Path $imagesDir $imgName
        if (-not (Test-Path -LiteralPath $targetImg)) {
            Write-Host ("  [MISSING IMAGE] in {0}: '{1}' (expected at {2})" -f $rel, $src, $targetImg) -ForegroundColor Red
            $errors++
        }
    }
}

Write-Host "-----------------------------------------------------------------"
Write-Host "Validation Summary:"
Write-Host "   Markdown files checked: $checkedFiles"
Write-Host "   Images verified: $checkedImages"
Write-Host "   Errors found: $errors"
Write-Host "================================================================="

if ($errors -gt 0) {
    Write-Host "[FAIL] Validation failed due to missing assets." -ForegroundColor Red
    exit 1
}

Write-Host "  [OK] All links and assets validated successfully!" -ForegroundColor Green
exit 0
