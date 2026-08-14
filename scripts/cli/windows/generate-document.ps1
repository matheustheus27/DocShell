# ==============================================================================
# DocShell Windows - Generate Consolidated Document & Functional TOC
# ==============================================================================
param(
    [Alias("l", "loc")]
    [string]$Locale = "en-US"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$python = Resolve-PythonCommand
$hasPython = ($null -ne (Get-Command $python -ErrorAction SilentlyContinue)) -or (Test-Path -LiteralPath $python -ErrorAction SilentlyContinue)

if ($hasPython) {
    Write-Host "[DocShell] Running Smart Doc Parser via Python Engine (Locale: $Locale)..." -ForegroundColor Cyan
    $parserScript = Join-Path $RootDir "scripts\core\doc_parser.py"
    & $python $parserScript -l $Locale
    exit $LASTEXITCODE
}

# ==============================================================================
# Native PowerShell Engine (Used when Python is not available in session)
# ==============================================================================
Write-Host "[DocShell] Running Smart Doc Parser (Native PowerShell Engine, Locale: $Locale)..." -ForegroundColor Cyan

$docsDir = Join-Path $RootDir "docs"
$pubDir = Join-Path $RootDir "publication"
$imagesDir = Join-Path $RootDir "images"
$outputMd = Join-Path $pubDir "documento-completo.md"
$searchJson = Join-Path $pubDir "search_index.json"

if (-not (Test-Path -LiteralPath $pubDir)) {
    New-Item -ItemType Directory -Force -Path $pubDir | Out-Null
}

$mdFiles = Get-ChildItem -Path $docsDir -Filter "*.md" -Recurse | Sort-Object {
    [regex]::Replace($_.FullName, '\d+', { $args[0].Value.PadLeft(8, '0') })
}

Write-Host "Found $($mdFiles.Count) documents:" -ForegroundColor Green

$docsList = @()
$searchChunks = @()

function Get-Slug([string]$text) {
    $clean = [System.Text.Encoding]::ASCII.GetString([System.Text.Encoding]::GetEncoding("Cyrillic").GetBytes($text))
    $clean = $clean.ToLower() -replace '[^\w\s-]', '' -replace '[\s_]+', '-'
    return $clean.Trim('-')
}

foreach ($file in $mdFiles) {
    $rel = $file.FullName.Substring($docsDir.Length).TrimStart('\', '/')
    $parts = $rel.Split([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    
    $section = if ($parts.Count -gt 1) {
        ([regex]::Replace($parts[0], '^\d+[-_.]*', '') -replace '[-_]', ' ')
    } else {
        "General"
    }
    $section = (Get-Culture).TextInfo.ToTitleCase($section)

    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $title = ""
    $body = $content

    # Extract Frontmatter
    if ($content -match '(?ms)^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$') {
        $body = $Matches[2]
        if ($Matches[1] -match 'title:\s*["'']?([^"''\r\n]+)["'']?') {
            $title = $Matches[1].Trim()
        }
    }

    if ([string]::IsNullOrWhiteSpace($title)) {
        if ($body -match '(?m)^#\s+(.+)$') {
            $title = $Matches[1].Trim()
        } else {
            $title = [System.IO.Path]::GetFileNameWithoutExtension($file.Name) -replace '^\d+[-_.]*', '' -replace '[-_]', ' '
        }
    }

    $slug = Get-Slug "$section-$title"

    $docObj = [PSCustomObject]@{
        FilePath = $file.FullName
        RelativePath = $rel -replace '\\', '/'
        Section = $section
        Title = $title
        Slug = $slug
        Body = $body
    }
    $docsList += $docObj
    Write-Host "   + [$section] $rel -> '$title'"

    # Search chunk
    $searchChunks += [PSCustomObject]@{
        id = "$slug-0"
        doc_title = $title
        section = $section
        chunk_title = $title
        slug = $slug
        relative_path = $rel -replace '\\', '/'
        text = ($body -replace '[#*`_\[\]()!>]', ' ' -replace '\s+', ' ').Trim().Substring(0, [Math]::Min(500, $body.Length))
    }
}

# Group docs by section to avoid split sections and duplicate anchors
$sections = [ordered]@{}
foreach ($d in $docsList) {
    if (-not $sections.Contains($d.Section)) {
        $sections[$d.Section] = [System.Collections.Generic.List[psobject]]::new()
    }
    $sections[$d.Section].Add($d)
}

# Localized headings (ASCII safe for Windows PowerShell 5.1)
$tocTitle = switch ($Locale.ToLower()) {
    { $_ -in @("pt", "pt-br") } { "Sumario Executivo" }
    { $_ -in @("es") } { "Indice de Contenidos" }
    { $_ -in @("fr") } { "Table des Matieres" }
    { $_ -in @("de") } { "Inhaltsverzeichnis" }
    { $_ -in @("it") } { "Indice dei Contenuti" }
    default { "Table of Contents" }
}

$docMainTitle = switch ($Locale.ToLower()) {
    { $_ -in @("pt", "pt-br") } { "DocShell - Documentacao Tecnica Unificada" }
    { $_ -in @("es") } { "DocShell - Documentacion Tecnica" }
    { $_ -in @("fr") } { "DocShell - Documentation Technique" }
    { $_ -in @("de") } { "DocShell - Technische Dokumentation" }
    { $_ -in @("it") } { "DocShell - Documentazione Tecnica" }
    default { "DocShell - Technical Documentation" }
}

# Build Consolidated Markdown
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("---")
$lines.Add("title: `"$docMainTitle`"")
$lines.Add('subtitle: "Guia de Arquitetura e Engenharia do Sistema"')
$lines.Add('author: "Matheus Ferreira"')
$lines.Add('version: "1.0.0"')
$lines.Add('release: "v1.0"')
$lines.Add("language: `"$Locale`"")
$lines.Add("---`n")
$lines.Add("# $docMainTitle`n")
$lines.Add("## $tocTitle`n")

$secIdx = 0
foreach ($secName in $sections.Keys) {
    $secIdx++
    $secSlug = Get-Slug "section-$secIdx-$secName"
    $lines.Add("### $secIdx. [$secName](#$secSlug)`n")
    
    $itemIdx = 0
    foreach ($d in $sections[$secName]) {
        $itemIdx++
        $lines.Add("- [$secIdx.$itemIdx $($d.Title)](#$($d.Slug))")
    }
    $lines.Add("")
}

$lines.Add("---`n")

$secNum = 0
foreach ($secName in $sections.Keys) {
    $secNum++
    $secSlug = Get-Slug "section-$secNum-$secName"
    $lines.Add("`n# $secNum. $secName {#$secSlug}`n")

    foreach ($d in $sections[$secName]) {
        $lines.Add("<!-- doc: $($d.RelativePath) -->")
        
        # Normalize image paths for PDF with PNG fallback
        $normBody = [regex]::Replace($d.Body, '!\[(.*?)\]\((.*?)\)', {
            param($m)
            $alt = $m.Groups[1].Value
            $src = $m.Groups[2].Value.Trim() -replace '\\', '/'
            if ($src.StartsWith("http://") -or $src.StartsWith("https://") -or $src.StartsWith("data:")) {
                return $m.Value
            }
            $imgName = if ($src.Contains("images/")) { $src.Substring($src.IndexOf("images/") + 7) } else { [System.IO.Path]::GetFileName($src) }
            
            if ($imgName.ToLower().EndsWith(".svg")) {
                $pngCandidate = [System.IO.Path]::ChangeExtension($imgName, ".png")
                if (Test-Path (Join-Path $imagesDir $pngCandidate)) {
                    $imgName = $pngCandidate
                }
            }
            return "![$alt](images/$imgName)"
        })

        # Inject {#slug} into the first heading
        $headingInjected = $false
        $bodyWithId = [regex]::Replace($normBody, '(?m)^(#+)\s+(.*?)(?:\s*\{#.*?\})?$', {
            param($hm)
            if (-not $headingInjected) {
                $script:headingInjected = $true
                return "$($hm.Groups[1].Value) $($hm.Groups[2].Value.Trim()) {#$($d.Slug)}"
            }
            return $hm.Value
        }, 1)

        if (-not $headingInjected) {
            $bodyWithId = "## $($d.Title) {#$($d.Slug)}`n`n" + $bodyWithId
        }

        $lines.Add($bodyWithId)
        $lines.Add("`n---`n")
    }
}

[System.IO.File]::WriteAllText($outputMd, ($lines -join "`n"), [System.Text.UTF8Encoding]::new($false))
$searchChunks | ConvertTo-Json -Depth 4 | Set-Content -Path $searchJson -Encoding UTF8

Write-Host "  [OK] Consolidated document generated: $outputMd" -ForegroundColor Green
Write-Host "  [OK] Search index generated: $searchJson" -ForegroundColor Green
