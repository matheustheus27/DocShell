#!/usr/bin/env node
/**
 * DocShell Web Generator - JavaScript (Node.js) Engine
 * Compila o site em dist/webpage usando Node.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const rootDir = path.resolve(__dirname, '../../../');
const distWeb = path.join(rootDir, 'dist', 'webpage');
const imagesDir = path.join(rootDir, 'images');

// Processa argumentos CLI
let modelName = 'glassmorphic';
process.argv.forEach((arg, i) => {
  if ((arg === '-m' || arg === '--model') && process.argv[i + 1]) {
    modelName = process.argv[i + 1];
  }
});

console.log('=================================================================');
console.log('⚡ DocShell JavaScript (Node.js) Web Generator');
console.log(`   Modelo visual : ${modelName}`);
console.log(`   Destino       : ${distWeb}`);
console.log('=================================================================');

// 1. Garante pastas
if (fs.existsSync(distWeb)) {
  fs.rmSync(distWeb, { recursive: true, force: true });
}
fs.mkdirSync(distWeb, { recursive: true });
fs.mkdirSync(path.join(distWeb, 'images'), { recursive: true });
fs.mkdirSync(path.join(distWeb, 'assets'), { recursive: true });

// 2. Copia imagens
if (fs.existsSync(imagesDir)) {
  fs.readdirSync(imagesDir).forEach(file => {
    const src = path.join(imagesDir, file);
    if (fs.lstatSync(src).isFile()) {
      fs.copyFileSync(src, path.join(distWeb, 'images', file));
    }
  });
  console.log('✅ Imagens copiadas para dist/webpage/images/');
}

// 3. Copia assets do modelo
let modelDir = path.join(rootDir, 'models', modelName.toLowerCase());
if (!fs.existsSync(modelDir)) {
  modelDir = path.join(rootDir, 'models', 'glassmorphic');
}

const cssSrc = path.join(modelDir, 'web', 'style.css');
const jsSrc = path.join(modelDir, 'web', 'script.js');

if (fs.existsSync(cssSrc)) fs.copyFileSync(cssSrc, path.join(distWeb, 'assets', 'style.css'));
if (fs.existsSync(jsSrc)) {
  fs.copyFileSync(jsSrc, path.join(distWeb, 'assets', 'script.js'));
} else {
  const fallbackJs = path.join(rootDir, 'models', 'glassmorphic', 'web', 'script.js');
  if (fs.existsSync(fallbackJs)) fs.copyFileSync(fallbackJs, path.join(distWeb, 'assets', 'script.js'));
}

// 4. Executa Python core parser para garantir sincronização de markdown e search_index
try {
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  execSync(`${pythonCmd} "${path.join(rootDir, 'scripts', 'generators', 'python', 'build_site.py')}" -m "${modelName}"`, {
    stdio: 'inherit',
    cwd: rootDir
  });
  console.log('✅ Compilação JS finalizada com sucesso!');
} catch (err) {
  console.error('⚠️ Execução de sincronização concluída com avisos:', err.message);
}
