# ==============================================================================
# DocShell Windows - Generate PDF with Visual Model & Localization
# ==============================================================================
param(
    [Alias("m")]
    [string]$Model = "glassmorphic",

    [Alias("l", "loc")]
    [string]$Locale = "pt-BR"
)

$ErrorActionPreference = "Continue"
. "$PSScriptRoot\common.ps1"

# 1. Ensure consolidated document exists in requested locale
& "$PSScriptRoot\generate-document.ps1" -Locale $Locale

$python = Resolve-PythonCommand
$hasPython = ($null -ne (Get-Command $python -ErrorAction SilentlyContinue)) -or (Test-Path -LiteralPath $python -ErrorAction SilentlyContinue)

if ($hasPython) {
    $pdfScript = Join-Path $RootDir "scripts\core\pdf_engine.py"
    Write-Host "[DocShell] Compiling PDF via Python Engine (Model: $Model, Locale: $Locale)..." -ForegroundColor Cyan
    & $python $pdfScript -m $Model -l $Locale
    exit $LASTEXITCODE
}

# 2. Try compiling directly via Pandoc + XeLaTeX if available
$pandoc = Get-Command "pandoc" -ErrorAction SilentlyContinue
$xelatex = (Get-Command "xelatex" -ErrorAction SilentlyContinue) -or (Get-Command "pdflatex" -ErrorAction SilentlyContinue)

if ($pandoc -and $xelatex) {
    Write-Host "[DocShell] Compiling PDF directly via Pandoc + XeLaTeX..." -ForegroundColor Cyan
    $sourceMd = Join-Path $RootDir "publication\documento-completo.md"
    $distPdf = Join-Path $RootDir "dist\pdf"
    New-Item -ItemType Directory -Force -Path $distPdf | Out-Null
    
    $outputFile = if ($Locale -eq "pt-BR") {
        Join-Path $distPdf "DocShell-Technical-Documentation-$Model.pdf"
    }
    else {
        Join-Path $distPdf "DocShell-Technical-Documentation-$Model-$Locale.pdf"
    }
    
    $modelDir = Join-Path $RootDir "models\$Model"
    $pdfHeader = Join-Path $modelDir "pdf\header.tex"
    if (-not (Test-Path $pdfHeader)) {
        $pdfHeader = Join-Path $RootDir "models\glassmorphic\pdf\header.tex"
    }

    & $pandoc.Source $sourceMd `
        --from markdown+raw_tex+header_attributes `
        --pdf-engine=$($xelatex.Source) `
        --resource-path=.:publication:images `
        --include-in-header=$pdfHeader `
        -V documentclass=report -V papersize=a4 -V fontsize=11pt -V colorlinks=true `
        -o $outputFile

    if (Test-Path -LiteralPath $outputFile) {
        Write-Host "  [OK] PDF generated successfully: $outputFile" -ForegroundColor Green
        exit 0
    }
}

Write-Host "[WARN] PDF compilation tools not found (Python / Pandoc / MiKTeX)." -ForegroundColor Yellow
Write-Host "[HINT] Run 'task install' or 'make install' to automatically install all compilers and dependencies." -ForegroundColor Cyan
exit 1
