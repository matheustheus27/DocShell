/**
 * DocShell - Client Interactive Engine & AI Chatbot
 * Multi-Language Localization Engine (9 Locales)
 * Real-time Markdown Chat Formatter, Source Deep-linking & Browser Locale Detection
 */

const DOCSHELL_I18N = {
  "pt-BR": {
    "search_placeholder": "Pesquisar documentação (Ctrl+K)...",
    "nav_title": "Navegação",
    "docs_loaded": "documentos carregados",
    "ai_btn": "✨ Assistente IA",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "Olá! Sou o assistente de IA do DocShell. Faça qualquer pergunta sobre arquitetura, comandos, temas ou instalação!",
    "ai_input_placeholder": "Faça uma pergunta sobre a documentação...",
    "copy_btn": "Copiar",
    "copied_btn": "Copiado!",
    "sources_label": "📚 Fontes:",
    "offline_notice": "💡 Dica: Para respostas geradas por IA em tempo real, inicie o Ollama com o modelo configurado."
  },
  "en-US": {
    "search_placeholder": "Search documentation (Ctrl+K)...",
    "nav_title": "Navigation",
    "docs_loaded": "documents loaded",
    "ai_btn": "✨ AI Assistant",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "Hello! I am your AI assistant for DocShell documentation. Ask any question about architecture, commands, themes, or deployment!",
    "ai_input_placeholder": "Ask a question about the docs...",
    "copy_btn": "Copy",
    "copied_btn": "Copied!",
    "sources_label": "📚 Sources:",
    "offline_notice": "💡 Tip: For real-time AI generation, start Ollama with your configured model."
  },
  "es": {
    "search_placeholder": "Buscar en la documentación (Ctrl+K)...",
    "nav_title": "Navegación",
    "docs_loaded": "documentos cargados",
    "ai_btn": "✨ Asistente IA",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "¡Hola! Soy tu asistente de IA para DocShell. ¡Pregunta lo que quieras sobre arquitectura, comandos o temas!",
    "ai_input_placeholder": "Haz una pergunta sobre los documentos...",
    "copy_btn": "Copiar",
    "copied_btn": "¡Copiado!",
    "sources_label": "📚 Fuentes:",
    "offline_notice": "💡 Consejo: Inicia Ollama para respuestas generadas por IA."
  },
  "fr": {
    "search_placeholder": "Rechercher dans la documentation (Ctrl+K)...",
    "nav_title": "Navigation",
    "docs_loaded": "documents chargés",
    "ai_btn": "✨ Assistant IA",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "Bonjour ! Je suis votre assistant IA pour DocShell. Posez vos questions sur l'architecture, les commandes ou les thèmes !",
    "ai_input_placeholder": "Posez une question sur la documentation...",
    "copy_btn": "Copier",
    "copied_btn": "Copié !",
    "sources_label": "📚 Sources :",
    "offline_notice": "💡 Conseil : Démarrez Ollama pour des réponses IA en direct."
  },
  "de": {
    "search_placeholder": "Dokumentation durchsuchen (Strg+K)...",
    "nav_title": "Navigation",
    "docs_loaded": "Dokumente geladen",
    "ai_btn": "✨ KI-Assistent",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "Hallo! Ich bin Ihr KI-Assistent für DocShell. Stellen Sie beliebige Fragen zu Architektur, Befehlen oder Themes!",
    "ai_input_placeholder": "Frage zur Dokumentation stellen...",
    "copy_btn": "Kopieren",
    "copied_btn": "Kopiert!",
    "sources_label": "📚 Quellen:",
    "offline_notice": "💡 Tipp: Starten Sie Ollama für KI-generierte Antworten."
  },
  "it": {
    "search_placeholder": "Cerca nella documentazione (Ctrl+K)...",
    "nav_title": "Navigazione",
    "docs_loaded": "documenti caricati",
    "ai_btn": "✨ Assistente IA",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "Ciao! Sono l'assistente IA di DocShell. Fai qualsiasi domanda su architettura, comandi o temi!",
    "ai_input_placeholder": "Fai una domanda sulla documentazione...",
    "copy_btn": "Copia",
    "copied_btn": "Copiato!",
    "sources_label": "📚 Fonti:",
    "offline_notice": "💡 Suggerimento: Avvia Ollama per risposte generate dall'IA."
  },
  "zh-CN": {
    "search_placeholder": "搜索文档 (Ctrl+K)...",
    "nav_title": "导航",
    "docs_loaded": "个文档已加载",
    "ai_btn": "✨ AI 助手",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "您好！我是 DocShell 文档 AI 助手。欢迎随时询问关于系统架构、命令、主题或部署的问题！",
    "ai_input_placeholder": "输入关于文档的问题...",
    "copy_btn": "复制",
    "copied_btn": "已复制!",
    "sources_label": "📚 参考来源:",
    "offline_notice": "💡 提示: 启动 Ollama 可获得实时 AI 生成回答。"
  },
  "ja": {
    "search_placeholder": "ドキュメントを検索 (Ctrl+K)...",
    "nav_title": "ナビゲーション",
    "docs_loaded": "件のドキュメントを読み込みました",
    "ai_btn": "✨ AI アシスタント",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "こんにちは！DocShell ドキュメント AI アシスタントです。アーキテクチャやコマンド、テーマについて何でもお聞きください！",
    "ai_input_placeholder": "ドキュメントについて質問する...",
    "copy_btn": "コピー",
    "copied_btn": "コピー完了!",
    "sources_label": "📚 参照ソース:",
    "offline_notice": "💡 ヒント: Ollama を起動するとリアルタイム AI 回答が有効になります。"
  },
  "ru": {
    "search_placeholder": "Поиск по документации (Ctrl+K)...",
    "nav_title": "Навигация",
    "docs_loaded": "документов загружено",
    "ai_btn": "✨ ИИ-Ассистент",
    "ai_title": "DocShell AI Assistant",
    "ai_greeting": "Здравствуйте! Я ИИ-ассистент документации DocShell. Задавайте любые вопросы по архитектуре, командам и темам оформления!",
    "ai_input_placeholder": "Задайте вопрос по документации...",
    "copy_btn": "Копировать",
    "copied_btn": "Скопировано!",
    "sources_label": "📚 Источники:",
    "offline_notice": "💡 Совет: Запустите Ollama для генерации ответов ИИ."
  }
};

let i18nData = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadTranslationsData();
  initLocaleSelector();
  initSearch();
  initTocSpy();
  initCopyCode();
  initAiAssistant();
});

// Load multi-language translated doc datasets if available
async function loadTranslationsData() {
  try {
    const res = await fetch('data/docs-i18n.json');
    if (res.ok) {
      i18nData = await res.json();
    }
  } catch (e) {
    // If not separate file, client uses embedded content
  }
}

// Detect user's preferred locale from browser or localStorage
function detectUserLocale() {
  const saved = localStorage.getItem('docshell_locale');
  if (saved && DOCSHELL_I18N[saved]) return saved;

  const navLang = (navigator.language || navigator.userLanguage || 'pt-BR').toLowerCase();
  if (navLang.startsWith('pt')) return 'pt-BR';
  if (navLang.startsWith('es')) return 'es';
  if (navLang.startsWith('fr')) return 'fr';
  if (navLang.startsWith('de')) return 'de';
  if (navLang.startsWith('it')) return 'it';
  if (navLang.startsWith('zh')) return 'zh-CN';
  if (navLang.startsWith('ja')) return 'ja';
  if (navLang.startsWith('ru')) return 'ru';
  if (navLang.startsWith('en')) return 'en-US';

  return 'pt-BR'; // Default to Portuguese
}

// Localization switcher
function initLocaleSelector() {
  const select = document.getElementById('docLocaleSelector');
  if (!select) return;

  const currentLocale = detectUserLocale();
  select.value = currentLocale;
  applyLocale(currentLocale);

  select.addEventListener('change', (e) => {
    const newLocale = e.target.value;
    localStorage.setItem('docshell_locale', newLocale);
    applyLocale(newLocale);
  });
}

async function applyLocale(locale) {
  const dict = DOCSHELL_I18N[locale] || DOCSHELL_I18N['pt-BR'];

  const searchInput = document.getElementById('docSearchInput');
  if (searchInput) searchInput.placeholder = dict.search_placeholder;

  const navTitle = document.getElementById('navTitle');
  if (navTitle) navTitle.innerText = dict.nav_title;

  const aiBtn = document.getElementById('aiToggleBtn');
  if (aiBtn) {
    const span = aiBtn.querySelector('span');
    if (span) span.innerText = dict.ai_btn;
  }

  const aiChatTitle = document.querySelector('.ai-chat-title span:last-child');
  if (aiChatTitle) aiChatTitle.innerText = dict.ai_title;

  const aiInput = document.getElementById('aiChatInput');
  if (aiInput) aiInput.placeholder = dict.ai_input_placeholder;

  const firstAssistantMsg = document.querySelector('#aiMessages .chat-msg.assistant');
  if (firstAssistantMsg && dict.ai_greeting) {
    firstAssistantMsg.innerHTML = dict.ai_greeting;
  }

  function cleanSectionName(sec) {
    if (!sec) return 'General';
    if (sec.includes('CRITICAL RULES') || sec.includes('Preserve ALL') || sec.includes('Content to translate') || sec.length > 40) {
      return 'General';
    }
    return sec;
  }

  function renderDocsList(docs) {
    if (!docs || !Array.isArray(docs)) return;
    const sectionNames = {};
    docs.forEach(d => {
      const card = document.getElementById(d.slug);
      const safeSection = cleanSectionName(d.section);
      if (card) {
        const badge = card.querySelector('.badge-tag');
        if (badge) badge.innerText = safeSection;

        const cardBody = card.querySelector('.doc-card-body');
        if (cardBody && d.html_body) {
          cardBody.innerHTML = d.html_body;
        }
      }

      const navLink = document.querySelector(`a.sidebar-nav-link[href="#${d.slug}"]`);
      if (navLink && d.title) {
        navLink.innerText = d.title;
      }
      if (safeSection) {
        sectionNames[safeSection.toLowerCase()] = safeSection;
      }
    });

    // Also update section titles in sidebar if matching
    document.querySelectorAll('.sidebar-section-title').forEach(st => {
      const currentText = st.innerText.trim().toLowerCase();
      if (sectionNames[currentText]) {
        st.innerText = sectionNames[currentText];
      }
    });
  }

  // 1. If available in memory cache
  if (i18nData && i18nData[locale]) {
    const isPoisoned = i18nData[locale].some(d => (d.section && d.section.includes('CRITICAL RULES')) || (d.html_body && d.html_body.includes('CRITICAL RULES')));
    if (!isPoisoned) {
      renderDocsList(i18nData[locale]);
      return;
    }
    delete i18nData[locale];
  }

  // 2. If available in LocalStorage cache (validate that it's not a stale Portuguese copy or poisoned)
  const localCached = localStorage.getItem('docshell_trans_' + locale);
  if (localCached) {
    try {
      const parsedDocs = JSON.parse(localCached);
      const isStalePt = (locale !== 'pt-BR' && Array.isArray(parsedDocs) && parsedDocs.length > 0 && parsedDocs[0].title === 'Capa e Identificação');
      const isPoisoned = Array.isArray(parsedDocs) && parsedDocs.some(d => (d.section && d.section.includes('CRITICAL RULES')) || (d.html_body && d.html_body.includes('CRITICAL RULES')));
      
      if (!isStalePt && !isPoisoned && Array.isArray(parsedDocs) && parsedDocs.length > 0) {
        if (!i18nData) i18nData = {};
        i18nData[locale] = parsedDocs;
        renderDocsList(parsedDocs);
        return;
      } else {
        localStorage.removeItem('docshell_trans_' + locale);
      }
    } catch (e) {}
  }

  if (locale === 'pt-BR') {
    if (i18nData && i18nData['pt-BR']) {
      renderDocsList(i18nData['pt-BR']);
    }
    return;
  }

  // 3. Dynamic On-Demand Translation via TranslateGemma & Redis Backend
  let toast = document.getElementById('translationToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'translationToast';
    toast.style.cssText = 'position:fixed; bottom:20px; left:20px; z-index:9999; background:rgba(30,41,59,0.92); border:1px solid rgba(99,102,241,0.4); backdrop-filter:blur(12px); color:#e2e8f0; padding:10px 16px; border-radius:8px; font-size:13px; display:flex; align-items:center; gap:8px; box-shadow:0 10px 25px rgba(0,0,0,0.5); transition:opacity 0.3s ease;';
    document.body.appendChild(toast);
  }
  const toastMsg = locale === 'pt-BR' ? 'Carregando documentação...' : 'Traduzindo documentação com IA & Redis...';
  toast.innerHTML = `<span class="loading-spin" style="display:inline-block; animation:spin 1s linear infinite;">⏳</span> <span>${toastMsg}</span>`;
  toast.style.opacity = '1';

  try {
    const res = await fetch('/api/docs?locale=' + encodeURIComponent(locale));
    if (res.ok) {
      const data = await res.json();
      if (data && data.docs && Array.isArray(data.docs) && data.docs.length > 0) {
        if (!i18nData) i18nData = {};
        i18nData[locale] = data.docs;
        
        // Only persist if translation succeeded
        const isStalePt = (locale !== 'pt-BR' && data.docs[0].title === 'Capa e Identificação');
        if (!isStalePt) {
          try {
            localStorage.setItem('docshell_trans_' + locale, JSON.stringify(data.docs));
          } catch (storageErr) {}
        }
        renderDocsList(data.docs);
      }
    }
  } catch (err) {
    console.warn('TranslateGemma on-demand translation fetch error:', err);
  } finally {
    if (toast) {
      toast.style.opacity = '0';
      setTimeout(() => { if (toast && toast.parentNode) toast.remove(); }, 350);
    }
  }
}

// Smooth navigation and card highlight from chat links
window.navigateToSection = function (slug) {
  if (!slug) return;
  const target = document.getElementById(slug);
  if (target) {
    const headerHeight = 80;
    const elementPosition = target.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - headerHeight;
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
    target.classList.add('highlight-card');
    setTimeout(() => {
      target.classList.remove('highlight-card');
    }, 2500);
  }
};

// Robust client-side Markdown formatter for chat bubbles
function formatMarkdown(text) {
  if (!text) return '';

  let html = text.replace(/\r\n/g, '\n');

  // Handle Code Blocks first
  const codeBlocks = [];
  html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (m, lang, code) => {
    const idx = codeBlocks.length;
    const escCode = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    codeBlocks.push(`<pre><code class="language-${lang}">${escCode}</code></pre>`);
    return `%%%CODEBLOCK_${idx}%%%`;
  });

  // Handle inline code
  const inlineCodes = [];
  html = html.replace(/`([^`]+)`/g, (m, code) => {
    const idx = inlineCodes.length;
    const escCode = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    inlineCodes.push(`<code>${escCode}</code>`);
    return `%%%INLINECODE_${idx}%%%`;
  });

  // Markdown Links [title](#slug)
  html = html.replace(/\[([^\]]+)\]\((#[^)]+)\)/g, (match, p1, p2) => {
    const slug = p2.replace(/^#/, '');
    return `<a href="${p2}" class="chat-link" onclick="event.preventDefault(); navigateToSection('${slug}');">${p1}</a>`;
  });
  // External links
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" class="chat-link" target="_blank" rel="noopener">$1</a>');

  // Bold & Italic
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // Blockquotes (> text)
  html = html.replace(/^>\s*(.+)$/gm, '<blockquote class="chat-quote">$1</blockquote>');

  // Headers (### Heading)
  html = html.replace(/^###\s+(.+)$/gm, '<h4 style="margin:0.5rem 0 0.25rem 0; font-size:0.95rem; color:#67e8f9;">$1</h4>');
  html = html.replace(/^##\s+(.+)$/gm, '<h3 style="margin:0.5rem 0 0.25rem 0; font-size:1.05rem; color:#38bdf8;">$1</h3>');

  // Unordered list items (- item)
  html = html.replace(/^[-*]\s+(.+)$/gm, '<li style="margin-left:1rem;">$1</li>');

  // Paragraphs
  html = html.replace(/\n\n+/g, '</p><p>');
  html = html.replace(/\n/g, '<br/>');

  // Restore Code Blocks and inline code
  codeBlocks.forEach((block, idx) => {
    html = html.replace(`%%%CODEBLOCK_${idx}%%%`, block);
  });
  inlineCodes.forEach((code, idx) => {
    html = html.replace(`%%%INLINECODE_${idx}%%%`, code);
  });

  return '<div class="chat-text">' + html + '</div>';
}

// Real-time client search filter
function initSearch() {
  const searchInput = document.getElementById('docSearchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase().trim();
    const cards = document.querySelectorAll('.content-card');
    const navItems = document.querySelectorAll('.sidebar-nav-item');

    cards.forEach(card => {
      const text = card.innerText.toLowerCase();
      if (!term || text.includes(term)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });

    navItems.forEach(item => {
      const text = item.innerText.toLowerCase();
      if (!term || text.includes(term)) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  });

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
  });
}

// Scroll spy for TOC
function initTocSpy() {
  const links = document.querySelectorAll('.sidebar-nav-link');
  const sections = document.querySelectorAll('section[id], h1[id], h2[id]');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
      const top = section.offsetTop - 120;
      if (window.pageYOffset >= top) {
        current = section.getAttribute('id');
      }
    });

    links.forEach(link => {
      link.classList.remove('active');
      if (current && link.getAttribute('href').includes(current)) {
        link.classList.add('active');
      }
    });
  });
}

// Copy Code Blocks
function initCopyCode() {
  const codeBlocks = document.querySelectorAll('pre');
  const locale = detectUserLocale();
  const dict = DOCSHELL_I18N[locale] || DOCSHELL_I18N['pt-BR'];

  codeBlocks.forEach(pre => {
    if (pre.querySelector('.copy-code-btn')) return;

    const btn = document.createElement('button');
    btn.className = 'copy-code-btn';
    btn.innerText = dict.copy_btn;
    btn.style.cssText = 'position:absolute; top:8px; right:8px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#cbd5e1; font-size:11px; padding:4px 8px; border-radius:4px; cursor:pointer;';

    pre.style.position = 'relative';
    pre.appendChild(btn);

    btn.addEventListener('click', async () => {
      const code = pre.querySelector('code') ? pre.querySelector('code').innerText : pre.innerText;
      try {
        await navigator.clipboard.writeText(code);
        btn.innerText = dict.copied_btn;
        btn.style.background = '#10b981';
        btn.style.color = '#fff';
        setTimeout(() => {
          const currentDict = DOCSHELL_I18N[detectUserLocale()] || DOCSHELL_I18N['pt-BR'];
          btn.innerText = currentDict.copy_btn;
          btn.style.background = 'rgba(255,255,255,0.1)';
          btn.style.color = '#cbd5e1';
        }, 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    });
  });
}

// Client-side offline search fallback
async function performClientSearch(query) {
  try {
    const res = await fetch('search_index.json');
    if (!res.ok) return null;
    const index = await res.json();
    if (!Array.isArray(index) || index.length === 0) return null;

    const terms = query.toLowerCase().split(/\s+/).filter(t => t.length > 2);
    let bestChunk = null;
    let maxScore = 0;

    index.forEach(chunk => {
      let score = 0;
      const text = (chunk.text + ' ' + chunk.chunk_title + ' ' + chunk.doc_title).toLowerCase();
      terms.forEach(t => {
        if (chunk.chunk_title.toLowerCase().includes(t)) score += 5;
        if (chunk.doc_title.toLowerCase().includes(t)) score += 4;
        if (text.includes(t)) score += 1;
      });
      if (score > maxScore) {
        maxScore = score;
        bestChunk = chunk;
      }
    });

    if (bestChunk) {
      return {
        answer: `**Resultado da busca na documentação:**\n\nNa seção [**${bestChunk.chunk_title}**](#${bestChunk.slug}) do documento *${bestChunk.doc_title}*:\n\n> ${bestChunk.text}\n\n*(💡 Dica: Inicie o servidor local com \`task serve\` e o Ollama para respostas sintetizadas por IA em tempo real).*`,
        sources: [{ title: bestChunk.chunk_title, slug: bestChunk.slug }]
      };
    }
  } catch (e) {
    console.warn('Client search fallback error:', e);
  }
  return null;
}

// Floating AI Assistant with Deep-Linking & Markdown Rendering
function initAiAssistant() {
  const toggleBtn = document.getElementById('aiToggleBtn');
  const chatBox = document.getElementById('aiChatBox');
  const closeBtn = document.getElementById('aiCloseBtn');
  const sendBtn = document.getElementById('aiSendBtn');
  const input = document.getElementById('aiChatInput');
  const messages = document.getElementById('aiMessages');

  if (!toggleBtn || !chatBox) return;

  toggleBtn.addEventListener('click', () => {
    chatBox.classList.toggle('hidden');
    if (!chatBox.classList.contains('hidden')) {
      input.focus();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      chatBox.classList.add('hidden');
    });
  }

  async function handleSend() {
    const prompt = input.value.trim();
    if (!prompt) return;

    appendMessage(prompt, 'user', null, false);
    input.value = '';

    const loadingId = 'loading-' + Date.now();
    appendMessage('🔍 Consultando base de conhecimento...', 'assistant', loadingId, false);

    try {
      let data = null;
      try {
        const userLocale = detectUserLocale();
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: prompt, locale: userLocale })
        });
        if (res.ok) {
          data = await res.json();
        }
      } catch (netErr) {
        // Fallback to client-side local search
        data = await performClientSearch(prompt);
      }

      if (!data) {
        data = await performClientSearch(prompt);
      }

      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();

      const rawAnswer = (data && (data.answer || data.response)) ? (data.answer || data.response) : 'Não encontrei informações específicas para esta consulta na documentação.';
      const formattedAnswer = formatMarkdown(rawAnswer);

      // Build clickable sources
      let sourcesHtml = '';
      if (data && data.sources && Array.isArray(data.sources) && data.sources.length > 0) {
        const locale = detectUserLocale();
        const dict = DOCSHELL_I18N[locale] || DOCSHELL_I18N['pt-BR'];

        const badges = data.sources.map(s => {
          if (typeof s === 'object' && s.slug) {
            return `<a href="#${s.slug}" class="chat-source-badge" onclick="event.preventDefault(); navigateToSection('${s.slug}');">📄 ${s.title}</a>`;
          } else {
            const title = typeof s === 'string' ? s : (s.title || 'Documentação');
            return `<span class="chat-source-badge">📄 ${title}</span>`;
          }
        }).join('');

        sourcesHtml = `<div class="chat-sources"><span>${dict.sources_label}</span> ${badges}</div>`;
      }

      appendMessage(formattedAnswer + sourcesHtml, 'assistant', null, true);

    } catch (err) {
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) {
        loadingEl.innerHTML = formatMarkdown('<em>Serviço de busca concluído. Para respostas IA, inicie o Ollama local na porta 11434.</em>');
      }
    }
  }

  if (sendBtn) {
    sendBtn.addEventListener('click', handleSend);
  }
  if (input) {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSend();
    });
  }

  function appendMessage(content, sender, id = null, isHtml = false) {
    const msg = document.createElement('div');
    msg.className = `chat-msg ${sender}`;
    if (id) msg.id = id;
    if (isHtml) {
      msg.innerHTML = content;
    } else {
      msg.innerText = content;
    }
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }
}
