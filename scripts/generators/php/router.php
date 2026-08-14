<?php
/**
 * DocShell PHP Built-in Web Server Router
 */
$uri = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH));
$distDir = dirname(__DIR__, 3) . '/dist/webpage';
$file = $distDir . $uri;

// Endpoints de API RAG
if ($uri === '/api/status') {
    header('Content-Type: application/json; charset=utf-8');
    header('Access-Control-Allow-Origin: *');
    echo json_encode([
        'status' => 'online',
        'runtime' => 'php',
        'php_version' => PHP_VERSION,
        'rag_enabled' => true
    ]);
    exit;
}

if ($uri === '/api/chat') {
    header('Content-Type: application/json; charset=utf-8');
    header('Access-Control-Allow-Origin: *');
    $input = json_decode(file_get_contents('php://input'), true);
    $msg = $input['message'] ?? '';
    
    $indexFile = $distDir . '/search_index.json';
    $searchIndex = file_exists($indexFile) ? json_decode(file_get_contents($indexFile), true) : [];
    $terms = array_filter(explode(' ', strtolower($msg)), function($t) { return strlen($t) > 2; });
    $found = [];

    foreach ($searchIndex as $chunk) {
        $text = strtolower($chunk['text'] . ' ' . $chunk['chunk_title'] . ' ' . $chunk['doc_title']);
        $score = 0;
        foreach ($terms as $t) {
            if (strpos($text, $t) !== false) {
                $score++;
            }
        }
        if ($score > 0) {
            $found[] = ['score' => $score, 'chunk' => $chunk];
        }
    }

    usort($found, function($a, $b) { return $b['score'] - $a['score']; });

    if (!empty($found)) {
        $top = $found[0]['chunk'];
        $resp = "**Resultado (Engine PHP):**\n\nNo documento **{$top['doc_title']}** (Seção: *{$top['chunk_title']}*):\n\n> {$top['text']}";
        echo json_encode(['response' => $resp, 'sources' => [$top['doc_title']], 'runtime' => 'php']);
    } else {
        echo json_encode(['response' => 'Nenhum trecho correspondente encontrado na documentação.', 'sources' => [], 'runtime' => 'php']);
    }
    exit;
}

// Arquivos estáticos
if ($uri !== '/' && file_exists($file) && !is_dir($file)) {
    return false; // Deixa o PHP servir o arquivo estático
}

// Fallback index.html
if (file_exists($distDir . '/index.html')) {
    readfile($distDir . '/index.html');
} else {
    echo "<h1>DocShell PHP Server</h1><p>Gere o site primeiro executando: <code>task site -l PHP</code></p>";
}
