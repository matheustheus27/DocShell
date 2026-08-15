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
  initMermaid();
});

// Mermaid.js Diagram Initializer and Renderer
function initMermaid() {
  if (typeof mermaid !== 'undefined') {
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'base',
        themeVariables: {
          darkMode: true,
          background: 'transparent',
          mainBkg: '#0f172a',
          nodeBorder: '#6366f1',
          nodeTextColor: '#f8fafc',
          clusterBkg: 'rgba(30, 41, 59, 0.7)',
          clusterBorder: 'rgba(99, 102, 241, 0.4)',
          defaultLinkColor: '#38bdf8',
          lineColor: '#38bdf8',
          arrowheadColor: '#38bdf8',
          titleColor: '#e0e7ff',
          edgeLabelBackground: '#1e293b',
          actorBkg: '#0f172a',
          actorBorder: '#6366f1',
          actorTextColor: '#f8fafc',
          actorLineColor: '#38bdf8',
          signalColor: '#38bdf8',
          signalTextColor: '#f8fafc',
          labelBoxBkgColor: '#0f172a',
          labelBoxBorderColor: '#6366f1',
          labelTextColor: '#f8fafc',
          loopTextColor: '#f8fafc',
          noteBkgColor: '#1e293b',
          noteBorderColor: '#6366f1',
          noteTextColor: '#f8fafc',
          fontFamily: 'Segoe UI, Roboto, -apple-system, BlinkMacSystemFont, sans-serif',
          fontSize: '13px'
        },
        securityLevel: 'loose'
      });
      renderMermaidDiagrams();
    } catch (err) {
      console.warn('[DocShell] Mermaid initialization warning:', err);
    }
  }
}

async function renderMermaidDiagrams() {
  if (typeof mermaid === 'undefined') return;
  try {
    const nodes = document.querySelectorAll('pre.mermaid:not([data-processed="true"]), div.mermaid:not([data-processed="true"])');
    if (nodes.length > 0) {
      await mermaid.run({
        nodes: Array.from(nodes)
      });
    }
  } catch (err) {
    console.warn('[DocShell] Mermaid render warning:', err);
  }
}

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
    const allCards = document.querySelectorAll('.content-card');
    const allNavLinks = document.querySelectorAll('.sidebar-nav-link');

    docs.forEach((d, idx) => {
      const card = document.getElementById(d.slug) || allCards[idx];
      const safeSection = cleanSectionName(d.section);
      if (card) {
        const badge = card.querySelector('.badge-tag');
        if (badge && safeSection) badge.innerText = safeSection;

        const cardBody = card.querySelector('.doc-card-body');
        if (cardBody && d.html_body) {
          cardBody.innerHTML = d.html_body;
        }
      }

      const navLink = document.querySelector(`a.sidebar-nav-link[href="#${d.slug}"]`) || allNavLinks[idx];
      if (navLink && d.title) {
        navLink.innerText = d.title;
      }
      if (safeSection) {
        sectionNames[safeSection.toLowerCase()] = safeSection;
      }
    });

    // Translate sidebar section titles by inspecting the first document link in each section list
    document.querySelectorAll('.sidebar-section-title').forEach(st => {
      const nextUl = st.nextElementSibling;
      if (nextUl && nextUl.classList.contains('sidebar-nav')) {
        const firstLink = nextUl.querySelector('.sidebar-nav-link');
        if (firstLink) {
          const href = firstLink.getAttribute('href') || '';
          const slug = href.replace(/^#/, '');
          const matchingDoc = docs.find(doc => doc.slug === slug);
          if (matchingDoc && matchingDoc.section) {
            st.innerText = cleanSectionName(matchingDoc.section);
          }
        }
      }
    });

    renderMermaidDiagrams();
    if (typeof initTocSpy === 'function') {
      initTocSpy();
    }
  }

  // 1. If available in memory cache and actually translated
  if (i18nData && i18nData[locale] && Array.isArray(i18nData[locale]) && i18nData[locale].length > 0) {
    const isTranslated = i18nData[locale].every(d => d.is_translated === true);
    const isPoisoned = i18nData[locale].some(d => (d.section && d.section.includes('CRITICAL RULES')) || (d.html_body && d.html_body.includes('CRITICAL RULES')));
    if (isTranslated && !isPoisoned) {
      renderDocsList(i18nData[locale]);
      return;
    }
  }

  // 2. If available in LocalStorage cache (validate that it's completed translation)
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

  // 3. Dynamic On-Demand Translation via Dedicated Worker & RabbitMQ/TranslateGemma
  translationUI.show(locale, 'Tradução iniciada...', `Solicitando processamento para ${locale}`, 0);

  let pollInterval = null;
  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  };

  try {
    const res = await fetch('/api/docs?locale=' + encodeURIComponent(locale));
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'completed' && data.docs && Array.isArray(data.docs) && data.docs.length > 0) {
        if (!i18nData) i18nData = {};
        i18nData[locale] = data.docs;
        try { localStorage.setItem('docshell_trans_' + locale, JSON.stringify(data.docs)); } catch (e) {}
        renderDocsList(data.docs);
        translationUI.show(locale, 'Tradução pronta!', `Documentação carregada em ${locale}.`, 100, true);
        return;
      } else {
        const progress = data.progress || 0;
        translationUI.show(locale, 'Traduzindo documentação...', `Worker TranslateGemma (${progress}% concluído)`, progress);
        
        // Start async polling
        pollInterval = setInterval(async () => {
          try {
            const stRes = await fetch('/api/translations/status?locale=' + encodeURIComponent(locale));
            if (stRes.ok) {
              const stData = await stRes.json();
              if (stData.status === 'completed' && stData.docs && stData.docs.length > 0) {
                stopPolling();
                if (!i18nData) i18nData = {};
                i18nData[locale] = stData.docs;
                try { localStorage.setItem('docshell_trans_' + locale, JSON.stringify(stData.docs)); } catch (e) {}
                renderDocsList(stData.docs);
                translationUI.show(locale, 'Tradução concluída!', `Documentação para ${locale} pronta.`, 100, true);
              } else if (stData.status === 'translating' || stData.status === 'processing' || stData.status === 'pending') {
                const currentPct = stData.progress || 0;
                translationUI.show(locale, 'Traduzindo em segundo plano...', `Worker TranslateGemma (${currentPct}% concluído)`, currentPct);
              } else if (stData.status === 'failed') {
                stopPolling();
                translationUI.show(locale, 'Falha na tradução', `Verifique se o modelo TranslateGemma está no Ollama.`, 0, false, true);
              }
            }
          } catch (pollErr) {
            stopPolling();
          }
        }, 2000);

        // Safety timeout for polling
        setTimeout(() => { stopPolling(); }, 180000);
      }
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    stopPolling();
    console.warn('TranslateGemma on-demand translation fetch error:', err);
    translationUI.show(locale, 'Ops! Tradução pausada', 'Serviço de tradução indisponível ou Ollama sem modelo.', 0, false, true);
  }
}

// Translation UI Notification & Minimized Chip Manager
const translationUI = {
  toastEl: null,
  chipEl: null,
  isMinimized: false,

  show(locale, title, message, progress = 0, isDone = false, isError = false) {
    if (!this.toastEl) {
      this.toastEl = document.createElement('div');
      this.toastEl.id = 'translationToast';
      this.toastEl.className = 'translation-toast-container';
      document.body.appendChild(this.toastEl);
    }
    if (!this.chipEl) {
      this.chipEl = document.createElement('div');
      this.chipEl.id = 'translationChip';
      this.chipEl.className = 'translation-chip';
      this.chipEl.style.display = 'none';
      this.chipEl.addEventListener('click', () => {
        this.expand();
      });
      document.body.appendChild(this.chipEl);
    }

    const icon = isError ? '⚠️' : (isDone ? '✅' : '🔄');
    const spinClass = (!isDone && !isError) ? 'loading-spin' : '';

    this.toastEl.innerHTML = `
      <div class="translation-toast-header">
        <div class="translation-toast-title">
          <span class="${spinClass}" style="display:inline-block; font-size:16px;">${icon}</span>
          <span>${title}</span>
        </div>
        <div class="translation-toast-actions">
          ${!isDone && !isError ? '<button class="translation-toast-btn" id="transMinimizeBtn" title="Ocultar para chip">_</button>' : ''}
          <button class="translation-toast-btn" id="transCloseBtn" title="Fechar">&times;</button>
        </div>
      </div>
      <div style="color: #cbd5e1; font-size: 12.5px; line-height: 1.4; margin: 2px 0 4px 0;">${message}</div>
      ${!isDone && !isError ? `
        <div class="translation-progress-bar">
          <div class="translation-progress-fill" style="width: ${progress}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11.5px; color:#94a3b8; margin-top: 2px;">
          <span>TranslateGemma AI</span>
          <span style="font-weight:600; color:#38bdf8;">${progress}%</span>
        </div>
      ` : ''}
    `;

    const minBtn = this.toastEl.querySelector('#transMinimizeBtn');
    if (minBtn) {
      minBtn.onclick = () => this.minimize(locale, progress, icon);
    }
    const closeBtn = this.toastEl.querySelector('#transCloseBtn');
    if (closeBtn) {
      closeBtn.onclick = () => {
        if (!isDone && !isError) {
          this.minimize(locale, progress, icon);
        } else {
          this.hide();
        }
      };
    }

    this.chipEl.innerHTML = `
      <span class="${spinClass}" style="display:inline-block; font-size:14px;">${icon}</span>
      <span>${locale} (${progress}%)</span>
    `;

    if (this.isMinimized && !isDone) {
      this.toastEl.style.display = 'none';
      this.chipEl.style.display = 'flex';
    } else {
      this.toastEl.style.display = 'flex';
      this.toastEl.style.opacity = '1';
      this.chipEl.style.display = 'none';
    }

    if (isDone) {
      setTimeout(() => {
        this.hide();
      }, 3500);
    } else if (isError) {
      setTimeout(() => {
        this.hide();
      }, 5000);
    }
  },

  minimize(locale, progress, icon = '🔄') {
    this.isMinimized = true;
    if (this.toastEl) this.toastEl.style.display = 'none';
    if (this.chipEl) {
      this.chipEl.style.display = 'flex';
    }
  },

  expand() {
    this.isMinimized = false;
    if (this.chipEl) this.chipEl.style.display = 'none';
    if (this.toastEl) {
      this.toastEl.style.display = 'flex';
      this.toastEl.style.opacity = '1';
    }
  },

  hide() {
    if (this.toastEl) {
      this.toastEl.style.opacity = '0';
      setTimeout(() => {
        if (this.toastEl) this.toastEl.style.display = 'none';
      }, 300);
    }
    if (this.chipEl) this.chipEl.style.display = 'none';
    this.isMinimized = false;
  }
};

// ============================================================================
// ScrollSpy - Active Navigation Highlighter (PDF.js / Modern Document Viewer Model)
// ============================================================================
function initTocSpy() {
  const cards = Array.from(document.querySelectorAll('.content-card[id]'));
  const navLinks = Array.from(document.querySelectorAll('.sidebar-nav-link[href^="#"]'));
  if (!cards.length || !navLinks.length) return;

  const HEADER_HEIGHT = 70;
  const linkMap = new Map();

  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (!href || !href.startsWith('#')) return;
    const slug = href.substring(1);
    if (slug) linkMap.set(slug, link);
  });

  // Clean up previous listeners
  if (window._tocScrollHandler) {
    window.removeEventListener('scroll', window._tocScrollHandler);
    window.removeEventListener('resize', window._tocScrollHandler);
  }
  if (window._tocClickHandlers) {
    window._tocClickHandlers.forEach(({ link, handler }) => {
      link.removeEventListener('click', handler);
    });
  }
  window._tocClickHandlers = [];

  let isClickScrolling = false;
  let clickScrollTimer = null;

  // Active Link Mutator
  function setActiveLink(activeId) {
    if (!activeId) return;
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      const isActive = href === `#${activeId}`;
      link.classList.toggle('active', isActive);
      if (isActive) {
        link.setAttribute('aria-current', 'location');
      } else {
        link.removeAttribute('aria-current');
      }
    });

    // Auto-scroll sidebar if active item is outside visible sidebar area
    const activeLink = linkMap.get(activeId);
    const sidebar = document.querySelector('.doc-sidebar');
    if (activeLink && sidebar) {
      const sRect = sidebar.getBoundingClientRect();
      const lRect = activeLink.getBoundingClientRect();
      if (lRect.top < sRect.top + 30 || lRect.bottom > sRect.bottom - 30) {
        activeLink.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
  }

  // Navigation Clicks with smooth scroll and temporary scrollspy lock
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (!href || !href.startsWith('#')) return;
    const slug = href.substring(1);
    const target = document.getElementById(slug);
    if (!target) return;

    const clickHandler = (event) => {
      event.preventDefault();
      isClickScrolling = true;
      if (clickScrollTimer) clearTimeout(clickScrollTimer);

      setActiveLink(slug);

      const targetTop = target.getBoundingClientRect().top + (window.scrollY || window.pageYOffset || document.documentElement.scrollTop) - HEADER_HEIGHT - 10;
      window.scrollTo({
        top: Math.max(0, targetTop),
        behavior: 'smooth'
      });

      // Release scroll lock after smooth scroll finishes
      clickScrollTimer = setTimeout(() => {
        isClickScrolling = false;
      }, 700);
    };

    link.addEventListener('click', clickHandler);
    window._tocClickHandlers.push({ link, handler: clickHandler });
  });

  // Calculate active section based on reading position
  function getActiveSectionId() {
    const scrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;

    // 1. Top of document
    if (scrollY <= 40 && cards.length > 0) {
      return cards[0].id;
    }

    // 2. Bottom of document (tolerant 50px boundary)
    if ((scrollY + windowHeight) >= (scrollHeight - 50) && cards.length > 0) {
      return cards[cards.length - 1].id;
    }

    // 3. Reading focus line (25% from top of visible content area)
    const readingLine = HEADER_HEIGHT + (windowHeight - HEADER_HEIGHT) * 0.25;

    let activeCard = cards[0];
    for (const card of cards) {
      if (card.hidden || card.style.display === 'none') continue;
      const rect = card.getBoundingClientRect();
      if (rect.top <= readingLine) {
        activeCard = card;
      } else {
        break;
      }
    }

    return activeCard ? activeCard.id : (cards[0] ? cards[0].id : null);
  }

  function highlightActive() {
    if (isClickScrolling) return; // Do not interrupt during click-initiated smooth scrolling
    const activeId = getActiveSectionId();
    if (activeId && linkMap.has(activeId)) {
      setActiveLink(activeId);
    }
  }

  // RAF throttled scroll handler for 60fps responsiveness
  let ticking = false;
  function handleScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      highlightActive();
      ticking = false;
    });
  }

  window._tocScrollHandler = handleScroll;
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('resize', handleScroll, { passive: true });

  // Initial highlight
  highlightActive();
  window.updateActiveTocSpy = highlightActive;
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
    if (lang && lang.toLowerCase() === 'mermaid') {
      codeBlocks.push(`<pre class="mermaid">${code.trim()}</pre>`);
    } else {
      const escCode = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      codeBlocks.push(`<pre><code class="language-${lang}">${escCode}</code></pre>`);
    }
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
  const codeBlocks = document.querySelectorAll('pre:not(.mermaid)');
  const locale = detectUserLocale();
  const dict = DOCSHELL_I18N[locale] || DOCSHELL_I18N['pt-BR'];

  codeBlocks.forEach(pre => {
    if (pre.classList.contains('mermaid') || pre.querySelector('.copy-code-btn')) return;

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

  const clearBtn = document.getElementById('aiClearBtn');

  // Load chat history from localStorage
  function loadChatHistory() {
    try {
      const saved = localStorage.getItem('docshell_chat_history');
      if (saved) {
        const history = JSON.parse(saved);
        if (Array.isArray(history) && history.length > 0) {
          messages.innerHTML = '';
          history.forEach(item => {
            appendMessage(item.content, item.sender, null, item.isHtml, false);
          });
          messages.scrollTop = messages.scrollHeight;
          return;
        }
      }
    } catch (e) {}
  }

  function saveChatHistory() {
    try {
      const msgEls = messages.querySelectorAll('.chat-msg');
      const history = [];
      msgEls.forEach(el => {
        const isUser = el.classList.contains('user');
        history.push({
          sender: isUser ? 'user' : 'assistant',
          content: el.innerHTML,
          isHtml: true
        });
      });
      // Keep last 30 messages
      const trimmed = history.slice(-30);
      localStorage.setItem('docshell_chat_history', JSON.stringify(trimmed));
    } catch (e) {}
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      localStorage.removeItem('docshell_chat_history');
      messages.innerHTML = '';
      const currentLocale = detectUserLocale();
      const dict = DOCSHELL_I18N[currentLocale] || DOCSHELL_I18N['pt-BR'];
      appendMessage(dict.ai_greeting || 'Olá! Sou o Assistente IA do DocShell. Como posso ajudar com a documentação?', 'assistant', null, false, false);
    });
  }

  loadChatHistory();

  async function handleSend() {
    const prompt = input.value.trim();
    if (!prompt) return;

    appendMessage(prompt, 'user', null, false);
    input.value = '';

    const assistantMsgId = 'assistant-msg-' + Date.now();
    const assistantMsgEl = appendMessage('🔍 Consultando base de conhecimento...', 'assistant', assistantMsgId, false);

    const userLocale = detectUserLocale();
    let accumulatedText = '';
    let sources = [];
    let isStreamActive = false;

    // Helper to format sources badges
    function buildSourcesHtml(srcList) {
      if (!srcList || !Array.isArray(srcList) || srcList.length === 0) return '';
      const dict = DOCSHELL_I18N[userLocale] || DOCSHELL_I18N['pt-BR'];
      const badges = srcList.map(s => {
        if (typeof s === 'object' && s.slug) {
          return `<a href="#${s.slug}" class="chat-source-badge" onclick="event.preventDefault(); navigateToSection('${s.slug}');">📄 ${s.title}</a>`;
        } else {
          const title = typeof s === 'string' ? s : (s.title || 'Documentação');
          return `<span class="chat-source-badge">📄 ${title}</span>`;
        }
      }).join('');
      return `<div class="chat-sources"><span>${dict.sources_label || 'Fontes:'}</span> ${badges}</div>`;
    }

    // Attempt 1: Realtime WebSocket Streaming (token-by-token typewriter effect)
    if (window.WebSocket && window.location.protocol.startsWith('http')) {
      try {
        const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProto}//${window.location.host}/ws/chat`;
        const ws = new WebSocket(wsUrl);

        await new Promise((resolve, reject) => {
          const wsTimeout = setTimeout(() => { ws.close(); reject(new Error('WS Timeout')); }, 4000);

          ws.onopen = () => {
            clearTimeout(wsTimeout);
            isStreamActive = true;
            ws.send(JSON.stringify({ message: prompt, locale: userLocale }));
          };

          ws.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              if (data.type === 'sources') {
                sources = data.sources || [];
              } else if (data.type === 'token') {
                accumulatedText += data.token;
                assistantMsgEl.innerHTML = formatMarkdown(accumulatedText) + buildSourcesHtml(sources);
                messages.scrollTop = messages.scrollHeight;
              } else if (data.type === 'done') {
                assistantMsgEl.innerHTML = formatMarkdown(accumulatedText) + buildSourcesHtml(sources);
                saveChatHistory();
                ws.close();
                resolve();
              }
            } catch (e) {}
          };

          ws.onerror = (err) => {
            clearTimeout(wsTimeout);
            reject(err);
          };

          ws.onclose = () => {
            if (isStreamActive) {
              saveChatHistory();
              resolve();
            }
          };
        });

        if (accumulatedText.trim().length > 0) {
          saveChatHistory();
          return;
        }
      } catch (wsErr) {
        console.warn('WebSocket stream fallback to REST API:', wsErr);
      }
    }

    // Attempt 2: REST /api/chat Fallback
    try {
      let data = null;
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: prompt, locale: userLocale })
        });
        if (res.ok) {
          data = await res.json();
        }
      } catch (netErr) {}

      if (!data) {
        data = await performClientSearch(prompt);
      }

      const rawAnswer = (data && (data.answer || data.response)) ? (data.answer || data.response) : 'Não encontrei informações específicas para esta consulta na documentação.';
      const sourcesList = data && data.sources ? data.sources : [];
      assistantMsgEl.innerHTML = formatMarkdown(rawAnswer) + buildSourcesHtml(sourcesList);
      messages.scrollTop = messages.scrollHeight;
      saveChatHistory();
    } catch (err) {
      assistantMsgEl.innerHTML = formatMarkdown('<em>Serviço de busca concluído. Para respostas IA completas, inicie o Ollama com o modelo `llama3.2`.</em>');
      saveChatHistory();
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

  function appendMessage(content, sender, id = null, isHtml = false, shouldSave = true) {
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
    if (shouldSave && sender === 'user') {
      saveChatHistory();
    }
    return msg;
  }
}
