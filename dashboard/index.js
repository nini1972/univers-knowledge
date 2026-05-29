/* ==========================================================================
   🌌 UNIVERS KNOWLEDGE BASE - INTERACTIVE ENGINE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Application State
    let concepts = [];
    let activeConceptId = null;
    let currentFilters = {
        search: '',
        level: 'level-all',
        status: 'status-all'
    };

    // Cache DOM Elements
    const elements = {
        conceptList: document.getElementById('concept-list'),
        searchInput: document.getElementById('search-input'),
        clearSearch: document.getElementById('clear-search'),
        levelFilters: document.getElementById('level-filters'),
        statusFilters: document.getElementById('status-filters'),
        resultsCount: document.getElementById('results-count'),
        welcomeView: document.getElementById('welcome-view'),
        contentView: document.getElementById('content-view'),
        networkView: document.getElementById('network-view'),
        
        // Stats
        totalStat: document.getElementById('stat-total'),
        verifiedStat: document.getElementById('stat-verified'),
        theoreticalStat: document.getElementById('stat-theoretical'),
        
        // Buttons
        btnExploreFirst: document.getElementById('btn-explore-first'),
        btnShowNetwork: document.getElementById('btn-show-network'),
        btnCloseNetwork: document.getElementById('btn-close-network'),
        btnBackToWelcome: document.getElementById('btn-back-to-welcome'),
        
        // Viewer elements
        viewTitle: document.getElementById('view-title'),
        viewLevel: document.getElementById('view-level'),
        viewStatus: document.getElementById('view-status'),
        viewOverview: document.getElementById('view-overview-content'),
        viewExplanation: document.getElementById('view-explanation-content'),
        viewMath: document.getElementById('view-math-content'),
        viewSkeptic: document.getElementById('view-skeptic-content'),
        viewVerification: document.getElementById('view-verification-content'),
        viewVisual: document.getElementById('view-visual-content'),
        viewRelated: document.getElementById('view-related-content'),
        viewSources: document.getElementById('view-sources-list'),
        networkCanvas: document.getElementById('network-graph-canvas'),
        tabLinks: document.querySelectorAll('.tab-link'),
        scrollContainer: document.querySelector('.scroll-container')
    };

    /* ==========================================================================
       📥 DATA INGESTION & ROBUST LOADING
       ========================================================================== */

    async function loadDatabase() {
        try {
            // Fetch database relative to the /dashboard folder
            const response = await fetch('../knowledge_base/database.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            concepts = await response.json();
            initializeDashboard();
        } catch (error) {
            console.warn('CORS / Fetch issue detected. Loading fallback UI state.', error);
            renderErrorOverlay(error);
        }
    }

    // High-fidelity fallback error card for running via local file:// protocol
    function renderErrorOverlay(error) {
        elements.conceptList.innerHTML = `
            <div style="padding: 20px; color: var(--text-muted); font-size: 13px; text-align: center;">
                <i class="fa-solid fa-triangle-exclamation" style="font-size: 24px; color: var(--status-theoretical); margin-bottom: 10px;"></i>
                <p>Unable to load local JSON via direct <code>file://</code> double-click due to browser security guidelines.</p>
                <p style="margin-top:10px;">Please launch a lightweight local server to run this beautiful interface:</p>
                <pre style="background: hsla(225, 20%, 2%, 0.8); border: 1px solid var(--border-glass); padding:8px; border-radius:4px; font-family:var(--font-mono); font-size:11px; margin-top:10px; color:var(--text-primary); text-align:left; overflow-x:auto;">python -m http.server 8000</pre>
            </div>
        `;
        
        elements.welcomeView.innerHTML = `
            <div class="welcome-content" style="max-width: 600px;">
                <i class="fa-solid fa-circle-nodes welcome-icon" style="color: var(--status-theoretical);"></i>
                <h2>Local Security Constraint Detected</h2>
                <p>Browsers restrict loading files via direct <code>file://</code> protocol to protect security. Launch a single-line development server in your workspace directory to view the database:</p>
                
                <div class="info-alert" style="background-color: hsla(38, 95%, 52%, 0.08); border-color: hsla(38, 95%, 52%, 0.25); text-align: left; width: 100%;">
                    <i class="fa-solid fa-code" style="color: var(--status-theoretical);"></i>
                    <div>
                        <strong>To run local server:</strong>
                        <ol style="margin-top: 8px; margin-left: 16px;">
                            <li>Open PowerShell or terminal inside <code>C:\\Users\\ninic\\univers-knowledge</code></li>
                            <li>Run: <code style="background: hsla(225,15%,100%,0.08); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); color:#fff;">python -m http.server 8000</code></li>
                            <li>Open your browser to: <a href="http://localhost:8000/dashboard/" target="_blank" style="color: var(--neon-blue); font-weight: 700; text-decoration: underline;">http://localhost:8000/dashboard/</a></li>
                        </ol>
                    </div>
                </div>
            </div>
        `;
    }

    /* ==========================================================================
       🏁 INITIALIZATION & STATE SETUP
       ========================================================================== */

    function initializeDashboard() {
        calculateGlobalStats();
        applyFiltersAndRender();
        setupEventListeners();
    }

    function calculateGlobalStats() {
        elements.totalStat.textContent = concepts.length;
        
        const verifiedCount = concepts.filter(c => c.status === 'VERIFIED').length;
        const theoreticalCount = concepts.filter(c => c.status === 'THEORETICAL').length;
        
        elements.verifiedStat.textContent = verifiedCount;
        elements.theoreticalStat.textContent = theoreticalCount;
    }

    /* ==========================================================================
       🔍 FILTERING & SEARCH MECHANICS
       ========================================================================== */

    function applyFiltersAndRender() {
        const filtered = concepts.filter(c => {
            // Search text filter
            const matchesSearch = currentFilters.search === '' || 
                c.title.toLowerCase().includes(currentFilters.search) ||
                c.overview.toLowerCase().includes(currentFilters.search) ||
                c.content.toLowerCase().includes(currentFilters.search);
            
            // Level filter
            let matchesLevel = true;
            if (currentFilters.level !== 'level-all') {
                const targetLvl = parseInt(currentFilters.level.replace('level-', ''));
                matchesLevel = c.level === targetLvl;
            }
            
            // Status filter
            let matchesStatus = true;
            if (currentFilters.status !== 'status-all') {
                const targetStatus = currentFilters.status.replace('status-', '').toUpperCase();
                matchesStatus = c.status === targetStatus;
            }

            return matchesSearch && matchesLevel && matchesStatus;
        });

        // Sort alphabetically
        filtered.sort((a, b) => a.title.localeCompare(b.title));

        renderConceptCards(filtered);
        elements.resultsCount.textContent = `${filtered.length} found`;
    }

    function renderConceptCards(filteredConcepts) {
        if (filteredConcepts.length === 0) {
            elements.conceptList.innerHTML = `
                <div class="no-results" style="padding: 32px; text-align: center; color: var(--text-muted);">
                    <i class="fa-regular fa-folder-open" style="font-size: 28px; margin-bottom: 8px;"></i>
                    <p style="font-size: 13px;">No matching concepts found.</p>
                </div>
            `;
            return;
        }

        elements.conceptList.innerHTML = filteredConcepts.map(c => {
            const statusClass = c.status === 'VERIFIED' ? 'status-verified' : 'status-theoretical';
            const statusDot = c.status === 'VERIFIED' ? 'dot-verified' : 'dot-theoretical';
            const cardBorderClass = c.status === 'VERIFIED' ? 'card-verified' : 'card-theoretical';
            const activeClass = c.id === activeConceptId ? 'active' : '';
            const linksCount = c.related.length;

            return `
                <div class="concept-card ${cardBorderClass} ${activeClass}" data-id="${c.id}">
                    <div class="card-top">
                        <span class="card-level">LEVEL ${c.level}</span>
                        <span class="card-status ${statusClass}">
                            <span class="pulse-dot ${statusDot}"></span> ${c.status}
                        </span>
                    </div>
                    <h3 class="card-title">${c.title}</h3>
                    <p class="card-excerpt">${cleanMarkdownExcerpts(c.overview)}</p>
                    <div class="card-footer">
                        <span style="color: var(--text-muted);"><i class="fa-solid fa-link"></i> ${linksCount} relations</span>
                        <span class="card-links" style="color: var(--neon-cyan);"><i class="fa-solid fa-angle-right"></i></span>
                    </div>
                </div>
            `;
        }).join('');

        // Attach click handlers
        document.querySelectorAll('.concept-card').forEach(card => {
            card.addEventListener('click', () => {
                const conceptId = card.getAttribute('data-id');
                selectConcept(conceptId);
            });
        });
    }

    function cleanMarkdownExcerpts(text) {
        return text
            .replace(/[#*`~]/g, '') // remove markdown tags
            .replace(/!\[[^\]]*\]\([^)]+\)/g, '') // remove images
            .replace(/\[[^\]]+\]\([^)]+\)/g, '$1') // simplify links
            .trim();
    }

    /* ==========================================================================
       📖 DYNAMIC MARKDOWN PARSER (Front-end Only)
       ========================================================================== */

    // Simple robust MD to HTML compiler for content rendering
    function parseMarkdown(mdText) {
        let text = mdText || '';
        
        // Remove yaml frontmatter block if passed
        text = text.replace(/^---\s*\n[\s\S]*?\n---\s*/, '');
        
        // Remove top-level # heading since header has its own title block
        text = text.replace(/^#\s+.+$/m, '');

        // Escape HTML
        text = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Inline formatting: Bold, Italic, Code
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Latex block equations $$ ... $$
        text = text.replace(/\$\$(.+?)\$\$/gs, '<div class="math-container">$1</div>');
        // Inline latex $ ... $
        text = text.replace(/\$([^\$]+)\$/g, '<code class="math-inline">$1</code>');

        // Unordered lists
        text = text.replace(/^\s*-\s+(.+)$/gm, '<li>$1</li>');
        // Wrap grouped list items
        text = text.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        // Fix nested double-wrapped lists
        text = text.replace(/<\/ul>\s*<ul>/g, '');

        // Blockquotes
        text = text.replace(/^\s*>\s+(.+)$/gm, '<blockquote>$1</blockquote>');
        
        // Section lines / HRs
        text = text.replace(/^---$/gm, '<hr>');

        // Paragraphs: Wrap double newlines that are not list items or titles
        const lines = text.split(/\n{2,}/);
        const parsedLines = lines.map(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith('<h') || trimmed.startsWith('<ul>') || trimmed.startsWith('<div') || trimmed.startsWith('<blockquote>')) {
                return trimmed;
            }
            return `<p>${trimmed.replace(/\n/g, '<br>')}</p>`;
        });

        return parsedLines.join('\n');
    }

    // Extracts and slices concept contents by standard templates
    function extractSection(contentText, headingPattern) {
        const text = contentText || '';
        const regex = new RegExp(`##\\s+${headingPattern}\\s*\\n([\\s\\S]*?)(?=\\n##|\\s*$)`, 'i');
        const match = text.match(regex);
        return match ? match[1].trim() : '';
    }

    /* ==========================================================================
       📬 ROUTING & CONTENT VIEWPORT UPDATES
       ========================================================================== */

    function selectConcept(id) {
        activeConceptId = id;
        
        // Highlight active card
        document.querySelectorAll('.concept-card').forEach(c => {
            if (c.getAttribute('data-id') === id) {
                c.classList.add('active');
            } else {
                c.classList.remove('active');
            }
        });

        const concept = concepts.find(c => c.id === id);
        if (!concept) return;

        // Viewport swap
        elements.welcomeView.style.display = 'none';
        elements.networkView.style.display = 'none';
        elements.contentView.style.display = 'flex';
        
        // Header Metas
        elements.viewTitle.textContent = concept.title;
        elements.viewLevel.textContent = `LEVEL ${concept.level}`;
        
        // Status badges adjustment
        elements.viewStatus.textContent = concept.status;
        elements.viewStatus.className = 'badge status-badge ' + (concept.status === 'VERIFIED' ? 'verified' : 'theoretical');

        // Extract and Render individual standard headings
        const rawContent = concept.content;
        
        const overviewRaw = extractSection(rawContent, '1\\.\\s+Overview');
        const explanationRaw = extractSection(rawContent, '2\\.\\s+Detailed Explanation');
        const mathRaw = extractSection(rawContent, '3\\.\\s+Mathematical Framework');
        const skepticRaw = extractSection(rawContent, '4\\.\\s+Skeptical Perspectives & Alternative Hypotheses');
        const verificationRaw = extractSection(rawContent, '5\\.\\s+Verification & Skeptic\'s Notes');
        const visualRaw = extractSection(rawContent, '6\\.\\s+Visual Representation');
        const relatedRaw = extractSection(rawContent, '7\\.\\s+Related Concepts');

        // Inject parsed html
        elements.viewOverview.innerHTML = parseMarkdown(overviewRaw || concept.overview || '*No overview available.*');
        elements.viewExplanation.innerHTML = parseMarkdown(explanationRaw || '*No explanation available.*');
        elements.viewMath.innerHTML = parseMarkdown(mathRaw || '*No mathematical framework compiled.*');
        elements.viewSkeptic.innerHTML = parseMarkdown(skepticRaw || '*No critical counter-hypotheses registered.*');
        elements.viewVerification.innerHTML = parseMarkdown(verificationRaw || '*Verification guidelines pending.*');

        // Section 6: Image Display Logic
        if (concept.image_path) {
            elements.viewVisual.innerHTML = `
                <div class="visual-img-container" style="text-align: center; width: 100%;">
                    <img src="../${concept.image_path}" alt="${concept.title} scientific simulation image" onerror="this.onerror=null; this.parentNode.innerHTML='<div class=\\'no-visual-placeholder\\\'><i class=\\'fa-regular fa-image\\\'></i><h4>Visual asset not compiled yet</h4><p>The image is queued for automatic generation.</p></div>';">
                    <p style="font-size: 11px; color: var(--text-muted); margin-top: 8px;"><i class="fa-solid fa-camera"></i> Generated by Universe Visualizer Agent</p>
                </div>
            `;
        } else {
            elements.viewVisual.innerHTML = `
                <div class="no-visual-placeholder">
                    <i class="fa-regular fa-image"></i>
                    <h4>Visual asset not generated</h4>
                    <p>This theoretical study has not triggered the deep-space visual pipeline yet.</p>
                </div>
            `;
        }

        // Section 7: Related & Prerequisites Hyperlinking
        if (concept.related && concept.related.length > 0) {
            const linksHtml = concept.related.map(relId => {
                const target = concepts.find(item => item.id === relId);
                const titleStr = target ? target.title : relId.replace(/_/g, ' ').toUpperCase();
                const icon = target && target.status === 'VERIFIED' ? 'fa-circle-check text-verified' : 'fa-circle-dot text-theoretical';
                return `
                    <div class="related-link-card" data-target-id="${relId}">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <i class="fa-solid ${icon}"></i>
                            <span class="related-link-title">${titleStr}</span>
                        </div>
                        <i class="fa-solid fa-arrow-right-long"></i>
                    </div>
                `;
            }).join('');
            
            elements.viewRelated.innerHTML = `<div class="related-grid">${linksHtml}</div>`;
            
            // Attach related link triggers
            elements.viewRelated.querySelectorAll('.related-link-card').forEach(card => {
                card.addEventListener('click', () => {
                    const targetId = card.getAttribute('data-target-id');
                    selectConcept(targetId);
                });
            });
        } else {
            elements.viewRelated.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;"><i class="fa-solid fa-link-slash"></i> No close physical connections registered.</p>';
        }

        // Bibliography sources rendering
        if (concept.sources && concept.sources.length > 0) {
            elements.viewSources.innerHTML = concept.sources.map(src => `
                <li><i class="fa-solid fa-circle-nodes"></i> ${src}</li>
            `).join('');
        } else {
            elements.viewSources.innerHTML = '<li><i class="fa-solid fa-circle-question"></i> Mainstream databases & arXiv references inside texts.</li>';
        }

        // Reset scroll position to top
        elements.scrollContainer.scrollTop = 0;
        
        // Highlight active nav tab based on viewport scroll later
        updateActiveTabLink('.tab-link[href="#sec-overview"]');
    }

    function updateActiveTabLink(selector) {
        elements.tabLinks.forEach(link => link.classList.remove('active'));
        const activeLink = document.querySelector(selector);
        if (activeLink) activeLink.classList.add('active');
    }

    /* ==========================================================================
       🕸️ INTERACTIVE PREREQUISITE NETWORK COMPILER
       ========================================================================== */

    function renderNetworkGraph() {
        elements.welcomeView.style.display = 'none';
        elements.contentView.style.display = 'none';
        elements.networkView.style.display = 'flex';

        // Layout rows based on concepts levels (simulating standard network node layers)
        const lv1 = concepts.filter(c => c.level === 1).sort((a,b) => a.title.localeCompare(b.title));
        const lv2 = concepts.filter(c => c.level === 2).sort((a,b) => a.title.localeCompare(b.title));
        const lv3 = concepts.filter(c => c.level === 3).sort((a,b) => a.title.localeCompare(b.title));

        const renderNodesRow = (nodes, levelNum, label) => {
            if (nodes.length === 0) return '';
            const cardsHtml = nodes.map(n => {
                const nodeClass = n.status === 'VERIFIED' ? 'node-verified' : 'node-theoretical';
                const icon = n.status === 'VERIFIED' ? 'fa-solid fa-circle-check text-verified' : 'fa-regular fa-circle-dot text-theoretical';
                return `
                    <button class="network-node-btn ${nodeClass}" data-node-id="${n.id}">
                        <i class="${icon}"></i>
                        <span>${n.title}</span>
                    </button>
                `;
            }).join('');

            return `
                <div class="network-level-row">
                    <div class="network-level-label">${label.toUpperCase()}</div>
                    <div class="network-cards-container">${cardsHtml}</div>
                </div>
            `;
        };

        let graphHtml = '<div class="network-nodes-layout">';
        
        // Level 1 Nodes
        graphHtml += renderNodesRow(lv1, 1, 'Level 1: Fundamental Physical Foundations');
        
        // Arrow separator if both layers exist
        if (lv1.length > 0 && lv2.length > 0) {
            graphHtml += '<div class="network-flow-arrow"><i class="fa-solid fa-angles-down"></i> Dynamic Expansion Flow <i class="fa-solid fa-angles-down"></i></div>';
        }
        
        // Level 2 Nodes
        graphHtml += renderNodesRow(lv2, 2, 'Level 2: Advanced Theoretical Frameworks');
        
        // Arrow separator
        if (lv2.length > 0 && lv3.length > 0) {
            graphHtml += '<div class="network-flow-arrow"><i class="fa-solid fa-angles-down"></i> Global Universe Projections <i class="fa-solid fa-angles-down"></i></div>';
        }

        // Level 3 Nodes
        graphHtml += renderNodesRow(lv3, 3, 'Level 3: Cosmology & Astrophysics');

        graphHtml += '</div>';
        elements.networkCanvas.innerHTML = graphHtml;

        // Add node click listeners
        elements.networkCanvas.querySelectorAll('.network-node-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const nodeId = btn.getAttribute('data-node-id');
                selectConcept(nodeId);
            });
        });
    }

    /* ==========================================================================
       👂 ACTION LISTENERS & EVENTS
       ========================================================================== */

    function setupEventListeners() {
        // Search Input triggers
        elements.searchInput.addEventListener('input', (e) => {
            currentFilters.search = e.target.value.toLowerCase().trim();
            if (currentFilters.search) {
                elements.clearSearch.style.display = 'block';
            } else {
                elements.clearSearch.style.display = 'none';
            }
            applyFiltersAndRender();
        });

        // Clear Search Btn
        elements.clearSearch.addEventListener('click', () => {
            elements.searchInput.value = '';
            currentFilters.search = '';
            elements.clearSearch.style.display = 'none';
            applyFiltersAndRender();
        });

        // Filter Level buttons
        elements.levelFilters.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                elements.levelFilters.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilters.level = btn.getAttribute('data-filter');
                applyFiltersAndRender();
            });
        });

        // Filter Status buttons
        elements.statusFilters.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                elements.statusFilters.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilters.status = btn.getAttribute('data-filter');
                applyFiltersAndRender();
            });
        });

        // Concept detail page Tabs navigation handling
        elements.tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                elements.tabLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                const targetId = link.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Track scroll position of elements panel to auto-highlight corresponding tab link
        elements.scrollContainer.addEventListener('scroll', () => {
            const sections = document.querySelectorAll('.concept-section');
            let activeSecId = 'sec-overview';
            
            sections.forEach(sec => {
                const rect = sec.getBoundingClientRect();
                // If section is partially visible near top threshold
                if (rect.top <= 140) {
                    activeSecId = sec.getAttribute('id');
                }
            });

            elements.tabLinks.forEach(link => {
                if (link.getAttribute('href') === `#${activeSecId}`) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        });

        // Navigation CTA hooks
        elements.btnExploreFirst.addEventListener('click', () => {
            if (concepts.length > 0) {
                // select first sorted concept
                const sorted = [...concepts].sort((a, b) => a.title.localeCompare(b.title));
                selectConcept(sorted[0].id);
            }
        });

        elements.btnShowNetwork.addEventListener('click', renderNetworkGraph);
        elements.btnCloseNetwork.addEventListener('click', () => {
            elements.networkView.style.display = 'none';
            if (activeConceptId) {
                elements.contentView.style.display = 'flex';
            } else {
                elements.welcomeView.style.display = 'flex';
            }
        });

        elements.btnBackToWelcome.addEventListener('click', () => {
            activeConceptId = null;
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'none';
            elements.welcomeView.style.display = 'flex';
            
            // clear sidebar active state
            document.querySelectorAll('.concept-card').forEach(c => c.classList.remove('active'));
        });
    }

    // Launch Ingest Engine
    loadDatabase();
});
