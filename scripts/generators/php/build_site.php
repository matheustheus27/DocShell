<?php
/**
 * DocShell Web Generator - PHP Engine
 * Compila a documentação Markdown em dist/webpage via PHP CLI.
 */

$rootDir = dirname(__DIR__, 3);
$docsDir = $rootDir . '/docs';
$distWeb = $rootDir . '/dist/webpage';
$imagesDir = $rootDir . '/images';
$pubDir = $rootDir . '/publication';

// Carrega modelo e argumentos
$options = getopt("m:l:", ["model:", "lang:"]);
$modelName = $options['m'] ?? $options['model'] ?? 'glassmorphic';

echo "=================================================================\n";
echo "🐘 DocShell PHP Web Generator\n";
echo "   Modelo visual : {$modelName}\n";
echo "   Destino       : {$distWeb}\n";
echo "=================================================================\n";

// Garante diretórios
if (is_dir($distWeb)) {
    $files = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($distWeb, RecursiveDirectoryIterator::SKIP_DOTS),
        RecursiveIteratorIterator::CHILD_FIRST
    );
    foreach ($files as $fileinfo) {
        $todo = ($fileinfo->isDir() ? 'rmdir' : 'unlink');
        @$todo($fileinfo->getRealPath());
    }
}
if (!is_dir($distWeb)) {
    mkdir($distWeb, 0755, true);
}
if (!is_dir($distWeb . '/images')) {
    mkdir($distWeb . '/images', 0755, true);
}
if (!is_dir($distWeb . '/assets')) {
    mkdir($distWeb . '/assets', 0755, true);
}

// 1. Copia imagens
if (is_dir($imagesDir)) {
    foreach (glob($imagesDir . '/*') as $img) {
        if (is_file($img)) {
            copy($img, $distWeb . '/images/' . basename($img));
        }
    }
    echo "✅ Imagens copiadas.\n";
}

// 2. Copia assets do modelo
$modelDir = $rootDir . '/models/' . strtolower($modelName);
if (!is_dir($modelDir)) {
    $modelDir = $rootDir . '/models/glassmorphic';
}

if (file_exists($modelDir . '/web/style.css')) {
    copy($modelDir . '/web/style.css', $distWeb . '/assets/style.css');
}
if (file_exists($modelDir . '/web/script.js')) {
    copy($modelDir . '/web/script.js', $distWeb . '/assets/script.js');
} elseif (file_exists($rootDir . '/models/glassmorphic/web/script.js')) {
    copy($rootDir . '/models/glassmorphic/web/script.js', $distWeb . '/assets/script.js');
}

// 3. Executa o parser core para gerar os dados
$pythonCmd = (DIRECTORY_SEPARATOR === '\\') ? 'python' : 'python3';
exec("{$pythonCmd} " . escapeshellarg($rootDir . '/scripts/core/doc_parser.py'), $output, $retCode);

// 4. Copia index e search_index gerados
if (file_exists($pubDir . '/search_index.json')) {
    copy($pubDir . '/search_index.json', $distWeb . '/search_index.json');
}

// 5. Gera a versão PHP com suporte a servidor
$phpIndexContent = <<<'PHP'
<?php
// DocShell PHP Dynamic & Static Viewer
$distDir = __DIR__;
if ($_SERVER['REQUEST_URI'] === '/api/status') {
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

if ($_SERVER['REQUEST_URI'] === '/api/chat' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    header('Access-Control-Allow-Origin: *');
    $input = json_decode(file_get_contents('php://input'), true);
    $msg = $input['message'] ?? '';
    
    // Busca simples no search_index.json
    $searchIndex = json_decode(file_get_contents($distDir . '/search_index.json'), true) ?: [];
    $found = [];
    $terms = explode(' ', strtolower($msg));
    
    foreach ($searchIndex as $chunk) {
        $text = strtolower($chunk['text'] . ' ' . $chunk['chunk_title']);
        $score = 0;
        foreach ($terms as $t) {
            if (strlen($t) > 2 && strpos($text, $t) !== false) {
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
        $resp = "**Resultado PHP RAG:**\n\nNa seção **{$top['chunk_title']}** ({$top['doc_title']}):\n\n> {$top['text']}";
        echo json_encode(['response' => $resp, 'sources' => [$top['doc_title']], 'runtime' => 'php-rag']);
    } else {
        echo json_encode(['response' => 'Não encontrei correspondência exata para sua busca.', 'sources' => [], 'runtime' => 'php-rag']);
    }
    exit;
}

// Serve o HTML gerado
readfile($distDir . '/index.html');
PHP;

file_put_contents($distWeb . '/index.php', $phpIndexContent);
echo "✅ Site compilado com sucesso com runtime PHP em {$distWeb}/index.php\n";
