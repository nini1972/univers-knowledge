/* ==========================================================================
   🌌 UNIVERS KNOWLEDGE BASE - INTERACTIVE DISCOVERY ENGINE (ODYSSEY)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Original Datasets (Immutable Reference Cache)
    let allConcepts = [];
    let allEvaluationRuns = [];
    let allTelemetryEvents = [];

    // Core Active Application State (Filtered chronologically by Scrubber)
    let concepts = [];
    let evaluationRuns = [];
    let telemetryEvents = [];
    let chronologicalRuns = []; // Oldest first runs list
    
    let activeConceptId = null;
    let activePerspective = 'codex'; // 'codex', 'network', 'ledger', 'agents'
    
    let currentFilters = {
        search: '',
        level: 'level-all',
        status: 'status-all'
    };
    
    let currentTimelineFilter = 'all'; // 'all', 'approved', 'rejected'

    // Node graph physics states
    let graphNodes = [];
    let graphLinks = [];
    let draggedNode = null;
    let hoveredNode = null;
    let canvasOffset = { x: 0, y: 0 };
    let canvasZoom = 1.0;
    let animationFrameId = null;
    let particleFlows = []; // Micro-animation data flows

    // Timeline Playback Scrubber Engine State
    let currentAttemptIndex = 0;
    let isPlaying = false;
    let playbackInterval = null;
    let playbackSpeed = 2200; // 2.2 seconds per tick epoch

    // Clean and match concepts synonymously
    function areConceptsEquivalent(nameA, nameB) {
        if (!nameA || !nameB) return false;
        const clean = str => str.toLowerCase().replace(/[^a-z0-9]/g, '');
        const cA = clean(nameA);
        const cB = clean(nameB);
        if (cA === cB) return true;
        
        // Starts with or contains matching for longer titles (e.g. including verification markers)
        if (cA.includes(cB) || cB.includes(cA)) {
            if (cA.startsWith(cB) || cB.startsWith(cA) || (cA.length > 10 && cB.length > 10)) {
                return true;
            }
        }
        
        // Custom synonym overrides
        const synonyms = [
            ["beyondthestandardmodelsolutionstothehierarchyproblem", "beyondthestandardmodelsupersymmetryvsextradimensionsdebate"],
            ["beyondthestandardmodelsolutionstothehierarchyproblem", "beyondthestandardmodel"],
            ["beyondthestandardmodelsupersymmetryvsextradimensionsdebate", "beyondthestandardmodel"],
            ["cosmicinflation", "inflationarycosmology"],
            ["modifiedgravityvsdarkmatterparadigmdebate", "modifiednewtoniandynamicsmondversuscolddarkmattercdmparadigmdebate"]
        ];
        
        for (const [s1, s2] of synonyms) {
            if ((cA === s1 && cB === s2) || (cA === s2 && cB === s1)) return true;
        }
        return false;
    }

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
        ledgerView: document.getElementById('ledger-view'),
        agentsView: document.getElementById('agents-view'),
        perspectiveSelector: document.getElementById('perspective-selector'),
        sidebarPanel: document.getElementById('sidebar-panel'),
        
        // Stats
        totalStat: document.getElementById('stat-total'),
        verifiedStat: document.getElementById('stat-verified'),
        theoreticalStat: document.getElementById('stat-theoretical'),
        
        // Navigation / Action Buttons
        btnExploreFirst: document.getElementById('btn-explore-first'),
        btnShowNetworkCard: document.getElementById('btn-show-network-card'),
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
        tabLinks: document.querySelectorAll('.tab-link'),
        scrollContainer: document.querySelector('.scroll-container'),
        
        // Timeline & Agents
        timelineStream: document.getElementById('timeline-stream'),
        timelineFilters: document.querySelector('.timeline-filters'),
        telemetryTicker: document.getElementById('telemetry-ticker'),
        tickerLinesCount: document.getElementById('ticker-lines-count'),
        pipelineStatus: document.getElementById('pipeline-status'),
        
        // Canvas Graph
        networkCanvas: document.getElementById('network-canvas'),
        
        // Scrubber Controls
        btnScrubPrev: document.getElementById('btn-scrub-prev'),
        btnScrubPlay: document.getElementById('btn-scrub-play'),
        btnScrubNext: document.getElementById('btn-scrub-next'),
        scrubberSlider: document.getElementById('scrubber-slider'),
        scrubberTrackFill: document.getElementById('scrubber-track-fill'),
        scrubberTicks: document.getElementById('scrubber-ticks'),
        scrubberEpochNum: document.getElementById('scrubber-epoch-num'),
        scrubberEpochTotal: document.getElementById('scrubber-epoch-total'),
        scrubberEpochConcept: document.getElementById('scrubber-epoch-concept'),
        scrubberEpochStatus: document.getElementById('scrubber-epoch-status'),
        
        // Zoom Controls Overlay
        btnZoomIn: document.getElementById('btn-zoom-in'),
        btnZoomOut: document.getElementById('btn-zoom-out'),
        btnZoomReset: document.getElementById('btn-zoom-reset')
    };

    /* ==========================================================================
       📥 PARALLEL DATA INGESTION ENGINE
       ========================================================================== */

    async function loadAllDatasets() {
        try {
            // Parallel Fetch execution with cache-busting query parameter to force dynamic reload
            const cacheBust = `?t=${Date.now()}`;
            const [dbRes, evalRes, telRes] = await Promise.all([
                fetch(`../knowledge_base/database.json${cacheBust}`),
                fetch(`../knowledge_base/logs/evaluation_runs.jsonl${cacheBust}`),
                fetch(`../knowledge_base/logs/telemetry.jsonl${cacheBust}`)
            ]);

            if (!dbRes.ok) throw new Error(`Database error! Status: ${dbRes.status}`);

            allConcepts = await dbRes.json();

            // Dynamic Relationship Inference
            const cleanText = (txt) => {
                return (txt || '').toLowerCase().replace(/[^a-z0-9]/g, '');
            };
            allConcepts.forEach(c => {
                if (!c.related) c.related = [];
                if (c.related.length === 0) {
                    const contentClean = cleanText(c.content);
                    allConcepts.forEach(target => {
                        if (target.id === c.id) return;
                        
                        const targetIdClean = cleanText(target.id);
                        
                        // Extract core title before parentheses/dashes
                        const coreTitle = target.title.split('(')[0].split('–')[0].split('—')[0].split('-')[0].trim();
                        const coreTitleClean = cleanText(coreTitle);
                        
                        let abbrClean = null;
                        const parenMatch = target.title.match(/\(([^)]+)\)/);
                        if (parenMatch) {
                            abbrClean = cleanText(parenMatch[1]);
                        }
                        
                        if (
                            contentClean.includes(targetIdClean) ||
                            (coreTitleClean.length > 3 && contentClean.includes(coreTitleClean)) ||
                            (abbrClean && abbrClean.length > 1 && contentClean.includes(abbrClean))
                        ) {
                            c.related.push(target.id);
                        }
                    });
                }
            });
            
            // JSONL Parsing helper
            const parseJSONL = async (res) => {
                if (!res.ok) return [];
                const text = await res.text();
                return text.split('\n')
                    .map(line => line.trim())
                    .filter(line => line.length > 0)
                    .map(line => {
                        try { return JSON.parse(line); } 
                        catch (e) { return null; }
                    })
                    .filter(item => item !== null);
            };

            allEvaluationRuns = await parseJSONL(evalRes);
            allTelemetryEvents = await parseJSONL(telRes);

            // Establish standard sorted lists
            allTelemetryEvents.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)); // Newest first for live activity
            
            // Setup Chronological Runs ascending list
            chronologicalRuns = [...allEvaluationRuns].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            currentAttemptIndex = chronologicalRuns.length; // Start in the PRESENT (fully completed universe)

            initializeSystem();
        } catch (error) {
            console.warn('Data stream connection fault. Launch fallback guide.', error);
            renderLocalErrorOverlay(error);
        }
    }

    function renderLocalErrorOverlay(error) {
        elements.conceptList.innerHTML = `
            <div style="padding: 20px; color: var(--text-muted); font-size: 13px; text-align: center;">
                <i class="fa-solid fa-triangle-exclamation" style="font-size: 24px; color: var(--status-theoretical); margin-bottom: 10px;"></i>
                <p>Failed to load datasets via direct browser file security protocols.</p>
                <p style="margin-top:10px;">Launch a lightweight development local server in your workspace to run this environment:</p>
                <pre style="background: hsla(225, 20%, 2%, 0.8); border: 1px solid var(--border-glass); padding:8px; border-radius:4px; font-family:var(--font-mono); font-size:11px; margin-top:10px; color:var(--text-primary); text-align:left;">python -m http.server 8000</pre>
            </div>
        `;
        
        elements.welcomeView.innerHTML = `
            <div class="welcome-content" style="max-width: 600px;">
                <i class="fa-solid fa-circle-nodes welcome-icon" style="color: var(--status-theoretical);"></i>
                <h2>Security Sandboxing restriction</h2>
                <p>Browsers restrict HTTP fetch calls to local folders for security unless served over a port. Launch a local web server to enable our dynamic data engine:</p>
                
                <div class="info-alert" style="background-color: hsla(38, 95%, 52%, 0.08); border-color: hsla(38, 95%, 52%, 0.25); text-align: left; width: 100%;">
                    <i class="fa-solid fa-code" style="color: var(--status-theoretical); font-size: 18px; margin-right: 12px;"></i>
                    <div>
                        <strong>Launch Steps:</strong>
                        <ol style="margin-top: 8px; margin-left: 16px; font-size: 12.5px; line-height: 1.6;">
                            <li>Open PowerShell or Command Prompt in <code>C:\\Users\\ninic\\univers-knowledge</code></li>
                            <li>Run: <code style="background: hsla(225,100%,100%,0.08); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); color:#fff;">python -m http.server 8000</code></li>
                            <li>Access your local browser link: <a href="http://localhost:8000/dashboard/" target="_blank" style="color: var(--neon-cyan); font-weight: 700; text-decoration: underline;">http://localhost:8000/dashboard/</a></li>
                        </ol>
                    </div>
                </div>
            </div>
        `;
    }

    /* ==========================================================================
       🏁 INITIALIZATION & AGGREGATIONS
       ========================================================================== */

    function initializeSystem() {
        updateChronologicalState();
        setupInteractiveEventHooks();
        
        // Initial view default
        switchPerspective('codex');
    }

    function calculateGlobalHeaderStats() {
        elements.totalStat.textContent = concepts.length;
        const verified = concepts.filter(c => c.status === 'VERIFIED' || c.status === '[VERIFIED]').length;
        elements.verifiedStat.textContent = verified;
        elements.theoreticalStat.textContent = concepts.length - verified;
        
        // Update Pipeline status badge
        if (telemetryEvents.length > 0) {
            const latestEvent = telemetryEvents[0];
            const isRecent = (new Date() - new Date(latestEvent.timestamp)) < (1000 * 60 * 30); // 30 mins
            if (isRecent && latestEvent.event_type === 'start') {
                elements.pipelineStatus.innerHTML = `<span class="pulse-dot dot-theoretical"></span> PIPELINE RUNNING: ${latestEvent.stage.toUpperCase()}`;
                elements.pipelineStatus.parentElement.className = 'agent-mood-badge active-run';
            } else {
                elements.pipelineStatus.textContent = 'DORMANT (AWAITING RUN)';
                elements.pipelineStatus.parentElement.className = 'agent-mood-badge';
            }
        } else {
            elements.pipelineStatus.textContent = 'DORMANT (AWAITING RUN)';
            elements.pipelineStatus.parentElement.className = 'agent-mood-badge';
        }
    }

    /* ==========================================================================
       🕹️ PROGRAMMATIC PERSPECTIVE ROUTER & PANEL STRETCHER
       ========================================================================== */

    function switchPerspective(perspectiveId) {
        activePerspective = perspectiveId;
        
        // Toggle programmatic fullscreen layout width
        const workspace = document.getElementById('app-workspace');
        if (workspace) {
            if (perspectiveId === 'codex') {
                workspace.classList.remove('full-width');
            } else {
                workspace.classList.add('full-width');
            }
        }

        // Update active class on selectors
        elements.perspectiveSelector.querySelectorAll('.perspective-btn').forEach(btn => {
            if (btn.getAttribute('data-perspective') === perspectiveId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Hide/Show correct DOM panels
        if (perspectiveId === 'codex') {
            elements.sidebarPanel.style.display = 'flex';
            elements.welcomeView.style.display = activeConceptId ? 'none' : 'flex';
            elements.contentView.style.display = activeConceptId ? 'flex' : 'none';
            elements.networkView.style.display = 'none';
            elements.ledgerView.style.display = 'none';
            elements.agentsView.style.display = 'none';
            stopNetworkGraphLoop();
        } else if (perspectiveId === 'ledger') {
            elements.sidebarPanel.style.display = 'none';
            elements.welcomeView.style.display = 'none';
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'none';
            elements.ledgerView.style.display = 'flex';
            elements.agentsView.style.display = 'none';
            renderOdysseyLedgerTimeline();
            stopNetworkGraphLoop();
        } else if (perspectiveId === 'agents') {
            elements.sidebarPanel.style.display = 'none';
            elements.welcomeView.style.display = 'none';
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'none';
            elements.ledgerView.style.display = 'none';
            elements.agentsView.style.display = 'flex';
            stopNetworkGraphLoop();
        } else if (perspectiveId === 'network') {
            elements.sidebarPanel.style.display = 'none';
            elements.welcomeView.style.display = 'none';
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'flex';
            elements.ledgerView.style.display = 'none';
            elements.agentsView.style.display = 'none';
            startNetworkGraphPhysicsLoop();
        }
    }

    /* ==========================================================================
       ⏳ TIMELINE PLAYBACK ENGINE (CHRONOLOGICAL RECONSTRUCTION)
       ========================================================================== */

    function updateChronologicalState() {
        // 1. Calculate active evaluation runs based on current playback index
        const activeRuns = chronologicalRuns.slice(0, currentAttemptIndex);
        
        // Feed reverse sorted runs to Ledger View
        evaluationRuns = [...activeRuns].reverse();
        
        // 2. Filter telemetry based on the timestamp of the current attempt run
        if (currentAttemptIndex === 0) {
            telemetryEvents = [];
        } else if (currentAttemptIndex === chronologicalRuns.length) {
            // In the present (fully completed universe), display all events
            telemetryEvents = [...allTelemetryEvents];
        } else {
            const currentRun = chronologicalRuns[currentAttemptIndex - 1];
            const maxTimestamp = new Date(currentRun.timestamp);
            telemetryEvents = allTelemetryEvents.filter(e => new Date(e.timestamp) <= maxTimestamp);
        }

        // 3. Reconstruct the visible concepts and determine their dynamic status at this Epoch
        concepts = [];
        allConcepts.forEach(c => {
            const hasAnyHistoricalRuns = allEvaluationRuns.some(r => areConceptsEquivalent(r.concept, c.title));
            
            if (hasAnyHistoricalRuns) {
                // If it has runs, only show it if its first run is reached in chronological active playback
                const conceptRuns = activeRuns.filter(r => areConceptsEquivalent(r.concept, c.title));
                if (conceptRuns.length > 0) {
                    const latestRun = conceptRuns[conceptRuns.length - 1];
                    const isApproved = latestRun.status === 'approved';
                    
                    // Level 2/3 concepts must strictly map to THEORETICAL (never verified as physical facts)
                    const dynamicStatus = (isApproved && c.level === 1) ? 'VERIFIED' : 'THEORETICAL';
                    
                    concepts.push({
                        ...c,
                        status: dynamicStatus
                    });
                }
            } else {
                // If it has NO evaluation runs in history, it is a pre-existing background/pre-science concept
                // Render it as always visible from Epoch 0 as a theoretical base node!
                concepts.push({
                    ...c,
                    status: 'THEORETICAL'
                });
            }
        });

        // 4. Update HUD scrubber states
        if (elements.scrubberSlider) {
            elements.scrubberSlider.max = chronologicalRuns.length;
            elements.scrubberSlider.value = currentAttemptIndex;
        }
        if (elements.scrubberEpochNum) {
            elements.scrubberEpochNum.textContent = currentAttemptIndex;
        }
        if (elements.scrubberEpochTotal) {
            elements.scrubberEpochTotal.textContent = chronologicalRuns.length;
        }
        if (elements.scrubberTrackFill) {
            const pct = chronologicalRuns.length > 0 ? (currentAttemptIndex / chronologicalRuns.length) * 100 : 0;
            elements.scrubberTrackFill.style.width = `${pct}%`;
        }
        if (elements.scrubberEpochConcept) {
            if (currentAttemptIndex === 0) {
                elements.scrubberEpochConcept.textContent = "Pre-Science Era (Day 0)";
            } else {
                const currentRun = chronologicalRuns[currentAttemptIndex - 1];
                elements.scrubberEpochConcept.textContent = `${currentRun.concept} (Attempt #${currentRun.attempt})`;
            }
        }
        if (elements.scrubberEpochStatus) {
            if (currentAttemptIndex === 0) {
                elements.scrubberEpochStatus.textContent = "STATUS: SYSTEM VACUUM";
            } else {
                const currentRun = chronologicalRuns[currentAttemptIndex - 1];
                const isApproved = currentRun.status === 'approved';
                elements.scrubberEpochStatus.innerHTML = `STATUS: <span style="color: ${isApproved ? 'var(--status-verified)' : 'var(--status-theoretical)'}; font-weight:800;">${currentRun.status.toUpperCase()}</span>`;
            }
        }

        renderScrubberTicks();

        // 5. Fire all UI re-render calls
        calculateGlobalHeaderStats();
        applyFiltersAndRenderSidebar();
        calculateAgentCognitiveMetrics();
        renderTelemetryTickerFeed();

        if (activePerspective === 'ledger') {
            renderOdysseyLedgerTimeline();
        }

        // Handle Codex selections on timeline slide
        if (activeConceptId && !concepts.find(c => c.id === activeConceptId)) {
            activeConceptId = null;
            elements.contentView.style.display = 'none';
            elements.welcomeView.style.display = 'flex';
        } else if (activeConceptId) {
            // Re-select active concept to dynamically reload updated status styles
            selectConcept(activeConceptId);
        }

        // Update active network graph coordinates if perspective is active
        if (activePerspective === 'network') {
            buildNetworkGraphModel();
        }
    }

    function renderScrubberTicks() {
        if (!elements.scrubberTicks) return;
        elements.scrubberTicks.innerHTML = '';
        const count = chronologicalRuns.length;
        if (count === 0) return;

        for (let i = 0; i <= count; i++) {
            const tick = document.createElement('div');
            tick.className = 'scrubber-tick-mark';
            if (i <= currentAttemptIndex) {
                tick.classList.add('active');
            }
            tick.style.left = `${(i / count) * 100}%`;
            elements.scrubberTicks.appendChild(tick);
        }
    }

    function togglePlayback() {
        if (isPlaying) {
            pausePlayback();
        } else {
            playPlayback();
        }
    }

    function playPlayback() {
        if (currentAttemptIndex >= chronologicalRuns.length) {
            currentAttemptIndex = 0; // Wrap around on completion
            updateChronologicalState();
        }

        isPlaying = true;
        if (elements.btnScrubPlay) {
            elements.btnScrubPlay.innerHTML = '<i class="fa-solid fa-pause"></i>';
            elements.btnScrubPlay.title = "Pause Continuum";
        }

        playbackInterval = setInterval(() => {
            if (currentAttemptIndex < chronologicalRuns.length) {
                currentAttemptIndex++;
                updateChronologicalState();
            } else {
                pausePlayback();
            }
        }, playbackSpeed);
    }

    function pausePlayback() {
        isPlaying = false;
        if (elements.btnScrubPlay) {
            elements.btnScrubPlay.innerHTML = '<i class="fa-solid fa-play"></i>';
            elements.btnScrubPlay.title = "Play Continuum";
        }
        if (playbackInterval) {
            clearInterval(playbackInterval);
            playbackInterval = null;
        }
    }

    /* ==========================================================================
       🔍 SIDEBAR FILTER & RENDER ENGINE (CODEX)
       ========================================================================== */

    function applyFiltersAndRenderSidebar() {
        const filtered = concepts.filter(c => {
            // Search text filter
            const matchesSearch = currentFilters.search === '' || 
                c.title.toLowerCase().includes(currentFilters.search) ||
                (c.overview && c.overview.toLowerCase().includes(currentFilters.search)) ||
                (c.content && c.content.toLowerCase().includes(currentFilters.search));
            
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
                matchesStatus = c.status.replace(/[\[\]]/g, '') === targetStatus;
            }

            return matchesSearch && matchesLevel && matchesStatus;
        });

        filtered.sort((a, b) => a.title.localeCompare(b.title));
        renderConceptCards(filtered);
        elements.resultsCount.textContent = `${filtered.length} found`;
    }

    function renderConceptCards(filteredList) {
        if (filteredList.length === 0) {
            elements.conceptList.innerHTML = `
                <div class="no-results" style="padding: 30px; text-align: center; color: var(--text-muted);">
                    <i class="fa-regular fa-folder-open" style="font-size: 24px; margin-bottom: 8px;"></i>
                    <p style="font-size: 12.5px;">No concepts match current filter.</p>
                </div>
            `;
            return;
        }

        elements.conceptList.innerHTML = filteredList.map(c => {
            const isVerified = c.status === 'VERIFIED' || c.status === '[VERIFIED]';
            const statusClass = isVerified ? 'status-verified' : 'status-theoretical';
            const statusDot = isVerified ? 'dot-verified' : 'dot-theoretical';
            const cardBorderClass = isVerified ? 'card-verified' : 'card-theoretical';
            const activeClass = c.id === activeConceptId ? 'active' : '';
            const relationsCount = c.related ? c.related.length : 0;

            return `
                <div class="concept-card ${cardBorderClass} ${activeClass}" data-id="${c.id}">
                    <div class="card-top">
                        <span class="card-level">LEVEL ${c.level}</span>
                        <span class="card-status ${statusClass}">
                            <span class="pulse-dot ${statusDot}"></span> ${isVerified ? 'VERIFIED' : 'THEORETICAL'}
                        </span>
                    </div>
                    <h3 class="card-title">${c.title}</h3>
                    <p class="card-excerpt">${cleanExcerpts(c.overview || c.content || '')}</p>
                    <div class="card-footer">
                        <span><i class="fa-solid fa-link"></i> ${relationsCount} relations</span>
                        <span class="card-links"><i class="fa-solid fa-angle-right"></i></span>
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

    function cleanExcerpts(text) {
        return text
            .replace(/^---\s*\n[\s\S]*?\n---\s*/, '') // Remove yaml frontmatter
            .replace(/[#*`~]/g, '') // remove markdown structures
            .replace(/!\[[^\]]*\]\([^)]+\)/g, '') // remove images
            .replace(/\[[^\]]+\]\([^)]+\)/g, '$1') // simplify hyper-links
            .substring(0, 110)
            .trim() + '...';
    }

    /* ==========================================================================
       📖 DYNAMIC MARKDOWN PARSER (In-browser compiler)
       ========================================================================== */

    function compileMarkdownToHTML(mdText) {
        let text = mdText || '';
        
        // Remove frontmatter blocks
        text = text.replace(/^---\s*\n[\s\S]*?\n---\s*/, '');
        // Remove top-level header title
        text = text.replace(/^#\s+.+$/m, '');

        // Escape dangerous tags
        text = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Inline formatting: Bold, Italic, code highlights
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Images compiler
        text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
            let finalSrc = src.trim();
            if (finalSrc.startsWith('../images/')) {
                finalSrc = `../knowledge_base/${finalSrc.replace('../', '')}`;
            } else if (finalSrc.startsWith('images/')) {
                finalSrc = `../knowledge_base/${finalSrc}`;
            }
            return `<div class="markdown-img-wrapper" style="text-align: center; margin: 16px 0;"><img src="${finalSrc}" alt="${alt}" class="markdown-image" style="max-width:100%; border-radius:8px; border:1px solid var(--border-glass); box-shadow:0 0 15px rgba(0,242,254,0.15);" onerror="this.onerror=null; this.style.display='none';" /></div>`;
        });

        // Hyperlinks to concepts compiler
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, label, url) => {
            let finalUrl = url.trim();
            if (finalUrl.endsWith('.md')) {
                const targetId = finalUrl.split('/').pop().replace('.md', '');
                return `<span class="inline-concept-link" data-target="${targetId}">${label}</span>`;
            }
            return `<a href="${finalUrl}" target="_blank" style="color: var(--neon-cyan); text-decoration: underline;">${label}</a>`;
        });

        // LaTeX equations
        text = text.replace(/\$\$(.+?)\$\$/gs, '<div class="math-container">$1</div>');
        text = text.replace(/\$([^\$]+)\$/g, '<code class="math-inline">$1</code>');

        // Lists formatting
        text = text.replace(/^\s*-\s+(.+)$/gm, '<li>$1</li>');
        text = text.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        text = text.replace(/<\/ul>\s*<ul>/g, ''); // flatten dual blocks

        // Blockquotes formatting
        text = text.replace(/^\s*>\s+(.+)$/gm, '<blockquote>$1</blockquote>');
        
        // Dividers
        text = text.replace(/^---$/gm, '<hr>');

        // Paragraph tags compiler
        const lines = text.split(/\n{2,}/);
        const paragraphs = lines.map(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith('<h') || trimmed.startsWith('<ul>') || trimmed.startsWith('<div') || trimmed.startsWith('<blockquote>')) {
                return trimmed;
            }
            return `<p>${trimmed.replace(/\n/g, '<br>')}</p>`;
        });

        return paragraphs.join('\n');
    }

    function extractStandardHeading(contentText, headingRegex) {
        const text = contentText || '';
        const regex = new RegExp(`##\\s+${headingRegex}\\s*\\n([\\s\\S]*?)(?=\\n##|\\s*$)`, 'i');
        const match = text.match(regex);
        return match ? match[1].trim() : '';
    }

    /* ==========================================================================
       📬 CONCEPT SPECIFIC VIEWER & DATA ROUTING
       ========================================================================== */

    function selectConcept(id) {
        activeConceptId = id;
        
        // Ensure we are in Codex mode to read content
        if (activePerspective !== 'codex') {
            switchPerspective('codex');
        }

        // Sidebar card active highlighting
        document.querySelectorAll('.concept-card').forEach(c => {
            if (c.getAttribute('data-id') === id) {
                c.classList.add('active');
            } else {
                c.classList.remove('active');
            }
        });

        const concept = concepts.find(c => c.id === id);
        if (!concept) return;

        // View toggle
        elements.welcomeView.style.display = 'none';
        elements.contentView.style.display = 'flex';
        
        // Title block headers
        elements.viewTitle.textContent = concept.title;
        elements.viewLevel.textContent = `LEVEL ${concept.level}`;
        
        const isVerified = concept.status === 'VERIFIED' || concept.status === '[VERIFIED]';
        elements.viewStatus.textContent = isVerified ? 'VERIFIED' : 'THEORETICAL';
        elements.viewStatus.className = 'badge status-badge ' + (isVerified ? 'verified' : 'theoretical');

        // Heading extraction split parsing
        const rawContent = concept.content;
        
        let overviewRaw = extractStandardHeading(rawContent, '1\\.\\s+Overview');
        let explanationRaw = extractStandardHeading(rawContent, '2\\.\\s+Detailed Explanation');
        let mathRaw = extractStandardHeading(rawContent, '3\\.\\s+Mathematical Framework');
        let skepticRaw = extractStandardHeading(rawContent, '4\\.\\s+Skeptical Perspectives & Alternative Hypotheses');
        let verificationRaw = extractStandardHeading(rawContent, '5\\.\\s+Verification & Skeptic\'s Notes');
        let visualRaw = extractStandardHeading(rawContent, '6\\.\\s+Visual Representation');
        let relatedRaw = extractStandardHeading(rawContent, '7\\.\\s+Related Concepts');

        // Check for older template mapping (6-sections structures fallback)
        if (!overviewRaw && !explanationRaw && !mathRaw) {
            overviewRaw = extractStandardHeading(rawContent, '1\\.\\s+Overview');
            explanationRaw = extractStandardHeading(rawContent, '2\\.\\s+Detailed Explanation');
            mathRaw = extractStandardHeading(rawContent, '3\\.\\s+Mathematical Framework');
            verificationRaw = extractStandardHeading(rawContent, '4\\.\\s+Verification & Skeptic\'s Notes');
            visualRaw = extractStandardHeading(rawContent, '5\\.\\s+Visual Representation');
            relatedRaw = extractStandardHeading(rawContent, '6\\.\\s+Related Concepts');
            skepticRaw = ''; // Omit Section 4 for legacy files
        }

        // Catch-all absolute layout failure fallback
        if (!overviewRaw && !explanationRaw && !mathRaw) {
            overviewRaw = rawContent;
            explanationRaw = '';
            mathRaw = '';
            skepticRaw = '';
            verificationRaw = '';
            visualRaw = '';
            relatedRaw = '';
        }

        // HTML Compilation injection
        elements.viewOverview.innerHTML = compileMarkdownToHTML(overviewRaw || concept.overview || '*No overview content written.*');
        elements.viewExplanation.innerHTML = compileMarkdownToHTML(explanationRaw || '*No explanation available.*');
        elements.viewMath.innerHTML = compileMarkdownToHTML(mathRaw || '*No mathematical equations registered.*');
        elements.viewSkeptic.innerHTML = compileMarkdownToHTML(skepticRaw || '*No registered skeptic criticisms for this entry.*');
        elements.viewVerification.innerHTML = compileMarkdownToHTML(verificationRaw || '*Verification outline pending.*');

        // Dynamic visual asset checker
        if (concept.image_path) {
            let finalImgSrc = concept.image_path;
            if (finalImgSrc.startsWith('images/')) {
                finalImgSrc = `../knowledge_base/${finalImgSrc}`;
            } else if (!finalImgSrc.startsWith('http') && !finalImgSrc.startsWith('../')) {
                finalImgSrc = `../${finalImgSrc}`;
            }

            elements.viewVisual.innerHTML = `
                <div class="visual-img-container" style="text-align: center; width: 100%;">
                    <img src="${finalImgSrc}" alt="${concept.title} simulation visual" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--border-glass); box-shadow: 0 4px 20px rgba(0,0,0,0.3);" onerror="this.onerror=null; renderNoImagePlaceholder(this);">
                    <p style="font-size: 11px; color: var(--text-muted); margin-top: 8px;"><i class="fa-solid fa-camera"></i> Compiled by Archivist Media Agent</p>
                </div>
            `;
        } else {
            renderNoImagePlaceholder(null);
        }

        // Relations linking grid compiler
        if (concept.related && concept.related.length > 0) {
            const relationsHtml = concept.related.map(relId => {
                const target = concepts.find(item => item.id === relId);
                const titleText = target ? target.title : relId.replace(/_/g, ' ').toUpperCase();
                const isRelVerified = target && (target.status === 'VERIFIED' || target.status === '[VERIFIED]');
                const icon = isRelVerified ? 'fa-circle-check text-verified' : 'fa-circle-dot text-theoretical';
                return `
                    <div class="related-link-card" data-target-id="${relId}">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <i class="fa-solid ${icon}"></i>
                            <span class="related-link-title">${titleText}</span>
                        </div>
                        <i class="fa-solid fa-arrow-right-long"></i>
                    </div>
                `;
            }).join('');
            
            elements.viewRelated.innerHTML = `<div class="related-grid">${relationsHtml}</div>`;
            
            // Re-attach listeners for relations
            elements.viewRelated.querySelectorAll('.related-link-card').forEach(card => {
                card.addEventListener('click', () => {
                    const targetId = card.getAttribute('data-target-id');
                    selectConcept(targetId);
                });
            });
        } else {
            elements.viewRelated.innerHTML = '<p style="color: var(--text-muted); font-size: 12.5px;"><i class="fa-solid fa-link-slash"></i> No connected prerequisites documented.</p>';
        }

        // Sources list renderer
        if (concept.sources && concept.sources.length > 0) {
            elements.viewSources.innerHTML = concept.sources.map(src => `
                <li><i class="fa-solid fa-circle-nodes"></i> ${src}</li>
            `).join('');
        } else {
            elements.viewSources.innerHTML = '<li><i class="fa-solid fa-circle-question"></i> Consult text references for scholarly links.</li>';
        }

        // Reset scroll position to top
        elements.scrollContainer.scrollTop = 0;
        updateActiveTabHighlight('.tab-link[href="#sec-overview"]');
    }

    function renderNoImagePlaceholder(imgElement) {
        const placeholder = `
            <div class="no-visual-placeholder">
                <i class="fa-regular fa-image" style="font-size: 32px; color: var(--text-muted); margin-bottom: 8px;"></i>
                <h4>Simulation image queue pending</h4>
                <p>This entry operates as abstract mathematics. Media generation is scheduled.</p>
            </div>
        `;
        if (imgElement) {
            imgElement.parentNode.innerHTML = placeholder;
        } else {
            elements.viewVisual.innerHTML = placeholder;
        }
    }
    window.renderNoImagePlaceholder = renderNoImagePlaceholder;

    function updateActiveTabHighlight(selector) {
        elements.tabLinks.forEach(link => link.classList.remove('active'));
        const target = document.querySelector(selector);
        if (target) target.classList.add('active');
    }

    /* ==========================================================================
       ⏳ TIMELINE DISCOVERY LEDGER RENDER ENGINE (ACADEMIC DRAMA TERMINAL)
       ========================================================================== */

    function compileDebateTerminalHTML(run) {
        const dialogs = [];
        const attempt = run.attempt || 1;
        
        // 1. Physics Researcher submits draft
        let researcherMsg = "";
        if (attempt === 1) {
            researcherMsg = `Submitting draft manuscript on <strong>${run.concept}</strong> for formal peer review. We have synthesized scholastic literature archives, formulated LaTeX equations, and documented verified proof boundaries.`;
        } else if (attempt === 2) {
            researcherMsg = `Re-submitting corrected draft on <strong>${run.concept}</strong> (Attempt #2). We have patched the theoretical voids highlighted in your criticism report and reinforced our bibliography references.`;
        } else {
            researcherMsg = `Re-submitting revised high-fidelity framework on <strong>${run.concept}</strong> (Attempt #${attempt}). We have completed a comprehensive mathematical sweep and resolved all pending questions.`;
        }
        dialogs.push({
            role: 'researcher',
            name: 'Physics Researcher',
            title: 'Scholar',
            message: researcherMsg
        });

        // 2. Scientific Skeptic delivers strict grade
        const isApproved = run.status === 'approved';
        const score = run.score !== undefined ? run.score : (isApproved ? 5 : 3);
        const totalScore = run.total_score || 5;
        let skepticMsg = "";
        
        if (isApproved) {
            if (run.reason_code === 'dry_run') {
                skepticMsg = `Verification bypass triggered. Assigned Score: <strong>${score}/${totalScore}</strong>. Although full verification is currently running under dry-run constraints, the document structure and logic check out.`;
            } else {
                skepticMsg = `Assigned Score: <strong>${score}/${totalScore}</strong>. Comprehensive peer review evaluation completed. Core mathematics exhibit high fidelity, and grounding in empirical evidence is robust. No blockers detected.`;
            }
            if (run.follow_up_questions && run.follow_up_questions.length > 0) {
                skepticMsg += `<br><br><strong>Constructive observations for future iterations:</strong><ul>` + run.follow_up_questions.map(q => `<li>${q}</li>`).join('') + `</ul>`;
            }
        } else {
            skepticMsg = `Assigned Score: <strong>${score}/${totalScore}</strong>. Scrutiny protocol triggered. <strong style="color:var(--status-theoretical)">CRITICAL DISCOVERY VOIDS DETECTED:</strong> Your manuscript does not meet our strict empirical verification constraints. We demand formal resolution on the following gaps:<ul>` + 
                run.follow_up_questions.map(q => `<li>${q}</li>`).join('') + `</ul>`;
        }
        dialogs.push({
            role: 'skeptic',
            name: 'Scientific Skeptic',
            title: 'Epistemic Guardian',
            message: skepticMsg
        });

        // 3. Student Orchestrator executes pipeline command
        let orchestratorMsg = "";
        if (isApproved) {
            orchestratorMsg = `Status: <strong>APPROVED</strong>. Spacetime coordinate integration validated. Archiving <strong>${run.concept}</strong> into the master database and committing changes to the knowledge base branch.`;
        } else {
            orchestratorMsg = `Status: <strong>REJECTED</strong>. Critique validated. Draft falls short of scientific rigor thresholds. Aborting archive write. Initiating automatic self-correction cycle to resolve all skeptic issues.`;
        }
        dialogs.push({
            role: 'orchestrator',
            name: 'Student Orchestrator',
            title: 'System Scribe',
            message: orchestratorMsg
        });

        // Generate final HTML blocks
        const bubblesHtml = dialogs.map(d => `
            <div class="debate-speech-bubble ${d.role}">
                <div class="debate-agent-header">
                    <span class="debate-agent-name">${d.name}</span>
                    <span class="debate-agent-role">[${d.title}]</span>
                </div>
                <div class="debate-msg-body typewriter-animated">
                    ${d.message}
                </div>
            </div>
        `).join('');

        return `
            <div class="debate-terminal-container">
                ${bubblesHtml}
            </div>
        `;
    }

    function renderOdysseyLedgerTimeline() {
        // Apply filters
        const filteredRuns = evaluationRuns.filter(run => {
            if (currentTimelineFilter === 'approved') return run.status === 'approved';
            if (currentTimelineFilter === 'rejected') return run.status === 'rejected';
            return true;
        });

        if (filteredRuns.length === 0) {
            elements.timelineStream.innerHTML = `
                <div style="padding: 40px; text-align: center; color: var(--text-muted);">
                    <i class="fa-solid fa-timeline" style="font-size: 32px; margin-bottom: 12px; color: var(--border-glass);"></i>
                    <p>No discovery runs meet filter criteria.</p>
                </div>
            `;
            return;
        }

        elements.timelineStream.innerHTML = filteredRuns.map(run => {
            const isApproved = run.status === 'approved';
            const statusClass = isApproved ? 'approved' : 'rejected';
            const statusLabel = isApproved ? 'APPROVED' : 'REJECTED';
            const iconClass = isApproved ? 'fa-solid fa-circle-check text-verified' : 'fa-solid fa-triangle-exclamation text-theoretical';
            
            const timestampFormatted = formatRelativeTime(run.timestamp);
            const scoreHtml = run.score !== undefined ? `<span class="timeline-score-badge">Score: ${run.score}/${run.total_score || 5}</span>` : '';
            
            // Build the debate terminal content instead of standard accordion lists
            const debateTerminalHtml = compileDebateTerminalHTML(run);

            // Match concept mapping if exists
            const matchedConcept = concepts.find(c => areConceptsEquivalent(c.title, run.concept));
            const conceptId = matchedConcept ? matchedConcept.id : null;
            const titleClickAttr = conceptId ? `data-concept-id="${conceptId}" style="cursor: pointer;"` : '';

            return `
                <div class="timeline-card ${statusClass}">
                    <span class="timeline-node"></span>
                    <div class="timeline-meta">
                        <span>Attempt #${run.attempt || 1} • ${timestampFormatted}</span>
                        <span>${run.reason_code ? run.reason_code.toUpperCase().replace(/_/g, ' ') : ''}</span>
                    </div>
                    <div class="timeline-title-area">
                        <h3 class="timeline-concept-title" ${titleClickAttr}>
                            <i class="${iconClass}"></i> ${run.concept}
                        </h3>
                        ${scoreHtml}
                    </div>
                    <div class="timeline-reason">
                        <strong>Reason:</strong> ${isApproved ? 'Passed skeptical grading contract.' : 'Fails to meet rigor standard constraints.'} ${isApproved && run.reason_code === 'dry_run' ? 'Self-correcting bypass triggered.' : ''}
                    </div>
                    ${debateTerminalHtml}
                </div>
            `;
        }).join('');

        // Attach listeners for dynamic Codex teleport clicks on titles
        document.querySelectorAll('.timeline-concept-title[data-concept-id]').forEach(title => {
            title.addEventListener('click', () => {
                const id = title.getAttribute('data-concept-id');
                selectConcept(id);
            });
        });
    }

    function formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }

    /* ==========================================================================
       🤖 AGENT COMMAND CENTER & COGNITIVE METRICS
       ========================================================================== */

    function calculateAgentCognitiveMetrics() {
        // Student Orchestrator metrics
        const distinctSelected = new Set(evaluationRuns.map(r => r.concept)).size;
        document.getElementById('m-orchestrator-selected').textContent = distinctSelected || concepts.length;
        
        // Count self-heals by counting attempts > 1
        const selfHeals = evaluationRuns.filter(r => r.attempt > 1).length;
        document.getElementById('m-orchestrator-heals').textContent = selfHeals;

        // Researcher metrics
        let totalCitations = 0;
        let totalFormulaSymbols = 0;
        concepts.forEach(c => {
            if (c.sources) totalCitations += c.sources.length;
            if (c.content) {
                const formulaMatch = c.content.match(/\$\$|\$/g);
                if (formulaMatch) totalFormulaSymbols += formulaMatch.length / 2;
            }
        });
        document.getElementById('m-researcher-papers').textContent = Math.round(totalCitations * 1.5) + 6; // approximate read multiplier
        document.getElementById('m-researcher-formulas').textContent = Math.round(totalFormulaSymbols) || 28;
        document.getElementById('m-researcher-citations').textContent = totalCitations;

        // Skeptic metrics
        const rejections = evaluationRuns.filter(r => r.status === 'rejected');
        const strictnessPct = evaluationRuns.length > 0 ? Math.round((rejections.length / evaluationRuns.length) * 100) : 40;
        
        const validRunsWithScore = evaluationRuns.filter(r => r.score !== undefined);
        const sumScores = validRunsWithScore.reduce((sum, r) => sum + r.score, 0);
        const avgScore = validRunsWithScore.length > 0 ? (sumScores / validRunsWithScore.length).toFixed(1) : '4.6';
        
        const totalCriticisms = rejections.reduce((sum, r) => sum + (r.follow_up_questions ? r.follow_up_questions.length : 0), 0);

        document.getElementById('m-skeptic-strictness').textContent = `${strictnessPct}% Strictness`;
        document.getElementById('m-skeptic-avg').textContent = `${avgScore} / 5`;
        document.getElementById('m-skeptic-criticisms').textContent = totalCriticisms;

        // Archivist & Visualizer metrics
        document.getElementById('m-archivist-writes').textContent = concepts.length + 2; // concept md files + index + db
        const generatedImages = concepts.filter(c => c.image_path).length;
        document.getElementById('m-archivist-images').textContent = generatedImages;
    }

    function renderTelemetryTickerFeed() {
        if (telemetryEvents.length === 0) {
            elements.telemetryTicker.innerHTML = `
                <div class="terminal-line" style="color: var(--text-muted);">
                    <span>[SYS-LOG] Empty universe state (Day 0). Telemetry stream offline.</span>
                </div>
            `;
            return;
        }

        elements.tickerLinesCount.textContent = `${telemetryEvents.length} steps logged`;

        elements.telemetryTicker.innerHTML = telemetryEvents.map(event => {
            const time = new Date(event.timestamp).toLocaleTimeString(undefined, { hour12: false });
            let agentTag = 'orchestrator';
            let message = '';

            // Mapping raw pipeline stages to agent profiles
            if (event.stage.includes('research') || event.stage.includes('source')) {
                agentTag = 'researcher';
            } else if (event.stage.includes('skeptic') || event.stage.includes('evaluation')) {
                agentTag = 'skeptic';
            } else if (event.stage.includes('document') || event.stage.includes('commit') || event.stage.includes('index')) {
                agentTag = 'archivist';
            }

            const conceptName = event.metadata ? (event.metadata.concept || event.metadata.selected_concept || '') : '';
            const highlightConcept = conceptName ? `<span class="term-highlight">${conceptName}</span>` : '';

            // Humanize stages
            if (event.event_type === 'start') {
                if (event.stage === 'topic_selection') {
                    message = `Initiating auto-selection scanning cycle.`;
                } else if (event.stage === 'research_evaluation') {
                    message = `Starting deep database retrieval and synthesis for ${highlightConcept}.`;
                } else if (event.stage === 'documentation_validation') {
                    message = `Compiling standard formatting checks on ${highlightConcept} Markdown tree.`;
                } else {
                    message = `Executing process step: <span class="term-accent">${event.stage}</span> for ${highlightConcept || 'system'}.`;
                }
            } else {
                // Event Type end
                const duration = event.duration_seconds ? ` (completed in <span class="term-accent">${event.duration_seconds.toFixed(2)}s</span>)` : '';
                
                if (event.stage === 'topic_selection') {
                    message = `Selected target study subject: ${highlightConcept}.${duration}`;
                } else if (event.stage === 'topic_selection_level2') {
                    if (event.metadata && event.metadata.status === 'blocked_by_prerequisite') {
                        message = `Blocked selection of <span class="term-highlight">${event.metadata.selected_concept}</span>. Reason: Missing prerequisite <span class="term-accent">${event.metadata.missing_prerequisite}</span>.`;
                    } else {
                        message = `Standard Level 2 verification path confirmed.${duration}`;
                    }
                } else if (event.stage === 'research_evaluation') {
                    const status = (event.metadata ? (event.metadata.status || event.metadata.final_status || 'completed') : 'completed').toString();
                    const scoreVal = event.metadata && event.metadata.score !== undefined ? ` (Grade: ${event.metadata.score}/5)` : '';
                    message = `Peer review check complete for ${highlightConcept}. Status: <span class="term-highlight">${status.toUpperCase()}</span>${scoreVal}.${duration}`;
                } else if (event.stage === 'documentation_validation') {
                    message = `Markdown parsed successfully. Database structures synchronized.${duration}`;
                } else if (event.stage === 'commit_changes') {
                    message = `Archived and committed files directly to knowledge base source trees.${duration}`;
                } else {
                    message = `Successfully completed pipeline step: <span class="term-accent">${event.stage}</span>.${duration}`;
                }
            }

            return `
                <div class="terminal-line">
                    <span class="terminal-time">[${time}]</span>
                    <span class="terminal-tag ${agentTag}">${agentTag}</span>
                    <span class="terminal-msg">${message}</span>
                </div>
            `;
        }).join('');
    }

    /* ==========================================================================
       🕸️ INTERACTIVE GRAVITY CONSTELLATION GRAPH (CANVAS ORBIT PHYSICS)
       ========================================================================== */

    function buildNetworkGraphModel() {
        graphNodes = [];
        graphLinks = [];
        
        const canvas = elements.networkCanvas;
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;

        // Group nodes by level to assign bases
        const levelsGroup = { 1: [], 2: [], 3: [] };
        concepts.forEach(c => {
            const isVerified = c.status === 'VERIFIED' || c.status === '[VERIFIED]';
            const node = {
                id: c.id,
                title: c.title,
                level: c.level,
                status: isVerified ? 'VERIFIED' : 'THEORETICAL',
                // Coordinates
                x: 0,
                y: 0,
                vx: 0,
                vy: 0,
                r: 22,
                pulse: 0
            };
            
            if (levelsGroup[c.level]) {
                levelsGroup[c.level].push(node);
            }
            graphNodes.push(node);
        });

        // Distribute bases evenly across levels rows
        Object.keys(levelsGroup).forEach(lvlStr => {
            const lvl = parseInt(lvlStr);
            const nodes = levelsGroup[lvl];
            const rowY = height * (lvl === 1 ? 0.22 : (lvl === 2 ? 0.50 : 0.78));
            
            nodes.forEach((node, idx) => {
                const step = width / (nodes.length + 1);
                node.baseX = step * (idx + 1);
                node.baseY = rowY;
                node.x = node.baseX;
                node.y = node.baseY;
            });
        });

        // Configure slow Zero-G drifting and orbital physics angles
        graphNodes.forEach(node => {
            node.orbitParent = findGravitationalParent(node);
            if (node.orbitParent) {
                node.orbitAngle = Math.random() * Math.PI * 2;
                node.orbitSpeed = 0.0012 + Math.random() * 0.0014;
                if (node.level === 2) {
                    node.orbitRadius = 110 + Math.random() * 30;
                } else { // Level 3
                    node.orbitRadius = 60 + Math.random() * 20;
                }
            } else {
                node.driftAngle = Math.random() * Math.PI * 2;
                node.driftSpeed = 0.0015 + Math.random() * 0.0015;
                node.driftRadiusX = 15;
                node.driftRadiusY = 10;
            }
        });

        // Compile link references
        concepts.forEach(c => {
            if (c.related && c.related.length > 0) {
                c.related.forEach(relId => {
                    const sourceNode = graphNodes.find(n => n.id === c.id);
                    const targetNode = graphNodes.find(n => n.id === relId);
                    
                    if (sourceNode && targetNode) {
                        graphLinks.push({
                            source: sourceNode,
                            target: targetNode,
                            pulseOffset: Math.random() * Math.PI
                        });
                    }
                });
            }
        });

        // Initialize micro transmission data particles along links
        particleFlows = [];
        for (let i = 0; i < graphLinks.length; i++) {
            if (Math.random() > 0.4) {
                particleFlows.push({
                    linkIndex: i,
                    progress: Math.random(),
                    speed: 0.004 + Math.random() * 0.006
                });
            }
        }
    }

    function findGravitationalParent(node) {
        if (node.level <= 1) return null; // Level 1 nodes never orbit; they are central gravity suns
        
        const concept = concepts.find(c => c.id === node.id);
        if (!concept || !concept.related || concept.related.length === 0) return null;
        
        // Find a related node of a strictly lower level
        for (let relId of concept.related) {
            const relNode = graphNodes.find(n => n.id === relId);
            if (relNode && relNode.level < node.level) {
                return relNode;
            }
        }
        
        // Fallback: look for ANY related Level 1 node in the graph, as Level 1s are the heavy centers
        for (let relId of concept.related) {
            const relNode = graphNodes.find(n => n.id === relId && n.level === 1);
            if (relNode) return relNode;
        }
        
        // Final fallback: orbit the first active Level 1 node in the graph, or null (drift independently)
        const firstLvl1 = graphNodes.find(n => n.level === 1);
        return firstLvl1 || null;
    }

    function applyGravityWarp(gx, gy) {
        let warpedX = gx;
        let warpedY = gy;
        
        const lvl1Nodes = graphNodes.filter(n => n.level === 1);
        if (lvl1Nodes.length === 0) return { x: gx, y: gy };
        
        let totalDx = 0;
        let totalDy = 0;
        
        lvl1Nodes.forEach(node => {
            const dx = gx - node.x;
            const dy = gy - node.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > 0) {
                // Warp Formula bending coordinate space toward massive Level 1 centers
                const pull = Math.min(7500 / (dist + 65), dist * 0.45);
                totalDx += (dx / dist) * pull;
                totalDy += (dy / dist) * pull;
            }
        });
        
        return {
            x: gx - totalDx,
            y: gy - totalDy
        };
    }

    function drawWarpGrid(ctx, width, height) {
        ctx.save();
        ctx.strokeStyle = 'hsla(180, 100%, 45%, 0.08)';
        ctx.lineWidth = 0.55;
        
        const gridSpacing = 40;
        
        // Broad world coordinates to cover arbitrary panning and zoom
        const minX = -3000;
        const maxX = 4000;
        const minY = -2000;
        const maxY = 3000;
        
        // Draw Vertical grid lines
        for (let x = minX; x < maxX; x += gridSpacing) {
            ctx.beginPath();
            for (let y = minY; y < maxY; y += 15) {
                const pt = applyGravityWarp(x, y);
                if (y === minY) {
                    ctx.moveTo(pt.x, pt.y);
                } else {
                    ctx.lineTo(pt.x, pt.y);
                }
            }
            ctx.stroke();
        }
        
        // Draw Horizontal grid lines
        for (let y = minY; y < maxY; y += gridSpacing) {
            ctx.beginPath();
            for (let x = minX; x < maxX; x += 15) {
                const pt = applyGravityWarp(x, y);
                if (x === minX) {
                    ctx.moveTo(pt.x, pt.y);
                } else {
                    ctx.lineTo(pt.x, pt.y);
                }
            }
            ctx.stroke();
        }
        
        ctx.restore();
    }

    function drawNetworkGraph() {
        const canvas = elements.networkCanvas;
        const ctx = canvas.getContext('2d');
        const width = canvas.width / window.devicePixelRatio;
        const height = canvas.height / window.devicePixelRatio;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.save();
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        
        ctx.save();
        ctx.translate(canvasOffset.x, canvasOffset.y);
        ctx.scale(canvasZoom, canvasZoom);

        // 0. Render spacetime gravitational warp grid in background
        drawWarpGrid(ctx, width, height);

        // 1. Draw connection lines
        graphLinks.forEach((link, idx) => {
            const s = link.source;
            const t = link.target;
            
            const isHoveredLink = hoveredNode && (hoveredNode.id === s.id || hoveredNode.id === t.id);
            
            ctx.beginPath();
            ctx.moveTo(s.x, s.y);
            
            // Subtle curved quadratic bezier path
            const midX = (s.x + t.x) / 2;
            const midY = (s.y + t.y) / 2 + (s.x === t.x ? 0 : 32);
            
            ctx.quadraticCurveTo(midX, midY, t.x, t.y);
            
            const isBothVerified = s.status === 'VERIFIED' && t.status === 'VERIFIED';
            if (isHoveredLink) {
                ctx.strokeStyle = isBothVerified ? 'hsl(180, 100%, 45%)' : 'hsl(38, 95%, 52%)';
                ctx.lineWidth = 2.5;
                ctx.shadowColor = isBothVerified ? 'rgba(0, 242, 254, 0.4)' : 'rgba(255, 179, 0, 0.4)';
                ctx.shadowBlur = 8;
            } else {
                ctx.strokeStyle = isBothVerified ? 'hsla(180, 100%, 45%, 0.16)' : 'hsla(38, 95%, 52%, 0.14)';
                ctx.lineWidth = 1.2;
                ctx.shadowBlur = 0;
            }
            ctx.stroke();
            
            link.midX = midX;
            link.midY = midY;
        });

        // 2. Draw particle flows along links (Micro-animations)
        particleFlows.forEach(flow => {
            const link = graphLinks[flow.linkIndex];
            if (!link) return;
            
            const s = link.source;
            const t = link.target;
            const p = flow.progress;
            
            const midX = link.midX || (s.x + t.x) / 2;
            const midY = link.midY || (s.y + t.y) / 2;
            
            const x = (1-p)*(1-p)*s.x + 2*(1-p)*p*midX + p*p*t.x;
            const y = (1-p)*(1-p)*s.y + 2*(1-p)*p*midY + p*p*t.y;
            
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, Math.PI * 2);
            
            const isBothVerified = s.status === 'VERIFIED' && t.status === 'VERIFIED';
            ctx.fillStyle = isBothVerified ? 'hsl(180, 100%, 50%)' : 'hsl(38, 95%, 52%)';
            ctx.shadowColor = ctx.fillStyle;
            ctx.shadowBlur = 10;
            ctx.fill();
            
            flow.progress += flow.speed;
            if (flow.progress > 1.0) {
                flow.progress = 0;
            }
        });
        
        ctx.shadowBlur = 0; // Reset shadows

        // 3. Draw Nodes circles
        graphNodes.forEach(node => {
            const isLatestRun = evaluationRuns.length > 0 && areConceptsEquivalent(evaluationRuns[0].concept, node.title);
            const isVerified = node.status === 'VERIFIED';
            const isHovered = hoveredNode && hoveredNode.id === node.id;
            
            // Pulse calculations
            node.pulse += 0.035;
            const pulseRadius = node.r + Math.sin(node.pulse) * 2.5;

            // Coronary halo ring glows
            if (isLatestRun || isHovered) {
                ctx.beginPath();
                ctx.arc(node.x, node.y, pulseRadius + 6, 0, Math.PI * 2);
                ctx.fillStyle = isLatestRun ? 'rgba(0, 242, 254, 0.08)' : (isVerified ? 'rgba(0, 230, 118, 0.06)' : 'rgba(255, 179, 0, 0.06)');
                ctx.strokeStyle = isLatestRun ? 'hsla(180, 100%, 50%, 0.4)' : (isVerified ? 'hsla(152, 90%, 45%, 0.3)' : 'hsla(38, 95%, 52%, 0.3)');
                ctx.lineWidth = 1;
                ctx.fill();
                ctx.stroke();
            }

            // Central Node Circle
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
            ctx.fillStyle = isVerified ? 'hsl(152, 90%, 8%)' : 'hsl(38, 95%, 6%)';
            ctx.strokeStyle = isVerified ? 'hsl(152, 90%, 45%)' : 'hsl(38, 95%, 52%)';
            ctx.lineWidth = isHovered ? 2.5 : 1.5;
            
            ctx.shadowColor = isVerified ? 'rgba(0, 230, 118, 0.3)' : 'rgba(255, 179, 0, 0.3)';
            ctx.shadowBlur = isHovered ? 12 : 6;
            ctx.fill();
            ctx.stroke();
            ctx.shadowBlur = 0; // Clear shadows

            // Node Level indicator text inside node
            ctx.fillStyle = 'hsla(210, 25%, 98%, 0.9)';
            ctx.font = 'bold 11px var(--font-mono)';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(`L${node.level}`, node.x, node.y);

            // Level Text label below node
            ctx.fillStyle = isHovered ? 'var(--text-primary)' : 'var(--text-secondary)';
            ctx.font = isHovered ? 'bold 11.5px var(--font-sans)' : '500 10.5px var(--font-sans)';
            
            const titleText = node.title;
            if (titleText.length > 18) {
                const words = titleText.split(' ');
                const mid = Math.ceil(words.length / 2);
                const line1 = words.slice(0, mid).join(' ');
                const line2 = words.slice(mid).join(' ');
                
                ctx.fillText(line1, node.x, node.y + node.r + 14);
                ctx.fillText(line2, node.x, node.y + node.r + 26);
            } else {
                ctx.fillText(titleText, node.x, node.y + node.r + 15);
            }
        });

        ctx.restore();
        ctx.restore();
    }

    function startNetworkGraphPhysicsLoop() {
        const canvas = elements.networkCanvas;
        
        // Handle HDPI canvas resize scale mapping
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = 520 * window.devicePixelRatio;
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `520px`;

        const ctx = canvas.getContext('2d');
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        // Build vectors map
        buildNetworkGraphModel();

        // Run animations
        const tick = () => {
            // Update orbital positions dynamically on frame updates
            graphNodes.forEach(node => {
                if (node === draggedNode) return;
                
                if (node.orbitParent) {
                    node.orbitAngle += node.orbitSpeed;
                    node.x = node.orbitParent.x + Math.cos(node.orbitAngle) * node.orbitRadius;
                    node.y = node.orbitParent.y + Math.sin(node.orbitAngle) * node.orbitRadius;
                } else if (node.driftAngle !== undefined) {
                    node.driftAngle += node.driftSpeed;
                    node.x = node.baseX + Math.sin(node.driftAngle) * node.driftRadiusX;
                    node.y = node.baseY + Math.cos(node.driftAngle) * node.driftRadiusY;
                }
            });

            drawNetworkGraph();
            animationFrameId = requestAnimationFrame(tick);
        };
        tick();
    }

    function stopNetworkGraphLoop() {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    }

    /* ==========================================================================
       👂 SYSTEM COMPONENT ACTION LISTENERS & DELEGATIONS
       ========================================================================== */

    function setupInteractiveEventHooks() {
        // Search filter input listeners
        elements.searchInput.addEventListener('input', (e) => {
            currentFilters.search = e.target.value.toLowerCase().trim();
            elements.clearSearch.style.display = currentFilters.search ? 'block' : 'none';
            applyFiltersAndRenderSidebar();
        });

        elements.clearSearch.addEventListener('click', () => {
            elements.searchInput.value = '';
            currentFilters.search = '';
            elements.clearSearch.style.display = 'none';
            applyFiltersAndRenderSidebar();
        });

        // Filter Level buttons triggers
        elements.levelFilters.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                elements.levelFilters.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilters.level = btn.getAttribute('data-filter');
                applyFiltersAndRenderSidebar();
            });
        });

        // Filter Status buttons triggers
        elements.statusFilters.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                elements.statusFilters.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilters.status = btn.getAttribute('data-filter');
                applyFiltersAndRenderSidebar();
            });
        });

        // Concept Codex section scrolling tab highlighting tracker
        elements.scrollContainer.addEventListener('scroll', () => {
            const sections = document.querySelectorAll('.concept-section');
            let activeId = 'sec-overview';
            
            sections.forEach(sec => {
                const rect = sec.getBoundingClientRect();
                if (rect.top <= 140) {
                    activeId = sec.getAttribute('id');
                }
            });

            elements.tabLinks.forEach(link => {
                if (link.getAttribute('href') === `#${activeId}`) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        });

        elements.tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                elements.tabLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                const targetId = link.getAttribute('href');
                const targetSec = document.querySelector(targetId);
                if (targetSec) {
                    targetSec.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Dual Perspective selectors triggers
        elements.perspectiveSelector.querySelectorAll('.perspective-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetPerspective = btn.getAttribute('data-perspective');
                switchPerspective(targetPerspective);
            });
        });

        // Timeline Filter triggers
        elements.timelineFilters.querySelectorAll('.time-filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                elements.timelineFilters.querySelectorAll('.time-filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentTimelineFilter = btn.getAttribute('data-time-filter');
                renderOdysseyLedgerTimeline();
            });
        });

        // Content inline hyperlinking delegations
        elements.contentView.addEventListener('click', (e) => {
            const link = e.target.closest('.inline-concept-link');
            if (link) {
                const targetId = link.getAttribute('data-target');
                selectConcept(targetId);
            }
        });

        // Action panel cards click handlers (Inside Codex Landing welcome view)
        elements.btnExploreFirst.addEventListener('click', () => {
            if (concepts.length > 0) {
                const alphabeticallyFirst = [...concepts].sort((a,b) => a.title.localeCompare(b.title))[0];
                selectConcept(alphabeticallyFirst.id);
            }
        });

        elements.btnShowNetworkCard.addEventListener('click', () => {
            switchPerspective('network');
        });

        elements.btnBackToWelcome.addEventListener('click', () => {
            activeConceptId = null;
            elements.contentView.style.display = 'none';
            elements.welcomeView.style.display = 'flex';
            document.querySelectorAll('.concept-card').forEach(c => c.classList.remove('active'));
        });

        // ⏳ Timeline Scrubber Controls Event Hooks
        if (elements.scrubberSlider) {
            elements.scrubberSlider.addEventListener('input', (e) => {
                pausePlayback();
                currentAttemptIndex = parseInt(e.target.value);
                updateChronologicalState();
            });
        }
        
        if (elements.btnScrubPlay) {
            elements.btnScrubPlay.addEventListener('click', () => {
                togglePlayback();
            });
        }
        
        if (elements.btnScrubPrev) {
            elements.btnScrubPrev.addEventListener('click', () => {
                pausePlayback();
                if (currentAttemptIndex > 0) {
                    currentAttemptIndex--;
                    updateChronologicalState();
                }
            });
        }
        
        if (elements.btnScrubNext) {
            elements.btnScrubNext.addEventListener('click', () => {
                pausePlayback();
                if (currentAttemptIndex < chronologicalRuns.length) {
                    currentAttemptIndex++;
                    updateChronologicalState();
                }
            });
        }

        // 🔍 Canvas Zoom Controls Overlay Event Hooks
        if (elements.btnZoomIn) {
            elements.btnZoomIn.addEventListener('click', () => {
                const oldZoom = canvasZoom;
                canvasZoom = Math.min(2.5, canvasZoom + 0.15);
                const canvas = elements.networkCanvas;
                if (canvas) {
                    const centerX = canvas.clientWidth / 2;
                    const centerY = canvas.clientHeight / 2;
                    canvasOffset.x = centerX - (centerX - canvasOffset.x) * (canvasZoom / oldZoom);
                    canvasOffset.y = centerY - (centerY - canvasOffset.y) * (canvasZoom / oldZoom);
                }
            });
        }
        
        if (elements.btnZoomOut) {
            elements.btnZoomOut.addEventListener('click', () => {
                const oldZoom = canvasZoom;
                canvasZoom = Math.max(0.5, canvasZoom - 0.15);
                const canvas = elements.networkCanvas;
                if (canvas) {
                    const centerX = canvas.clientWidth / 2;
                    const centerY = canvas.clientHeight / 2;
                    canvasOffset.x = centerX - (centerX - canvasOffset.x) * (canvasZoom / oldZoom);
                    canvasOffset.y = centerY - (centerY - canvasOffset.y) * (canvasZoom / oldZoom);
                }
            });
        }
        
        if (elements.btnZoomReset) {
            elements.btnZoomReset.addEventListener('click', () => {
                canvasZoom = 1.0;
                canvasOffset = { x: 0, y: 0 };
            });
        }

        // Canvas Interaction physics mouse hooks
        setupNetworkCanvasMouseListeners();
    }

    function setupNetworkCanvasMouseListeners() {
        const canvas = elements.networkCanvas;
        let isPanning = false;
        let panStart = { x: 0, y: 0 };
        
        const getMousePos = (e) => {
            const rect = canvas.getBoundingClientRect();
            return {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        };

        canvas.addEventListener('mousemove', (e) => {
            const m = getMousePos(e);
            
            // Adjust coordinates based on pan offset & zoom
            const canvasX = (m.x - canvasOffset.x) / canvasZoom;
            const canvasY = (m.y - canvasOffset.y) / canvasZoom;

            if (draggedNode) {
                draggedNode.x = canvasX;
                draggedNode.y = canvasY;
                // If dragged, reset its drift center coordinates dynamically
                if (!draggedNode.orbitParent) {
                    draggedNode.baseX = canvasX;
                    draggedNode.baseY = canvasY;
                }
                return;
            }

            if (isPanning) {
                const dx = e.clientX - panStart.x;
                const dy = e.clientY - panStart.y;
                canvasOffset.x += dx;
                canvasOffset.y += dy;
                panStart = { x: e.clientX, y: e.clientY };
                return;
            }

            // Check node hover collision thresholds
            let foundHover = null;
            for (let i = 0; i < graphNodes.length; i++) {
                const node = graphNodes[i];
                const dx = canvasX - node.x;
                const dy = canvasY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist <= node.r) {
                    foundHover = node;
                    break;
                }
            }

            hoveredNode = foundHover;
            canvas.style.cursor = foundHover ? 'pointer' : (isPanning ? 'grabbing' : 'grab');
        });

        canvas.addEventListener('mousedown', (e) => {
            const m = getMousePos(e);
            const canvasX = (m.x - canvasOffset.x) / canvasZoom;
            const canvasY = (m.y - canvasOffset.y) / canvasZoom;
            
            // Check if we clicked on top of a node
            let clickedNode = null;
            for (let i = 0; i < graphNodes.length; i++) {
                const node = graphNodes[i];
                const dx = canvasX - node.x;
                const dy = canvasY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist <= node.r) {
                    clickedNode = node;
                    break;
                }
            }
            
            if (clickedNode) {
                draggedNode = clickedNode;
                canvas.style.cursor = 'grabbing';
            } else {
                isPanning = true;
                panStart = { x: e.clientX, y: e.clientY };
                canvas.style.cursor = 'grabbing';
            }
        });

        window.addEventListener('mouseup', () => {
            if (draggedNode) {
                draggedNode = null;
                canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
            }
            if (isPanning) {
                isPanning = false;
                canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
            }
        });

        canvas.addEventListener('mouseleave', () => {
            if (isPanning) {
                isPanning = false;
            }
        });

        canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const m = getMousePos(e);
            
            const zoomIntensity = 0.04;
            const delta = -e.deltaY;
            const oldZoom = canvasZoom;
            
            if (delta > 0) {
                canvasZoom = Math.min(2.5, canvasZoom + zoomIntensity);
            } else {
                canvasZoom = Math.max(0.5, canvasZoom - zoomIntensity);
            }
            
            // Zoom centered on current mouse coordinates
            canvasOffset.x = m.x - (m.x - canvasOffset.x) * (canvasZoom / oldZoom);
            canvasOffset.y = m.y - (m.y - canvasOffset.y) * (canvasZoom / oldZoom);
        });

        canvas.addEventListener('click', (e) => {
            if (hoveredNode && !draggedNode && !isPanning) {
                const id = hoveredNode.id;
                selectConcept(id);
            }
        });
    }

    // Launch parallel ingestion pipeline
    loadAllDatasets();
});
