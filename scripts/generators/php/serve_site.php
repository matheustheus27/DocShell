<?php
/**
 * DocShell PHP Server Starter
 */
$port = $argv[1] ?? 8000;
$rootDir = dirname(__DIR__, 3);
$routerPath = __DIR__ . '/router.php';
$distWeb = $rootDir . '/dist/webpage';

echo "=================================================================\n";
echo "🐘 DocShell PHP Server & API\n";
echo "   URL: http://127.0.0.1:{$port}\n";
echo "   Doc Root: {$distWeb}\n";
echo "   Pressione Ctrl+C para encerrar.\n";
echo "=================================================================\n";

passthru("php -S 0.0.0.0:{$port} " . escapeshellarg($routerPath));
