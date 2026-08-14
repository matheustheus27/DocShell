#!/usr/bin/env node
/**
 * DocShell JavaScript (Node.js) Web Server & RAG API
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const rootDir = path.resolve(__dirname, '../../../');
const distWeb = path.join(rootDir, 'dist', 'webpage');
let port = 8000;

process.argv.forEach((arg, i) => {
  if ((arg === '-p' || arg === '--port') && process.argv[i + 1]) {
    port = parseInt(process.argv[i + 1], 10);
  }
});

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // API Status
  if (pathname === '/api/status' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({
      status: 'online',
      runtime: 'javascript (node.js)',
      node_version: process.version,
      rag_enabled: true
    }));
    return;
  }

  // API Chat / RAG
  if (pathname === '/api/chat' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        const query = (payload.message || '').toLowerCase();
        
        const indexPath = path.join(distWeb, 'search_index.json');
        let searchIndex = [];
        if (fs.existsSync(indexPath)) {
          searchIndex = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
        }

        const terms = query.split(/\s+/).filter(t => t.length > 2);
        let matches = [];

        searchIndex.forEach(item => {
          const text = (item.text + ' ' + item.chunk_title + ' ' + item.doc_title).toLowerCase();
          let score = 0;
          terms.forEach(t => {
            if (text.includes(t)) score++;
          });
          if (score > 0) matches.push({ score, item });
        });

        matches.sort((a, b) => b.score - a.score);

        if (matches.length > 0) {
          const top = matches[0].item;
          const resp = `**Resultado (Node.js RAG Engine):**\n\nNo documento **${top.doc_title}** (Seção: *${top.chunk_title}*):\n\n> ${top.text}`;
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ response: resp, sources: [top.doc_title], runtime: 'node-rag' }));
        } else {
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ response: 'Não encontrei trechos correspondentes nesta consulta.', sources: [], runtime: 'node-rag' }));
        }
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // Servir arquivos estáticos
  let safePath = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
  let filePath = path.join(distWeb, safePath === '/' ? 'index.html' : safePath);

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found - DocShell');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = mimeTypes[ext] || 'application/octet-stream';

    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
});

console.log('=================================================================');
console.log('⚡ DocShell Node.js Server & API');
console.log(`   URL: http://127.0.0.1:${port}`);
console.log(`   Doc Root: ${distWeb}`);
console.log('   Pressione Ctrl+C para encerrar.');
console.log('=================================================================');

server.listen(port, '0.0.0.0');
