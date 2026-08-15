# ==============================================================================
# DocShell Windows - Full Build & Deploy Orchestrator
# Builds docs, PDF, web frontend, atomic backend, worker and Docker containers
# ==============================================================================
param (
    [Alias("l", "lang")]
    [string]$Language = "python",

    [Alias("m")]
    [string]$Model = "glassmorphic",

    [Alias("a")]
    [switch]$All,

    [Alias("loc")]
    [string]$Locale = "pt-BR"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "[DocShell] Full Build Pipeline Orchestrator" -ForegroundColor Cyan
Write-Host "   Language Runtime : $(if ($All) { 'ALL (Python, PHP, Node.js)' } else { $Language })" -ForegroundColor Cyan
Write-Host "   Theme Model      : $Model" -ForegroundColor Cyan
Write-Host "   Target Locale    : $Locale" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Validate internal links and asset references
Write-Host "`n[1/5] Validating internal links and assets..." -ForegroundColor Yellow
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "validate-links.ps1")

# 2. Consolidate documents and build Table of Contents
Write-Host "`n[2/5] Consolidating documents (documento-completo.md)..." -ForegroundColor Yellow
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "generate-document.ps1")

# 3. Generate versioned PDF
Write-Host "`n[3/5] Compiling PDF ($Model)..." -ForegroundColor Yellow
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "generate-pdf.ps1") -m $Model

# 4. Generate Webdoc, Backend, Worker and Standalone Package
Write-Host "`n[4/5] Generating Web, Backend & Worker ($Language, $Model)..." -ForegroundColor Yellow
if ($All) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "generate-site.ps1") -l "py" -m $Model
} else {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "generate-site.ps1") -l $Language -m $Model
}

# 5. Build and start Docker container stack
Write-Host "`n[5/5] Building and launching Docker container stack..." -ForegroundColor Yellow
if ($All) {
    Write-Host "Starting all Docker profiles: python, php, node..." -ForegroundColor Cyan
    docker compose --profile python --profile php --profile node up -d --build
} else {
    $normLang = $Language.ToLower().Trim()
    if ($normLang -in @("php")) {
        Write-Host "Starting PHP stack on port 8000..." -ForegroundColor Cyan
        docker compose --profile php up -d --build
    } elseif ($normLang -in @("js", "javascript", "node", "nodejs")) {
        Write-Host "Starting Node.js stack on port 8000..." -ForegroundColor Cyan
        docker compose --profile node up -d --build
    } else {
        Write-Host "Starting Python stack on port 8000..." -ForegroundColor Cyan
        docker compose --profile python up -d --build
    }
}

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host "[OK] Full build completed successfully!" -ForegroundColor Green
Write-Host "   Web Interface: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   RAG API Gateway: http://localhost:8080" -ForegroundColor Cyan
Write-Host "   RabbitMQ UI: http://localhost:15672 (guest/guest)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Green
