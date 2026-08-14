# ==============================================================================
# DocShell Windows - Generate Web Documentation (Python, PHP, JavaScript, Native)
# ==============================================================================
param(
    [Alias("l")]
    [string]$Lang = "python",

    [Alias("m")]
    [string]$Model = "glassmorphic",

    [Alias("loc")]
    [string]$Locale = "pt-BR"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$normalizedLang = $Lang.ToLower().Trim()
$targetModel = $Model.ToLower().Trim()

# 0. Clean dist/webpage directory before building site
$distWeb = Join-Path $RootDir "dist\webpage"
if (Test-Path -LiteralPath $distWeb) {
    Write-Host "[DocShell] Cleaning dist\webpage directory..." -ForegroundColor DarkGray
    Get-ChildItem -LiteralPath $distWeb -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $distWeb | Out-Null

# 1. Python Generator (if available)
$python = Resolve-PythonCommand
$hasPython = ($null -ne (Get-Command $python -ErrorAction SilentlyContinue)) -or (Test-Path -LiteralPath $python -ErrorAction SilentlyContinue)

if ($hasPython -and ($normalizedLang -in @("python", "py"))) {
    $buildScript = Join-Path $RootDir "scripts\generators\python\build_site.py"
    Write-Host "[DocShell] Building website via Python generator (Model: $Model, Locale: $Locale)..." -ForegroundColor Cyan
    & $python $buildScript -m $Model -l $Locale
    if ($LASTEXITCODE -eq 0) { exit 0 }
}

# 2. PHP Generator (if available)
$php = Resolve-PhpCommand
$hasPhp = ($null -ne (Get-Command $php -ErrorAction SilentlyContinue)) -or (Test-Path -LiteralPath $php -ErrorAction SilentlyContinue)
if ($hasPhp -and ($normalizedLang -eq "php")) {
    $buildScript = Join-Path $RootDir "scripts\generators\php\build_site.php"
    Write-Host "[DocShell] Building website via PHP generator (Model: $Model)..." -ForegroundColor Cyan
    & $php $buildScript $Model
    if ($LASTEXITCODE -eq 0) { exit 0 }
}

# 3. JavaScript/Node.js Generator (if available)
$node = Resolve-NodeCommand
$hasNode = ($null -ne (Get-Command $node -ErrorAction SilentlyContinue)) -or (Test-Path -LiteralPath $node -ErrorAction SilentlyContinue)
if ($hasNode -and ($normalizedLang -in @("javascript", "js", "node"))) {
    $buildScript = Join-Path $RootDir "scripts\generators\javascript\build_site.js"
    Write-Host "[DocShell] Building website via Node.js generator (Model: $Model)..." -ForegroundColor Cyan
    & $node $buildScript -m $Model
    if ($LASTEXITCODE -eq 0) { exit 0 }
}

# ==============================================================================
# Native PowerShell Engine (Fallback & Standalone)
# ==============================================================================
$distWeb = Join-Path $RootDir "dist\webpage"
$imagesDir = Join-Path $RootDir "images"
$modelDir = Join-Path $RootDir "models\$targetModel"

if (-not (Test-Path $modelDir)) {
    $modelDir = Join-Path $RootDir "models\glassmorphic"
}

& "$PSScriptRoot\generate-document.ps1" -Locale $Locale

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "[DocShell] Web Documentation Generator (Native Engine, Locale: $Locale)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path (Join-Path $distWeb "images") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $distWeb "assets") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $distWeb "data") | Out-Null

if (Test-Path $imagesDir) {
    Get-ChildItem -Path $imagesDir -File | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination (Join-Path $distWeb "images\$($_.Name)") -Force
    }
    Write-Host "  [OK] Images copied to dist/webpage/images/" -ForegroundColor Green
}

$cssSrc = Join-Path $modelDir "web\style.css"
$jsSrc = Join-Path $modelDir "web\script.js"
if (-not (Test-Path $jsSrc)) {
    $jsSrc = Join-Path $RootDir "models\glassmorphic\web\script.js"
}

if (Test-Path $cssSrc) { Copy-Item -Path $cssSrc -Destination (Join-Path $distWeb "assets\style.css") -Force }
if (Test-Path $jsSrc) { Copy-Item -Path $jsSrc -Destination (Join-Path $distWeb "assets\script.js") -Force }

$docsDir = Join-Path $RootDir "docs"
$mdFiles = Get-ChildItem -Path $docsDir -Filter "*.md" -Recurse | Sort-Object {
    [regex]::Replace($_.FullName, '\d+', { $args[0].Value.PadLeft(8, '0') })
}

function Get-Slug([string]$text) {
    $clean = [System.Text.Encoding]::ASCII.GetString([System.Text.Encoding]::GetEncoding("Cyrillic").GetBytes($text))
    $clean = $clean.ToLower() -replace '[^\w\s-]', '' -replace '[\s_]+', '-'
    return $clean.Trim('-')
}

function Convert-MdContent([string]$md) {
    $lines = $md -split "\r?\n"
    $res = [System.Collections.Generic.List[string]]::new()
    $inCode = $false
    $inList = $false

    foreach ($l in $lines) {
        $trim = $l.Trim()

        if ($trim.StartsWith('```')) {
            if (-not $inCode) {
                $inCode = $true
                $res.Add('<pre><code>')
            } else {
                $inCode = $false
                $res.Add('</code></pre>')
            }
            continue
        }

        if ($inCode) {
            $esc = [System.Security.SecurityElement]::Escape($l)
            $res.Add($esc)
            continue
        }

        if ([string]::IsNullOrWhiteSpace($trim)) {
            if ($inList) {
                $res.Add('</ul>')
                $inList = $false
            }
            continue
        }

        if ($trim -match '^#{1,6}\s+(.+)$') {
            if ($inList) { $res.Add('</ul>'); $inList = $false }
            $lvl = ($trim -replace '^([#]+).*', '$1').Length
            $htext = [regex]::Replace($Matches[1].Trim(), '\{#.*?\}', '')
            $res.Add("<h$lvl>$htext</h$lvl>")
            continue
        }

        if ($trim -match '^[-*]\s+(.+)$') {
            if (-not $inList) {
                $inList = $true
                $res.Add('<ul class="doc-list">')
            }
            $item = $Matches[1]
            $item = [regex]::Replace($item, '\*\*(.*?)\*\*', '<strong>$1</strong>')
            $item = [regex]::Replace($item, '`([^`]+)`', '<code>$1</code>')
            $res.Add("<li>$item</li>")
            continue
        }

        $p = $trim
        $p = [regex]::Replace($p, '!\[(.*?)\]\((.*?)\)', '<img src="$2" alt="$1" class="doc-img" />')
        $p = [regex]::Replace($p, '(?<!!)\[(.*?)\]\((.*?)\)', '<a href="$2">$1</a>')
        $p = [regex]::Replace($p, '\*\*(.*?)\*\*', '<strong>$1</strong>')
        $p = [regex]::Replace($p, '\*(.*?)\*', '<em>$1</em>')
        $p = [regex]::Replace($p, '`([^`]+)`', '<code>$1</code>')
        $res.Add("<p>$p</p>")
    }

    if ($inList) { $res.Add('</ul>') }
    return ($res -join "`n")
}

$sidebarHtml = [System.Collections.Generic.List[string]]::new()
$cardsHtml = [System.Collections.Generic.List[string]]::new()
$currentSec = $null

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

    if ($content -match '(?ms)^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$') {
        $body = $Matches[2]
        if ($Matches[1] -match 'title:\s*["\x27]?([^"\x27\r\n]+)') {
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

    if ($section -ne $currentSec) {
        if ($currentSec -ne $null) { $sidebarHtml.Add('</ul>') }
        $currentSec = $section
        $sidebarHtml.Add("<div class=""sidebar-section-title"">$section</div>")
        $sidebarHtml.Add('<ul class="sidebar-nav">')
    }

    $sidebarHtml.Add("<li class=""sidebar-nav-item""><a href=""#$slug"" class=""sidebar-nav-link"">$title</a></li>")

    $htmlBody = Convert-MdContent $body

    $cardItem = @"
    <section id="$slug" class="content-card">
        <div class="content-card-header">
            <span class="badge-tag">$section</span>
            <span style="font-size:0.8rem; color:var(--text-muted);">$rel</span>
        </div>
        <div class="doc-card-body">
            $htmlBody
        </div>
    </section>
"@
    $cardsHtml.Add($cardItem)
}

if ($currentSec -ne $null) {
    $sidebarHtml.Add('</ul>')
}

$sidebarStr = $sidebarHtml -join "`n"
$cardsStr = $cardsHtml -join "`n"

# # Generate base docs-i18n.json (pt-BR)
$baseDocs = @()
foreach ($file in $mdFiles) {
    $rel = $file.FullName.Substring($docsDir.Length).TrimStart('\', '/')
    $parts = $rel.Split([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $section = if ($parts.Count -gt 1) { ([regex]::Replace($parts[0], '^\d+[-_.]*', '') -replace '[-_]', ' ') } else { "General" }
    $section = (Get-Culture).TextInfo.ToTitleCase($section)

    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $title = ""
    $body = $content

    if ($content -match '(?ms)^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$') {
        $body = $Matches[2]
        if ($Matches[1] -match 'title:\s*["\x27]?([^"\x27\r\n]+)') { $title = $Matches[1].Trim() }
    }
    if ([string]::IsNullOrWhiteSpace($title)) {
        if ($body -match '(?m)^#\s+(.+)$') { $title = $Matches[1].Trim() }
        else { $title = [System.IO.Path]::GetFileNameWithoutExtension($file.Name) -replace '^\d+[-_.]*', '' -replace '[-_]', ' ' }
    }
    $slug = Get-Slug "$section-$title"
    $htmlBody = Convert-MdContent $body

    $baseDocs += [ordered]@{
        slug = $slug
        section = $section
        title = $title
        body = $body
        html_body = $htmlBody
    }
}

$i18nDict = [ordered]@{
    "pt-BR" = $baseDocs
}

$distData = Join-Path $distWeb "data"
New-Item -ItemType Directory -Path $distData -Force | Out-Null
$i18nJsonPath = Join-Path $distData "docs-i18n.json"
$i18nDict | ConvertTo-Json -Depth 5 | Set-Content -Path $i18nJsonPath -Encoding UTF8
Write-Host "  [OK] Base language dataset (pt-BR) generated: $i18nJsonPath" -ForegroundColor Green

$fullHtml = @"
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocShell - Documentação Técnica (v1.0)</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <header class="doc-header">
        <a href="#" class="brand-container">
            <img src="images/logo.svg" alt="Logo" class="brand-logo" onerror="this.style.display='none'">
            <span class="brand-title">Doc<span>Shell</span></span>
            <span class="badge-tag">v1.0</span>
        </a>
        
        <div class="search-container">
            <span class="search-icon">&#128269;</span>
            <input type="text" id="docSearchInput" class="search-input" placeholder="Pesquisar documenta&ccedil;&atilde;o (Ctrl+K)...">
        </div>

        <div class="header-actions">
            <!-- 9-Language Selector with clean HTML entities -->
            <select id="docLocaleSelector" class="locale-select" title="Select Language">
                <option value="pt-BR" selected>&#127463;&#127479; Portugu&ecirc;s</option>
                <option value="en-US">&#127482;&#127480; English</option>
                <option value="es">&#127466;&#127480; Espa&ntilde;ol</option>
                <option value="fr">&#127467;&#127479; Fran&ccedil;ais</option>
                <option value="de">&#127465;&#127466; Deutsch</option>
                <option value="it">&#127470;&#127481; Italiano</option>
                <option value="zh-CN">&#127464;&#127475; &#31616;&#20307;&#20013;&#25991;</option>
                <option value="ja">&#127471;&#127477; &#26085;&#26412;&#35486;</option>
                <option value="ru">&#127479;&#127482; &#1056;&#1091;&#1089;&#1089;&#1082;&#1080;&#1081;</option>
            </select>
            <span style="font-size:0.85rem; color:var(--text-secondary);">Runtime: <strong>$Lang</strong></span>
        </div>
    </header>

    <div class="doc-wrapper">
        <aside class="doc-sidebar">
            <div style="margin-bottom:1.5rem;">
                <h3 id="navTitle" style="font-size:1.1rem; color:#fff; font-weight:700;">Navega&ccedil;&atilde;o</h3>
                <p style="font-size:0.8rem; color:var(--text-muted);">$($mdFiles.Count) documentos carregados</p>
            </div>
            $sidebarStr
        </aside>

        <main class="doc-main">
            $cardsStr
        </main>
    </div>

    <!-- Floating AI Assistant Widget -->
    <div class="ai-assistant-widget">
        <button id="aiToggleBtn" class="ai-toggle-btn">
            <span>&#10024; Assistente IA</span>
        </button>

        <div id="aiChatBox" class="ai-chat-box hidden">
            <div class="ai-chat-header">
                <div class="ai-chat-title">
                    <span class="ai-status-indicator"></span>
                    <span>DocShell AI Assistant</span>
                </div>
                <button id="aiCloseBtn" class="ai-chat-close">&times;</button>
            </div>
            <div id="aiMessages" class="ai-chat-messages">
                <div class="chat-msg assistant">
                    Ol&aacute;! Sou o assistente de IA do DocShell. Fa&ccedil;a qualquer pergunta sobre a arquitetura, instala&ccedil;&atilde;o, comandos ou temas!
                </div>
            </div>
            <div class="ai-chat-input-area">
                <input type="text" id="aiChatInput" class="ai-chat-input" placeholder="Fa&ccedil;a uma pergunta sobre a documenta&ccedil;&atilde;o...">
                <button id="aiSendBtn" class="ai-chat-send">&#10148;</button>
            </div>
        </div>
    </div>

    <script src="assets/script.js"></script>
</body>
</html>
"@

$indexHtmlPath = Join-Path $distWeb "index.html"
[System.IO.File]::WriteAllText($indexHtmlPath, $fullHtml, [System.Text.UTF8Encoding]::new($false))
Copy-Item -Path (Join-Path $RootDir "publication\search_index.json") -Destination (Join-Path $distWeb "search_index.json") -Force

Write-Host "  [OK] Website generated successfully: $indexHtmlPath" -ForegroundColor Green
