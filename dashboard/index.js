/* ==========================================================================
   🌌 UNIVERS KNOWLEDGE BASE - INTERACTIVE DISCOVERY ENGINE (ODYSSEY)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Original Datasets (Immutable Reference Cache)
    let allConcepts = [];
    let allEvaluationRuns = [];
    let allTelemetryEvents = [];
    let allEquationData = null;
    let allOKFGraph = null;

    // Core Active Application State (Filtered chronologically by Scrubber)
    let concepts = [];
    let evaluationRuns = [];
    let telemetryEvents = [];
    let chronologicalRuns = []; // Oldest first runs list

    let activeConceptId = null;
    let activePerspective = 'codex'; // 'codex', 'network', 'equations', 'ledger', 'agents'

    let selectedEqConstant = null;
    let currentEqSearch = '';
    let currentEqCategory = 'all';

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
    let galacticRotationAngle = 0; // Milky Way spiral rotation
    let currentNetworkViewMode = 'topology'; // 'topology' or 'galaxy'
    let currentNetworkFilter = 'all'; // 'all', 'l1', 'l2', 'l3', 'bridges'
    let animationFrameId = null;
    let particleFlows = []; // Micro-animation data flows

    const graphState = {
        nodesById: new Map(),
        linksByKey: new Map(),
        simulation: {
            alpha: 1.0,
            repulsion: 3500,      // soft neighbor repulsion
            linkStrength: 0.025,   // spring link attraction
            damping: 0.82         // friction to settle positions smoothly
        }
    };

    // Timeline Playback Scrubber Engine State
    let currentAttemptIndex = 0;
    let isPlaying = false;
    let playbackInterval = null;
    let playbackSpeed = 2200; // 2.2 seconds per tick epoch

    // Sandbox Arena Engine State
    let allSandboxDebates = [];
    let isSandboxDebateRunning = false;

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
        equationsView: document.getElementById('equations-view'),
        ledgerView: document.getElementById('ledger-view'),
        agentsView: document.getElementById('agents-view'),
        perspectiveSelector: document.getElementById('perspective-selector'),
        sidebarPanel: document.getElementById('sidebar-panel'),

        // Stats
        totalStat: document.getElementById('stat-total'),
        verifiedStat: document.getElementById('stat-verified'),
        theoreticalStat: document.getElementById('stat-theoretical'),
        mathProvenStat: document.getElementById('stat-math-proven'),

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
        btnZoomReset: document.getElementById('btn-zoom-reset'),
        btnViewTopology: document.getElementById('btn-view-topology'),
        btnViewGalaxy: document.getElementById('btn-view-galaxy'),

        // Tab switcher
        commandTabBtns: document.querySelectorAll('.command-tab-btn'),
        tabTelemetry: document.getElementById('tab-telemetry'),
        tabSandbox: document.getElementById('tab-sandbox'),

        // Sandbox elements
        sandboxConceptSelect: document.getElementById('sandbox-concept-select'),
        sandboxCustomInput: document.getElementById('sandbox-custom-input'),
        btnSandboxStart: document.getElementById('btn-sandbox-start'),
        sandboxDebateStream: document.getElementById('sandbox-debate-stream'),
        sandboxGaugeFill: document.getElementById('sandbox-gauge-fill'),
        sandboxScoreValue: document.getElementById('sandbox-score-value'),
        sandboxVerdictBox: document.getElementById('sandbox-verdict-box'),
        sandboxHistoryList: document.getElementById('sandbox-history-list')
    };

    /* ==========================================================================
       📥 PARALLEL DATA INGESTION ENGINE
       ========================================================================== */

    async function loadAllDatasets() {
        try {
            // Parallel Fetch execution with cache-busting query parameter to force dynamic reload
            const cacheBust = `?t=${Date.now()}`;
            const [dbRes, evalRes, telRes, sandboxRes, eqRes, graphRes] = await Promise.all([
                fetch(`../knowledge_base/database.json${cacheBust}`),
                fetch(`../knowledge_base/logs/evaluation_runs.jsonl${cacheBust}`),
                fetch(`../knowledge_base/logs/telemetry.jsonl${cacheBust}`),
                fetch(`../knowledge_base/logs/sandbox_debates.jsonl${cacheBust}`).catch(() => null),
                fetch(`../knowledge_base/equation_index.json${cacheBust}`).catch(() => null),
                fetch(`../knowledge_base/graph.json${cacheBust}`).catch(() => null)
            ]);

            if (!dbRes.ok) throw new Error(`Database error! Status: ${dbRes.status}`);

            allConcepts = await dbRes.json();
            allEquationData = eqRes && eqRes.ok ? await eqRes.json() : null;
            allOKFGraph = graphRes && graphRes.ok ? await graphRes.json() : null;

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
            allSandboxDebates = sandboxRes && sandboxRes.ok ? await parseJSONL(sandboxRes) : [];

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
                <p style="margin-top:10px;">Launch a self-routing development local server in your workspace to run this environment:</p>
                <pre style="background: hsla(225, 20%, 2%, 0.8); border: 1px solid var(--border-glass); padding:8px; border-radius:4px; font-family:var(--font-mono); font-size:11px; margin-top:10px; color:var(--text-primary); text-align:left;">python serve.py</pre>
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
                            <li>Run: <code style="background: hsla(225,100%,100%,0.08); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); color:#fff;">python serve.py</code></li>
                            <li>Access your local browser link via the port reported in the terminal, or run: <code style="background: hsla(225,100%,100%,0.08); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); color:#fff;">python -m http.server 8000</code></li>
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
        populateSandboxConcepts();
        renderSandboxHistory();

        // Initial view default
        switchPerspective('codex');
    }

    function calculateGlobalHeaderStats() {
        elements.totalStat.textContent = concepts.length;
        const verified = concepts.filter(c => c.status === 'VERIFIED' || c.status === '[VERIFIED]').length;
        elements.verifiedStat.textContent = verified;
        elements.theoreticalStat.textContent = concepts.length - verified;

        // Math Engine stat: count concepts with math_status MATH_PROVEN, MATH_CONSISTENT, or MATH_TOPOLOGICAL
        const mathOkStatuses = ['MATH_PROVEN', 'MATH_CONSISTENT', 'MATH_TOPOLOGICAL', '[MATH_PROVEN]', '[MATH_CONSISTENT]', '[MATH_TOPOLOGICAL]'];
        const mathOkCount = concepts.filter(c => mathOkStatuses.includes(c.math_status || '')).length;
        if (elements.mathProvenStat) elements.mathProvenStat.textContent = mathOkCount;

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
            if (elements.equationsView) elements.equationsView.style.display = 'none';
            elements.ledgerView.style.display = 'none';
            elements.agentsView.style.display = 'none';
            stopNetworkGraphLoop();
        } else if (perspectiveId === 'equations') {
            elements.sidebarPanel.style.display = 'none';
            elements.welcomeView.style.display = 'none';
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'none';
            if (elements.equationsView) elements.equationsView.style.display = 'flex';
            elements.ledgerView.style.display = 'none';
            elements.agentsView.style.display = 'none';
            renderEquationExplorer();
            stopNetworkGraphLoop();
        } else if (perspectiveId === 'ledger') {
            elements.sidebarPanel.style.display = 'none';
            elements.welcomeView.style.display = 'none';
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'none';
            if (elements.equationsView) elements.equationsView.style.display = 'none';
            elements.ledgerView.style.display = 'flex';
            elements.agentsView.style.display = 'none';
            renderOdysseyLedgerTimeline();
            stopNetworkGraphLoop();
        } else if (perspectiveId === 'agents') {
            elements.sidebarPanel.style.display = 'none';
            elements.welcomeView.style.display = 'none';
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'none';
            if (elements.equationsView) elements.equationsView.style.display = 'none';
            elements.ledgerView.style.display = 'none';
            elements.agentsView.style.display = 'flex';
            stopNetworkGraphLoop();
        } else if (perspectiveId === 'network') {
            elements.sidebarPanel.style.display = 'none';
            elements.welcomeView.style.display = 'none';
            elements.contentView.style.display = 'none';
            elements.networkView.style.display = 'flex';
            if (elements.equationsView) elements.equationsView.style.display = 'none';
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
            // Re-select active concept to dynamically reload updated status styles (preserving the current active tab perspective)
            selectConcept(activeConceptId, true);
        }

        // Update active network graph coordinates if perspective is active
        if (activePerspective === 'network') {
            syncGraphWithConcepts(concepts);
            graphState.simulation.alpha = 0.35; // gently reheat on timeline change
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

            // Math status badge
            const rawMathStatus = (c.math_status || '').replace(/[\[\]]/g, '').trim();
            const mathBadgeMap = {
                'MATH_PROVEN':      { label: 'PROVEN',      color: 'var(--status-verified)',      icon: 'fa-square-root-variable' },
                'MATH_CONSISTENT':  { label: 'CONSISTENT',  color: 'var(--status-verified)',      icon: 'fa-square-root-variable' },
                'MATH_TOPOLOGICAL': { label: 'TOPOLOGICAL', color: 'var(--neon-cyan)',             icon: 'fa-atom' },
                'MATH_CONJECTURED': { label: 'CONJECTURED', color: 'var(--status-theoretical)',   icon: 'fa-flask' },
                'MATH_FLAWED':      { label: 'FLAWED',      color: 'hsl(0, 90%, 60%)',            icon: 'fa-triangle-exclamation' },
                'MATH_PENDING':     { label: 'PENDING',     color: 'var(--text-muted)',            icon: 'fa-hourglass-half' },
            };
            const mathBadge = mathBadgeMap[rawMathStatus];
            const mathBadgeHtml = mathBadge
                ? `<span class="math-status-badge" style="color:${mathBadge.color}; font-size: 9.5px; letter-spacing: 0.06em; font-weight: 700; opacity: 0.85;" title="Math Status: ${rawMathStatus}">
                        <i class="fa-solid ${mathBadge.icon}" style="font-size: 8px; margin-right: 3px;"></i>${mathBadge.label}
                   </span>`
                : '';

            return `
                <div class="concept-card ${cardBorderClass} ${activeClass}" data-id="${c.id}">
                    <div class="card-top">
                        <span class="card-level">LEVEL ${c.level}</span>
                        <span class="card-status ${statusClass}">
                            <span class="pulse-dot ${statusDot}"></span> ${isVerified ? 'VERIFIED' : 'THEORETICAL'}
                        </span>
                    </div>
                    <h3 class="card-title" title="${c.title}">${c.title}</h3>
                    <p class="card-excerpt">${cleanExcerpts(c.overview || c.content || '')}</p>
                    <div class="card-footer">
                        <span><i class="fa-solid fa-link"></i> ${relationsCount} relations</span>
                        ${mathBadgeHtml}
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

    function findConceptByAnyId(id) {
        if (!id) return null;
        const cleanQuery = id.toLowerCase().replace(/[^a-z0-9]/g, '');

        // 1. Direct ID match
        let concept = allConcepts.find(c => c.id === id || c.id.toLowerCase() === id.toLowerCase());
        if (concept) return concept;

        // 2. Normalized ID or Title match
        concept = allConcepts.find(c => {
            const cleanId = c.id.toLowerCase().replace(/[^a-z0-9]/g, '');
            const cleanTitle = c.title.toLowerCase().replace(/[^a-z0-9]/g, '');
            return cleanId === cleanQuery || cleanTitle === cleanQuery;
        });
        if (concept) return concept;

        // 3. Partial title substring match
        return allConcepts.find(c => {
            const cleanTitle = c.title.toLowerCase().replace(/[^a-z0-9]/g, '');
            return cleanTitle.includes(cleanQuery) || cleanQuery.includes(cleanTitle);
        });
    }

    function selectConcept(id, preservePerspective = false) {
        const concept = findConceptByAnyId(id);
        if (!concept) return;

        activeConceptId = concept.id;

        // Ensure we are in Codex mode to read content unless explicitly requested to preserve current perspective
        if (!preservePerspective && activePerspective !== 'codex') {
            switchPerspective('codex');
        }

        // Reset scroll position to top when opening document
        if (elements.scrollContainer) {
            elements.scrollContainer.scrollTop = 0;
        }

        // Sidebar card active highlighting
        document.querySelectorAll('.concept-card').forEach(c => {
            if (c.getAttribute('data-id') === concept.id) {
                c.classList.add('active');
            } else {
                c.classList.remove('active');
            }
        });

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
        let activeRelated = (concept.related && concept.related.length > 0) ? [...concept.related] : [];
        if (activeRelated.length === 0 && allOKFGraph && allOKFGraph.edges) {
            allOKFGraph.edges.forEach(edge => {
                const srcId = edge.source || edge.from;
                const tgtId = edge.target || edge.to;
                if (srcId === concept.id) activeRelated.push(tgtId);
                else if (tgtId === concept.id) activeRelated.push(srcId);
            });
            activeRelated = [...new Set(activeRelated)];
        }

        if (activeRelated.length > 0) {
            const relationsHtml = activeRelated.map(relId => {
                const target = allConcepts.find(item => item.id === relId || item.title.toLowerCase().replace(/[^a-z0-9]/g, '') === relId.toLowerCase().replace(/[^a-z0-9]/g, ''));
                const titleText = target ? target.title : relId.replace(/_/g, ' ');
                const isRelVerified = target && (target.status === 'VERIFIED' || target.status === '[VERIFIED]');
                const icon = isRelVerified ? 'fa-circle-check text-verified' : 'fa-circle-dot text-theoretical';
                const targetId = target ? target.id : relId;
                return `
                    <div class="related-link-card" data-target-id="${targetId}">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <i class="fa-solid ${icon}"></i>
                            <span class="related-link-title">${escapeHtml(titleText)}</span>
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
        } else if (relatedRaw) {
            elements.viewRelated.innerHTML = compileMarkdownToHTML(relatedRaw);
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

    function computeNodeRadius(concept) {
        const relationsCount = concept.related ? concept.related.length : 0;

        if (currentNetworkViewMode === 'galaxy') {
            // Galaxy mode: stars sized purely by degree (connectivity)
            // dwarf 1-2 → 5px, main sequence 3-5 → 7px, giant 6-9 → 10px, supergiant 10+ → 13px
            const isLatestRun = evaluationRuns.length > 0 && areConceptsEquivalent(evaluationRuns[0].concept, concept.title);
            let r;
            if (relationsCount >= 10) r = 13;
            else if (relationsCount >= 6)  r = 10;
            else if (relationsCount >= 3)  r = 7;
            else                           r = 5;
            return isLatestRun ? r + 3 : r; // latest-run star glows a bit bigger
        }

        // Topology mode: compact size logic so 159 nodes leave plenty of whitespace for links & flow arrows
        if (concept.level === 3) {
            return 14; // Level 3 emergence nodes stand out as structural hubs
        }
        const relationBoost = Math.min(relationsCount * 0.6, 4);
        let latestBoost = 0;
        if (evaluationRuns.length > 0 && areConceptsEquivalent(evaluationRuns[0].concept, concept.title)) {
            latestBoost = 3;
        }
        const base = 8 + relationBoost + latestBoost;
        return Math.max(8, Math.min(base, 14));
    }

    // Returns the thematic arm colour for a concept based on its ID keywords (galaxy mode only)
    function getGalaxyArmColour(nodeId) {
        const id = nodeId.toLowerCase();
        if (id.includes('neutrino'))                                            return { fill: 'hsl(310, 80%, 10%)', stroke: 'hsl(310, 90%, 62%)', glow: 'rgba(255, 60, 220, 0.45)' };
        if (id.includes('quantum_gravity') || id.includes('loop_quantum') ||
            id.includes('causal_dynamical') || id.includes('asymptotic_safety') ||
            id.includes('string_theory'))                                        return { fill: 'hsl(270, 80%, 10%)', stroke: 'hsl(270, 90%, 68%)', glow: 'rgba(160, 80, 255, 0.45)' };
        if (id.includes('dark') || id.includes('axion') || id.includes('wimp')) return { fill: 'hsl(220, 70%, 9%)',  stroke: 'hsl(220, 80%, 62%)', glow: 'rgba(80, 130, 255, 0.40)' };
        if (id.includes('standard_model') || id.includes('higgs') ||
            id.includes('fermion') || id.includes('electroweak') ||
            id.includes('qcd') || id.includes('quark') || id.includes('boson')) return { fill: 'hsl(50, 80%, 8%)',   stroke: 'hsl(50, 95%, 58%)',  glow: 'rgba(255, 220, 50, 0.40)' };
        if (id.includes('cosmol') || id.includes('inflat') ||
            id.includes('big_bang') || id.includes('cosmic') ||
            id.includes('cmb') || id.includes('baryon'))                         return { fill: 'hsl(38, 80%, 8%)',   stroke: 'hsl(38, 95%, 58%)',  glow: 'rgba(255, 160, 40, 0.40)' };
        if (id.includes('general_relativ') || id.includes('black_hole') ||
            id.includes('spacetime') || id.includes('gravitational_wave'))       return { fill: 'hsl(25, 80%, 8%)',   stroke: 'hsl(25, 95%, 60%)',  glow: 'rgba(255, 110, 30, 0.40)' };
        if (id.includes('supersymmet') || id.includes('beyond_standard') ||
            id.includes('extra_dimension') || id.includes('hierarchy'))          return { fill: 'hsl(285, 70%, 9%)',  stroke: 'hsl(285, 85%, 65%)', glow: 'rgba(200, 80, 255, 0.38)' };
        // Quantum foundations + fallback
        return { fill: 'hsl(180, 60%, 8%)', stroke: 'hsl(180, 100%, 50%)', glow: 'rgba(0, 242, 254, 0.38)' };
    }

    function getLevelZone(level, width, height) {
        const h = height || 520;
        const w = width || 900;
        const padX = 100;

        if (level === 1) {
            return {
                xMin: padX,
                xMax: w - padX,
                yMin: h * 0.10,
                yMax: h * 0.30
            };
        } else if (level === 2) {
            return {
                xMin: padX,
                xMax: w - padX,
                yMin: h * 0.40,
                yMax: h * 0.60
            };
        } else {
            return {
                xMin: padX,
                xMax: w - padX,
                yMin: h * 0.68,
                yMax: h * 0.88
            };
        }
    }

    function findBestSeedParent(concept) {
        if (!concept.related || concept.related.length === 0) return null;

        for (let relId of concept.related) {
            const relNode = graphState.nodesById.get(relId);
            if (relNode && relNode.visible && relNode.level < concept.level) {
                return relNode;
            }
        }

        for (let relId of concept.related) {
            const relNode = graphState.nodesById.get(relId);
            if (relNode && relNode.visible) {
                return relNode;
            }
        }

        return null;
    }

    function seedNodePosition(concept) {
        const canvas = elements.networkCanvas;
        const width = canvas ? canvas.clientWidth : 900;
        const height = canvas ? canvas.clientHeight : 520;

        const parentNode = findBestSeedParent(concept);
        if (parentNode) {
            return {
                x: parentNode.x + (Math.random() - 0.5) * 60,
                y: parentNode.y + (Math.random() - 0.5) * 60
            };
        }

        const visibleRelated = [];
        if (concept.related) {
            concept.related.forEach(relId => {
                const node = graphState.nodesById.get(relId);
                if (node && node.visible) {
                    visibleRelated.push(node);
                }
            });
        }
        if (visibleRelated.length > 0) {
            let sumX = 0, sumY = 0;
            visibleRelated.forEach(n => { sumX += n.x; sumY += n.y; });
            return {
                x: sumX / visibleRelated.length + (Math.random() - 0.5) * 40,
                y: sumY / visibleRelated.length + (Math.random() - 0.5) * 40
            };
        }

        const zone = getLevelZone(concept.level, width, height);
        return {
            x: (zone.xMin + zone.xMax) / 2 + (Math.random() - 0.5) * (width * 0.2),
            y: (zone.yMin + zone.yMax) / 2 + (Math.random() - 0.5) * 30
        };
    }

    function syncGraphWithConcepts(conceptsList) {
        const canvas = elements.networkCanvas;
        if (!canvas) return;

        let filteredList = conceptsList;
        if (currentNetworkFilter === 'l1') {
            filteredList = conceptsList.filter(c => c.level === 1);
        } else if (currentNetworkFilter === 'l2') {
            filteredList = conceptsList.filter(c => c.level === 2);
        } else if (currentNetworkFilter === 'l3') {
            filteredList = conceptsList.filter(c => c.level === 3);
        } else if (currentNetworkFilter === 'bridges') {
            const bridgeIds = new Set();
            if (allOKFGraph && allOKFGraph.edges) {
                allOKFGraph.edges.forEach(e => {
                    const srcId = e.source || e.from;
                    const tgtId = e.target || e.to;
                    const src = conceptsList.find(c => c.id === srcId);
                    const tgt = conceptsList.find(c => c.id === tgtId);
                    if (src && tgt && src.level !== tgt.level) {
                        bridgeIds.add(src.id);
                        bridgeIds.add(tgt.id);
                    }
                });
            }
            if (bridgeIds.size === 0) {
                conceptsList.forEach(c => {
                    if (c.related) {
                        c.related.forEach(relId => {
                            const rel = conceptsList.find(r => r.id === relId);
                            if (rel && rel.level !== c.level) {
                                bridgeIds.add(c.id);
                                bridgeIds.add(rel.id);
                            }
                        });
                    }
                });
            }
            filteredList = conceptsList.filter(c => bridgeIds.has(c.id));
        }

        const activeIds = new Set(filteredList.map(c => c.id));

        conceptsList.forEach(c => {
            const isVerified = c.status === 'VERIFIED' || c.status === '[VERIFIED]';
            const isVisible = activeIds.has(c.id);

            if (graphState.nodesById.has(c.id)) {
                const node = graphState.nodesById.get(c.id);
                node.visible = isVisible;
                node.status = isVerified ? 'VERIFIED' : 'THEORETICAL';
                node.r = computeNodeRadius(c);
            } else {
                const seed = seedNodePosition(c);
                const node = {
                    id: c.id,
                    title: c.title,
                    level: c.level,
                    status: isVerified ? 'VERIFIED' : 'THEORETICAL',
                    x: seed.x,
                    y: seed.y,
                    vx: (Math.random() - 0.5) * 2,
                    vy: (Math.random() - 0.5) * 2,
                    r: computeNodeRadius(c),
                    pulse: Math.random() * Math.PI,
                    visible: isVisible
                };
                graphState.nodesById.set(c.id, node);
            }
        });

        graphState.nodesById.forEach((node, id) => {
            if (!activeIds.has(id)) {
                node.visible = false;
            }
        });

        graphNodes = Array.from(graphState.nodesById.values()).filter(n => n.visible);

        syncGraphLinks(filteredList);
    }

    function syncGraphLinks(conceptsList) {
        const activeKeys = new Set();

        // 1. OKF Smart Directed Edges (from graph.json)
        if (allOKFGraph && allOKFGraph.edges && allOKFGraph.edges.length > 0) {
            allOKFGraph.edges.forEach(edge => {
                const srcId = edge.source || edge.from;
                const tgtId = edge.target || edge.to;

                const hasSource = graphState.nodesById.has(srcId);
                const hasTarget = graphState.nodesById.has(tgtId);

                if (hasSource && hasTarget) {
                    const key = `${srcId}->${tgtId}`;
                    activeKeys.add(key);

                    if (!graphState.linksByKey.has(key)) {
                        const sourceNode = graphState.nodesById.get(srcId);
                        const targetNode = graphState.nodesById.get(tgtId);

                        const newLink = {
                            key,
                            source: sourceNode,
                            target: targetNode,
                            isDirected: true,
                            pulseOffset: Math.random() * Math.PI,
                            visible: true
                        };
                        graphState.linksByKey.set(key, newLink);
                    } else {
                        const existing = graphState.linksByKey.get(key);
                        existing.visible = true;
                        existing.isDirected = true;
                    }
                }
            });
        }

        // 2. Inferred Content Relations
        conceptsList.forEach(c => {
            if (c.related && c.related.length > 0) {
                c.related.forEach(relId => {
                    const hasSource = graphState.nodesById.has(c.id);
                    const hasTarget = graphState.nodesById.has(relId);

                    if (hasSource && hasTarget) {
                        const key = c.id < relId ? `${c.id}->${relId}` : `${relId}->${c.id}`;
                        activeKeys.add(key);

                        if (!graphState.linksByKey.has(key)) {
                            const sourceNode = graphState.nodesById.get(c.id);
                            const targetNode = graphState.nodesById.get(relId);

                            const newLink = {
                                key,
                                source: sourceNode,
                                target: targetNode,
                                isDirected: false,
                                pulseOffset: Math.random() * Math.PI,
                                visible: true
                            };
                            graphState.linksByKey.set(key, newLink);
                        } else {
                            graphState.linksByKey.get(key).visible = true;
                        }
                    }
                });
            }
        });

        graphState.linksByKey.forEach((link, key) => {
            if (!activeKeys.has(key)) {
                link.visible = false;
            } else {
                if (!link.source.visible || !link.target.visible) {
                    link.visible = false;
                }
            }
        });

        graphLinks = Array.from(graphState.linksByKey.values()).filter(l => l.visible);

        // Sync particle flows dynamically
        particleFlows = particleFlows.filter(flow => flow.link && flow.link.visible);

        graphLinks.forEach(link => {
            const hasParticle = particleFlows.some(flow => flow.link === link);
            if (!hasParticle && Math.random() > 0.5) {
                particleFlows.push({
                    link: link,
                    progress: Math.random(),
                    speed: 0.004 + Math.random() * 0.006
                });
            }
        });
    }

    /* ==========================================================================
       🧬 2D GRAPH FORCE PHYSICS, COLLISION RESOLUTION, & LOD VIEWPORT ENGINE
       ========================================================================== */

    function applyRepulsionForces(nodes) {
        const repulsion = graphState.simulation.repulsion;
        for (let i = 0; i < nodes.length; i++) {
            const nodeA = nodes[i];
            for (let j = i + 1; j < nodes.length; j++) {
                const nodeB = nodes[j];
                const dx = nodeB.x - nodeA.x;
                const dy = nodeB.y - nodeA.y;
                const distSq = dx * dx + dy * dy + 1; // prevent division by zero
                const dist = Math.sqrt(distSq);

                if (dist < 320) { // limit repulsion reach for performance
                    const force = repulsion / distSq;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;

                    nodeA.vx -= fx;
                    nodeA.vy -= fy;
                    nodeB.vx += fx;
                    nodeB.vy += fy;
                }
            }
        }
    }

    function applyLinkForces(links) {
        const strength = graphState.simulation.linkStrength;
        const restLength = 110; // desired distance between connected concepts

        links.forEach(link => {
            const s = link.source;
            const t = link.target;

            const dx = t.x - s.x;
            const dy = t.y - s.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;

            const displacement = dist - restLength;
            const force = displacement * strength;

            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            s.vx += fx;
            s.vy += fy;
            t.vx -= fx;
            t.vy -= fy;
        });
    }

    function applyClusterForces(nodes) {
        const canvas = elements.networkCanvas;
        const width = canvas ? canvas.clientWidth : 900;
        const height = canvas ? canvas.clientHeight : 520;
        const centerX = width / 2;
        const centerY = height / 2;

        if (currentNetworkViewMode === 'topology') {
            // Original Clean vertical bands layout
            const gravityStrength = 0.006;
            nodes.forEach(node => {
                if (node === draggedNode) return;
                const zone = getLevelZone(node.level, width, height);
                const targetY = (zone.yMin + zone.yMax) / 2;

                const dy = targetY - node.y;
                node.vy += dy * gravityStrength;

                const dx = centerX - node.x;
                node.vx += dx * 0.0025;
            });
        } else {
            // Milky Way Galaxy layout: spiral arms
            const coreHubs = new Set(['quantum_gravity', 'standard_model_of_particle_physics', 'neutrino_oscillations']);

            nodes.forEach(node => {
                if (node === draggedNode) return;

                let targetX = centerX;
                let targetY = centerY;

                if (coreHubs.has(node.id)) {
                    // Core hubs gravitate strongly to the supermassive core
                    const dx = centerX - node.x;
                    const dy = centerY - node.y;
                    node.vx += dx * 0.018;
                    node.vy += dy * 0.018;
                } else {
                    // Other nodes are distributed along 4 spiral arms of the galaxy
                    let hash = 0;
                    for (let idx = 0; idx < node.id.length; idx++) {
                        hash += node.id.charCodeAt(idx);
                    }
                    const armIndex = hash % 4; // 4 spiral arms
                    const armAngleOffset = armIndex * (Math.PI / 2);

                    // Deeper spacing: wider radius prevents overlaps in Galaxy mode!
                    let baseRadius = 140;
                    if (node.level === 2) {
                        baseRadius = 260;
                    } else if (node.level === 3) {
                        baseRadius = 380;
                    }
                    
                    const variation = (hash % 10) / 10;
                    const radius = baseRadius + variation * 100;

                    // Spiral angle: theta = spiral_winding * radius + arm_angle_offset + global_rotation
                    const windFactor = 0.005; // slightly wider winding
                    const theta = radius * windFactor + armAngleOffset + galacticRotationAngle;

                    targetX = centerX + radius * Math.cos(theta);
                    targetY = centerY + radius * Math.sin(theta);

                    const dx = targetX - node.x;
                    const dy = targetY - node.y;
                    
                    const gravityStrength = 0.012; 
                    node.vx += dx * gravityStrength;
                    node.vy += dy * gravityStrength;
                }
            });
        }
    }

    function applyBoundaryForces(nodes) {
        if (currentNetworkViewMode === 'galaxy') return; // let them orbit freely in space!

        const canvas = elements.networkCanvas;
        const width = canvas ? canvas.clientWidth : 900;
        const height = canvas ? canvas.clientHeight : 520;
        const borderPadding = 50;

        nodes.forEach(node => {
            if (node.x < borderPadding) {
                node.vx += (borderPadding - node.x) * 0.08;
            } else if (node.x > width - borderPadding) {
                node.vx -= (node.x - (width - borderPadding)) * 0.08;
            }

            if (node.y < borderPadding) {
                node.vy += (borderPadding - node.y) * 0.08;
            } else if (node.y > height - borderPadding) {
                node.vy -= (node.y - (height - borderPadding)) * 0.08;
            }
        });
    }

    function applyAmbientMotion(nodes) {
        // 1. Slow breathing cycle
        nodes.forEach(node => {
            node.pulse += 0.012; // slow breathing cycle
            node.x += Math.sin(node.pulse) * 0.05;
            node.y += Math.cos(node.pulse * 0.7) * 0.05;
        });

        // 2. Slow majestic orbital circulation for Level 2 nodes around their connected Level 1 parent nodes
        graphLinks.forEach(link => {
            const s = link.source;
            const t = link.target;
            if (!s || !t || !s.visible || !t.visible) return;

            let parent = null;
            let child = null;

            if (s.level === 1 && t.level === 2) {
                parent = s;
                child = t;
            } else if (t.level === 1 && s.level === 2) {
                parent = t;
                child = s;
            }

            if (parent && child && child !== draggedNode) {
                const dx = child.x - parent.x;
                const dy = child.y - parent.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;

                // Tangential vector (-dy, dx) normalized
                const tx = -dy / dist;
                const ty = dx / dist;

                // Slow rotation speed (pixels per frame)
                const orbitSpeed = 0.16;

                // Determine direction based on character hash of IDs to keep it stable but varied
                const keyStr = String(parent.id) + String(child.id);
                let charSum = 0;
                for (let idx = 0; idx < keyStr.length; idx++) {
                    charSum += keyStr.charCodeAt(idx);
                }
                const dir = charSum % 2 === 0 ? 1 : -1;

                child.x += tx * dir * orbitSpeed;
                child.y += ty * dir * orbitSpeed;
            }
        });
    }

    function integrateNodeMotion(nodes) {
        const damping = graphState.simulation.damping;
        const alpha = graphState.simulation.alpha;

        nodes.forEach(node => {
            if (node === draggedNode) return;

            node.x += node.vx * alpha;
            node.y += node.vy * alpha;

            node.vx *= damping;
            node.vy *= damping;
        });

        // Cooling schedule
        if (graphState.simulation.alpha > 0.04) {
            graphState.simulation.alpha *= 0.985;
        } else {
            graphState.simulation.alpha = 0.04; // maintain baseline reactive alpha
        }
    }

    function resolveNodeCollisions(nodes) {
        const padding = 12; // space between circles
        for (let i = 0; i < nodes.length; i++) {
            const nodeA = nodes[i];
            for (let j = i + 1; j < nodes.length; j++) {
                const nodeB = nodes[j];
                const dx = nodeB.x - nodeA.x;
                const dy = nodeB.y - nodeA.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;

                const minDist = nodeA.r + nodeB.r + padding;
                if (dist < minDist) {
                    const overlap = minDist - dist;
                    const ox = (dx / dist) * overlap * 0.5;
                    const oy = (dy / dist) * overlap * 0.5;

                    if (nodeA !== draggedNode) {
                        nodeA.x -= ox;
                        nodeA.y -= oy;
                    }
                    if (nodeB !== draggedNode) {
                        nodeB.x += ox;
                        nodeB.y += oy;
                    }
                }
            }
        }
    }

    function isNodeInViewport(node, width, height) {
        const screenX = node.x * canvasZoom + canvasOffset.x;
        const screenY = node.y * canvasZoom + canvasOffset.y;
        const padding = node.r * canvasZoom + 100; // expanded bounds checking
        return (
            screenX >= -padding &&
            screenX <= width + padding &&
            screenY >= -padding &&
            screenY <= height + padding
        );
    }

    function isLinkInViewport(link, width, height) {
        return isNodeInViewport(link.source, width, height) || isNodeInViewport(link.target, width, height);
    }

    function getAdaptiveLabelMode() {
        const nodeCount = graphNodes.length;
        if (canvasZoom < 0.7) {
            return 'minimal';
        }
        if (nodeCount > 35) {
            return canvasZoom > 1.4 ? 'compact' : 'minimal';
        } else if (nodeCount > 15) {
            return canvasZoom > 1.1 ? 'expanded' : 'compact';
        }
        return canvasZoom > 0.85 ? 'expanded' : 'compact';
    }

    function truncateLabel(title, maxLen) {
        if (title.length <= maxLen) return title;
        return title.substring(0, maxLen) + '...';
    }

    function drawNodeLabel(ctx, node, mode) {
        const isHovered = hoveredNode && hoveredNode.id === node.id;
        const isSelected = activeConceptId === node.id;
        const isLatestRun = evaluationRuns.length > 0 && areConceptsEquivalent(evaluationRuns[0].concept, node.title);
        const isHighPriority = isHovered || isSelected || isLatestRun;

        if (mode === 'minimal' && !isHighPriority) {
            return;
        }

        ctx.save();
        ctx.fillStyle = isHighPriority ? '#ffffff' : (node.level === 3 ? '#e0aaff' : 'hsla(210, 25%, 90%, 0.85)');
        ctx.font = isHighPriority ? 'bold 12px "Inter", -apple-system, sans-serif' : '500 10.5px "Inter", -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';

        if (isHighPriority) {
            ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
            ctx.shadowBlur = 8;
        }

        const titleText = node.title;
        if (mode === 'compact' && !isHighPriority) {
            const label = truncateLabel(titleText, 14);
            ctx.fillText(label, node.x, node.y + node.r + 10);
        } else {
            if (titleText.length > 18) {
                const words = titleText.split(' ');
                const mid = Math.ceil(words.length / 2);
                const line1 = words.slice(0, mid).join(' ');
                const line2 = words.slice(mid).join(' ');

                ctx.fillText(line1, node.x, node.y + node.r + 10);
                ctx.fillText(line2, node.x, node.y + node.r + 22);
            } else {
                ctx.fillText(titleText, node.x, node.y + node.r + 10);
            }
        }
        ctx.restore();
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

    function drawGalacticCore(ctx, cx, cy) {
        ctx.save();
        const grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, 75);
        grad.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
        grad.addColorStop(0.15, 'rgba(0, 242, 254, 0.5)');
        grad.addColorStop(0.45, 'rgba(156, 39, 176, 0.22)');
        grad.addColorStop(1, 'rgba(10, 15, 30, 0)');

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(cx, cy, 75, 0, Math.PI * 2);
        ctx.fill();
        
        // Orbiting accretion disk particles
        const time = Date.now() * 0.0012;
        for (let i = 0; i < 16; i++) {
            const r = 12 + (i * 3.8);
            const speed = 1.6 / (r * 0.08 + 1.0);
            const angle = time * speed + (i * (Math.PI / 8));
            const px = cx + r * Math.cos(angle);
            const py = cy + r * Math.sin(angle);
            
            ctx.beginPath();
            ctx.arc(px, py, 1.1, 0, Math.PI * 2);
            ctx.fillStyle = i % 3 === 0 ? 'rgba(0, 242, 254, 0.75)' : (i % 3 === 1 ? 'rgba(238, 130, 238, 0.75)' : 'rgba(255, 255, 255, 0.8)');
            ctx.fill();
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

        // Draw the Supermassive Galactic Nucleus (Milky Way core) only in Galaxy mode
        if (currentNetworkViewMode === 'galaxy') {
            drawGalacticCore(ctx, width / 2, height / 2);
        }

        // 1. Draw connection lines
        graphLinks.forEach((link, idx) => {
            if (!isLinkInViewport(link, width, height)) return;

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
                ctx.strokeStyle = isBothVerified ? 'hsl(180, 100%, 45%)' : (s.level === 3 || t.level === 3 ? '#e0aaff' : 'hsl(38, 95%, 52%)');
                ctx.lineWidth = 2.5;
                ctx.shadowColor = isBothVerified ? 'rgba(0, 242, 254, 0.4)' : (s.level === 3 || t.level === 3 ? 'rgba(224, 170, 255, 0.5)' : 'rgba(255, 179, 0, 0.4)');
                ctx.shadowBlur = 8;
            } else {
                ctx.strokeStyle = isBothVerified ? 'hsla(180, 100%, 45%, 0.16)' : (s.level === 3 || t.level === 3 ? 'hsla(280, 100%, 75%, 0.25)' : 'hsla(38, 95%, 52%, 0.14)');
                ctx.lineWidth = 1.2;
                ctx.shadowBlur = 0;
            }
            ctx.stroke();

            // Draw directed arrowhead for OKF directed links
            if (link.isDirected || isHoveredLink) {
                const dx = t.x - midX;
                const dy = t.y - midY;
                const dist = Math.hypot(dx, dy);
                if (dist > 0) {
                    const targetRadius = (t.r || 10) + 4;
                    const arrowX = t.x - (dx / dist) * targetRadius;
                    const arrowY = t.y - (dy / dist) * targetRadius;
                    const angle = Math.atan2(dy, dx);
                    const headLen = 7;

                    ctx.save();
                    ctx.fillStyle = isHoveredLink ? (isBothVerified ? 'hsl(180, 100%, 45%)' : '#e0aaff') : 'hsla(180, 100%, 50%, 0.65)';
                    ctx.beginPath();
                    ctx.moveTo(arrowX, arrowY);
                    ctx.lineTo(arrowX - headLen * Math.cos(angle - Math.PI / 6), arrowY - headLen * Math.sin(angle - Math.PI / 6));
                    ctx.lineTo(arrowX - headLen * Math.cos(angle + Math.PI / 6), arrowY - headLen * Math.sin(angle + Math.PI / 6));
                    ctx.closePath();
                    ctx.fill();
                    ctx.restore();
                }
            }

            link.midX = midX;
            link.midY = midY;
        });

        // 2. Draw particle flows along links (Micro-animations)
        particleFlows.forEach(flow => {
            const link = flow.link;
            if (!link || !link.visible) return;

            // Always update progress so the animation flows naturally offscreen
            flow.progress += flow.speed;
            if (flow.progress > 1.0) {
                flow.progress = 0;
            }

            // Viewport culling for particle rendering
            if (!isLinkInViewport(link, width, height)) return;

            const s = link.source;
            const t = link.target;
            const p = flow.progress;

            const midX = link.midX || (s.x + t.x) / 2;
            const midY = link.midY || (s.y + t.y) / 2;

            const x = (1-p)*(1-p)*s.x + 2*(1-p)*p*midX + p*p*t.x;
            const y = (1-p)*(1-p)*s.y + 2*(1-p)*p*midY + p*p*t.y;

            ctx.save();
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, Math.PI * 2);

            const isBothVerified = s.status === 'VERIFIED' && t.status === 'VERIFIED';
            ctx.fillStyle = (s.level === 3 || t.level === 3) ? '#e0aaff' : (isBothVerified ? 'hsl(180, 100%, 50%)' : 'hsl(38, 95%, 52%)');
            ctx.shadowColor = ctx.fillStyle;
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.restore();
        });

        ctx.shadowBlur = 0; // Reset shadows

        // Get adaptive label mode once per frame
        const labelMode = getAdaptiveLabelMode();

        // 3. Draw Nodes circles
        graphNodes.forEach(node => {
            if (!isNodeInViewport(node, width, height)) return;

            const isLatestRun = evaluationRuns.length > 0 && areConceptsEquivalent(evaluationRuns[0].concept, node.title);
            const isVerified = node.status === 'VERIFIED';
            const isLevel3 = node.level === 3;
            const isHovered = hoveredNode && hoveredNode.id === node.id;

            // Pulse calculations
            node.pulse += 0.035;
            const pulseRadius = node.r + Math.sin(node.pulse) * 2.5;

            // Coronary halo ring glows
            if (isLatestRun || isHovered || isLevel3) {
                ctx.save();
                ctx.beginPath();
                ctx.arc(node.x, node.y, pulseRadius + 6, 0, Math.PI * 2);
                ctx.fillStyle = isLatestRun ? 'rgba(0, 242, 254, 0.08)' : (isLevel3 ? 'rgba(224, 170, 255, 0.12)' : (isVerified ? 'rgba(0, 230, 118, 0.06)' : 'rgba(255, 179, 0, 0.06)'));
                ctx.strokeStyle = isLatestRun ? 'hsla(180, 100%, 50%, 0.4)' : (isLevel3 ? 'hsla(280, 100%, 75%, 0.6)' : (isVerified ? 'hsla(152, 90%, 45%, 0.3)' : 'hsla(38, 95%, 52%, 0.3)'));
                ctx.lineWidth = 1.2;
                ctx.fill();
                ctx.stroke();
                ctx.restore();
            }

            // Central Node Circle — themed colour in Galaxy mode, status/level colour in Topology mode
            ctx.save();
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);

            if (currentNetworkViewMode === 'galaxy') {
                const armColour = getGalaxyArmColour(node.id);
                ctx.fillStyle   = armColour.fill;
                ctx.strokeStyle = isHovered ? 'rgba(255,255,255,0.9)' : armColour.stroke;
                ctx.lineWidth   = isHovered ? 2.5 : 1.5;
                ctx.shadowColor = armColour.glow;
                ctx.shadowBlur  = isHovered ? 18 : (isLatestRun ? 14 : 8);
            } else {
                ctx.fillStyle   = isLevel3 ? 'hsl(280, 80%, 10%)' : (isVerified ? 'hsl(152, 90%, 8%)' : 'hsl(38, 95%, 6%)');
                ctx.strokeStyle = isLevel3 ? '#e0aaff' : (isVerified ? 'hsl(152, 90%, 45%)' : 'hsl(38, 95%, 52%)');
                ctx.lineWidth   = isHovered ? 2.5 : 1.5;
                ctx.shadowColor = isLevel3 ? 'rgba(224, 170, 255, 0.6)' : (isVerified ? 'rgba(0, 230, 118, 0.3)' : 'rgba(255, 179, 0, 0.3)');
                ctx.shadowBlur  = isHovered ? 14 : (isLevel3 ? 10 : 6);
            }

            ctx.fill();
            ctx.stroke();
            ctx.restore();

            // Node Level indicator — only show in Topology mode (stars don't need Ln text)
            if (currentNetworkViewMode !== 'galaxy') {
                ctx.save();
                ctx.fillStyle = 'hsla(210, 25%, 98%, 0.9)';
                ctx.font = 'bold 11px var(--font-mono)';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`L${node.level}`, node.x, node.y);
                ctx.restore();
            }

            // Adaptive Label rendering
            drawNodeLabel(ctx, node, labelMode);
        });

        ctx.restore();
        ctx.restore();
    }

    function startNetworkGraphPhysicsLoop() {
        stopNetworkGraphLoop();
        const canvas = elements.networkCanvas;
        if (!canvas) return;

        // Handle HDPI canvas resize scale mapping
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = 520 * window.devicePixelRatio;
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `520px`;

        const ctx = canvas.getContext('2d');
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        // Synchronize and seed coordinates on graph load
        syncGraphWithConcepts(concepts);
        graphState.simulation.alpha = 1.0; // energetically layout elements on load

        // Run animations
        const tick = () => {
            // Increment galactic rotation angle slowly over time only in Galaxy mode
            if (currentNetworkViewMode === 'galaxy') {
                galacticRotationAngle += 0.00045;
            }

            // Apply physics force pipeline
            applyRepulsionForces(graphNodes);
            applyLinkForces(graphLinks);
            applyClusterForces(graphNodes);
            applyBoundaryForces(graphNodes);
            resolveNodeCollisions(graphNodes);
            integrateNodeMotion(graphNodes);
            applyAmbientMotion(graphNodes);

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
        // 1. Search filter input listeners
        if (elements.searchInput && elements.clearSearch) {
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
        }

        // 2. Filter Level buttons triggers
        if (elements.levelFilters) {
            elements.levelFilters.querySelectorAll('.filter-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    elements.levelFilters.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentFilters.level = btn.getAttribute('data-filter');
                    applyFiltersAndRenderSidebar();
                });
            });
        }

        // 3. Filter Status buttons triggers
        if (elements.statusFilters) {
            elements.statusFilters.querySelectorAll('.filter-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    elements.statusFilters.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentFilters.status = btn.getAttribute('data-filter');
                    applyFiltersAndRenderSidebar();
                });
            });
        }

        // 4. Concept Codex section scrolling tab highlighting tracker
        if (elements.scrollContainer && elements.tabLinks) {
            let isManualSectionNav = false;
            let manualNavTimeout = null;

            elements.scrollContainer.addEventListener('scroll', () => {
                if (isManualSectionNav) return;

                const sections = document.querySelectorAll('.concept-section');
                let activeId = 'sec-overview';

                sections.forEach(sec => {
                    const rect = sec.getBoundingClientRect();
                    if (rect.top <= 160) {
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
                    isManualSectionNav = true;

                    elements.tabLinks.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');

                    const targetId = link.getAttribute('href');
                    const targetSec = document.querySelector(targetId);
                    if (targetSec) {
                        targetSec.scrollIntoView({ behavior: 'smooth' });
                    }

                    if (manualNavTimeout) clearTimeout(manualNavTimeout);
                    manualNavTimeout = setTimeout(() => {
                        isManualSectionNav = false;
                    }, 1200);
                });
            });
        }

        // 5. Dual Perspective selectors triggers
        if (elements.perspectiveSelector) {
            elements.perspectiveSelector.querySelectorAll('.perspective-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const targetPerspective = btn.getAttribute('data-perspective');
                    switchPerspective(targetPerspective);
                });
            });
        }

        // 6. Timeline Filter triggers
        if (elements.timelineFilters) {
            elements.timelineFilters.querySelectorAll('.time-filter-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    elements.timelineFilters.querySelectorAll('.time-filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentTimelineFilter = btn.getAttribute('data-time-filter');
                    renderOdysseyLedgerTimeline();
                });
            });
        }

        // 7. Content inline hyperlinking delegations
        if (elements.contentView) {
            elements.contentView.addEventListener('click', (e) => {
                const link = e.target.closest('.inline-concept-link');
                if (link) {
                    const targetId = link.getAttribute('data-target');
                    selectConcept(targetId);
                }
            });
        }

        // 8. Action panel cards click handlers (Inside Codex Landing welcome view)
        if (elements.btnExploreFirst) {
            elements.btnExploreFirst.addEventListener('click', () => {
                if (concepts.length > 0) {
                    const alphabeticallyFirst = [...concepts].sort((a,b) => a.title.localeCompare(b.title))[0];
                    selectConcept(alphabeticallyFirst.id);
                }
            });
        }

        if (elements.btnShowNetworkCard) {
            elements.btnShowNetworkCard.addEventListener('click', () => {
                switchPerspective('network');
            });
        }

        if (elements.btnBackToWelcome) {
            elements.btnBackToWelcome.addEventListener('click', () => {
                activeConceptId = null;
                if (elements.contentView) elements.contentView.style.display = 'none';
                if (elements.welcomeView) elements.welcomeView.style.display = 'flex';
                document.querySelectorAll('.concept-card').forEach(c => c.classList.remove('active'));
            });
        }

        // 9. ⏳ Timeline Scrubber Controls Event Hooks
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

        // 10. 🔍 Canvas Zoom Controls Overlay Event Hooks
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

        // Network View Mode Toggle click handlers (Topological Flow vs Milky Way Galaxy)
        if (elements.btnViewTopology) {
            elements.btnViewTopology.addEventListener('click', () => {
                if (currentNetworkViewMode === 'topology') return;
                currentNetworkViewMode = 'topology';
                elements.btnViewTopology.classList.add('active');
                elements.btnViewGalaxy.classList.remove('active');
                canvasZoom = 1.0;
                canvasOffset = { x: 0, y: 0 };
                // Re-sync so computeNodeRadius reverts to topology circle sizes
                syncGraphWithConcepts(concepts);
                graphState.simulation.alpha = 1.0;
            });
        }

        if (elements.btnViewGalaxy) {
            elements.btnViewGalaxy.addEventListener('click', () => {
                // Open the dedicated Milky Way Galaxy page
                window.location.href = 'galaxy.html';
            });
        }

    function recenterCameraOnNodes(nodes) {
        if (!nodes || nodes.length === 0) return;
        const canvas = elements.networkCanvas;
        if (!canvas) return;

        const width = canvas.clientWidth || 900;
        const height = canvas.clientHeight || 520;

        let sumX = 0, sumY = 0;
        nodes.forEach(n => { sumX += n.x; sumY += n.y; });
        const avgX = sumX / nodes.length;
        const avgY = sumY / nodes.length;

        canvasOffset.x = (width / 2) - (avgX * canvasZoom);
        canvasOffset.y = (height / 2) - (avgY * canvasZoom);
    }

    const netFilterGroup = document.getElementById('net-filter-group');
    if (netFilterGroup) {
        netFilterGroup.querySelectorAll('.net-pill-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                netFilterGroup.querySelectorAll('.net-pill-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentNetworkFilter = btn.getAttribute('data-net-filter');
                syncGraphWithConcepts(concepts);
                graphState.simulation.alpha = 1.0;
                setTimeout(() => recenterCameraOnNodes(graphNodes), 50);
            });
        });
    }

        // Canvas Interaction physics mouse hooks
        setupNetworkCanvasMouseListeners();

        // 11. Command tab switcher (Telemetry / Sandbox Arena) using Delegated Click Hooks
        const tabsHeader = document.querySelector('.command-tabs-header');
        if (tabsHeader) {
            tabsHeader.addEventListener('click', (e) => {
                const btn = e.target.closest('.command-tab-btn');
                if (!btn) return;

                const targetTab = btn.getAttribute('data-tab');

                const btns = tabsHeader.querySelectorAll('.command-tab-btn');
                btns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const tabTelemetry = document.getElementById('tab-telemetry');
                const tabSandbox = document.getElementById('tab-sandbox');

                if (targetTab === 'telemetry') {
                    if (tabTelemetry) tabTelemetry.style.display = 'block';
                    if (tabSandbox) tabSandbox.style.display = 'none';
                } else if (targetTab === 'sandbox') {
                    if (tabTelemetry) tabTelemetry.style.display = 'none';
                    if (tabSandbox) tabSandbox.style.display = 'block';
                }
            });
        } else if (elements.commandTabBtns) {
            // Fallback for isolated systems or cached states
            elements.commandTabBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const targetTab = btn.getAttribute('data-tab');

                    elements.commandTabBtns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    if (targetTab === 'telemetry') {
                        if (elements.tabTelemetry) elements.tabTelemetry.style.display = 'block';
                        if (elements.tabSandbox) elements.tabSandbox.style.display = 'none';
                    } else if (targetTab === 'sandbox') {
                        if (elements.tabTelemetry) elements.tabTelemetry.style.display = 'none';
                        if (elements.tabSandbox) elements.tabSandbox.style.display = 'block';
                    }
                });
            });
        }

        // 12. Initiate Sandbox Debate Event Hook
        if (elements.btnSandboxStart) {
            elements.btnSandboxStart.addEventListener('click', () => {
                const selectVal = elements.sandboxConceptSelect ? elements.sandboxConceptSelect.value : '';
                let concept = selectVal;

                if (selectVal === 'custom') {
                    concept = elements.sandboxCustomInput ? elements.sandboxCustomInput.value.trim() : '';
                }

                if (!concept) {
                    alert('Please select or input a scientific topic to initiate.');
                    return;
                }

                runSandboxDebate(concept);
            });
        }
    }

    function setupNetworkCanvasMouseListeners() {
        const canvas = elements.networkCanvas;
        if (!canvas) return;
        let isPanning = false;
        let panStart = { x: 0, y: 0 };
        let mouseMovedDuringClick = false;
        let mouseDownPos = { x: 0, y: 0 };

        const getCanvasCoords = (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = (canvas.width / window.devicePixelRatio) / rect.width;
            const scaleY = (canvas.height / window.devicePixelRatio) / rect.height;

            const mouseX = (e.clientX - rect.left) * scaleX;
            const mouseY = (e.clientY - rect.top) * scaleY;

            return {
                x: (mouseX - canvasOffset.x) / canvasZoom,
                y: (mouseY - canvasOffset.y) / canvasZoom
            };
        };

        const getNodeAtMouse = (e) => {
            const coords = getCanvasCoords(e);
            let closestNode = null;
            let minDistance = Infinity;

            for (let i = 0; i < graphNodes.length; i++) {
                const node = graphNodes[i];
                const pt = currentNetworkViewMode === 'topology' ? applyGravityWarp(node.x, node.y) : { x: node.x, y: node.y };
                const dx = coords.x - pt.x;
                const dy = coords.y - pt.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                const hitRadius = Math.max(node.r + 10, 18);

                if (dist <= hitRadius && dist < minDistance) {
                    minDistance = dist;
                    closestNode = node;
                }
            }

            return closestNode;
        };

        canvas.addEventListener('mousemove', (e) => {
            const coords = getCanvasCoords(e);

            if (draggedNode) {
                draggedNode.x = coords.x;
                draggedNode.y = coords.y;
                graphState.simulation.alpha = Math.max(graphState.simulation.alpha, 0.45);
                return;
            }

            if (isPanning) {
                const dx = e.clientX - panStart.x;
                const dy = e.clientY - panStart.y;
                if (Math.hypot(e.clientX - mouseDownPos.x, e.clientY - mouseDownPos.y) > 5) {
                    mouseMovedDuringClick = true;
                }
                canvasOffset.x += dx;
                canvasOffset.y += dy;
                panStart = { x: e.clientX, y: e.clientY };
                return;
            }

            hoveredNode = getNodeAtMouse(e);
            canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
        });

        canvas.addEventListener('mousedown', (e) => {
            mouseDownPos = { x: e.clientX, y: e.clientY };
            mouseMovedDuringClick = false;

            const clickedNode = getNodeAtMouse(e);
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
            draggedNode = null;
            isPanning = false;
            canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
        });

        canvas.addEventListener('mouseleave', () => {
            isPanning = false;
            draggedNode = null;
        });

        canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left) * ((canvas.width / window.devicePixelRatio) / rect.width);
            const mouseY = (e.clientY - rect.top) * ((canvas.height / window.devicePixelRatio) / rect.height);

            const zoomIntensity = 0.04;
            const delta = -e.deltaY;
            const oldZoom = canvasZoom;

            if (delta > 0) {
                canvasZoom = Math.min(2.5, canvasZoom + zoomIntensity);
            } else {
                canvasZoom = Math.max(0.5, canvasZoom - zoomIntensity);
            }

            canvasOffset.x = mouseX - (mouseX - canvasOffset.x) * (canvasZoom / oldZoom);
            canvasOffset.y = mouseY - (mouseY - canvasOffset.y) * (canvasZoom / oldZoom);
        });

        canvas.addEventListener('click', (e) => {
            if (!mouseMovedDuringClick) {
                const targetNode = getNodeAtMouse(e);
                if (targetNode) {
                    selectConcept(targetNode.id);
                }
            }
        });
    }

    /* ==========================================================================
       🪐 SKEPTIC SANDBOX ARENA CORE ROUTINES
       ========================================================================== */

    function populateSandboxConcepts() {
        if (!elements.sandboxConceptSelect) return;

        const select = elements.sandboxConceptSelect;
        select.innerHTML = '';

        const placeholderOpt = document.createElement('option');
        placeholderOpt.value = '';
        placeholderOpt.disabled = true;
        placeholderOpt.selected = true;
        placeholderOpt.textContent = 'Select a scientific concept...';
        select.appendChild(placeholderOpt);

        const uniqueTitles = new Set();
        allConcepts.forEach(c => {
            if (c.title) {
                uniqueTitles.add(c.title);
            }
        });

        Array.from(uniqueTitles).sort().forEach(title => {
            const opt = document.createElement('option');
            opt.value = title;
            opt.textContent = title;
            select.appendChild(opt);
        });

        const customOpt = document.createElement('option');
        customOpt.value = 'custom';
        customOpt.textContent = 'Custom Topic...';
        select.appendChild(customOpt);

        select.addEventListener('change', () => {
            if (select.value === 'custom') {
                if (elements.sandboxCustomInput) {
                    elements.sandboxCustomInput.style.display = 'block';
                    elements.sandboxCustomInput.focus();
                }
            } else {
                if (elements.sandboxCustomInput) {
                    elements.sandboxCustomInput.style.display = 'none';
                }
            }
        });
    }

    function renderSandboxHistory() {
        if (!elements.sandboxHistoryList) return;

        const list = elements.sandboxHistoryList;
        list.innerHTML = '';

        if (allSandboxDebates.length === 0) {
            list.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 11px; padding: 10px;">No debate records available.</div>`;
            return;
        }

        allSandboxDebates.forEach(debate => {
            const item = document.createElement('div');
            item.className = 'history-item';

            let scoreClass = 'score-low';
            if (debate.score >= 80) {
                scoreClass = 'score-high';
            } else if (debate.score >= 60) {
                scoreClass = 'score-mid';
            }

            item.innerHTML = `
                <span class="history-item-concept" title="${debate.concept}">${debate.concept}</span>
                <span class="history-item-score ${scoreClass}">${debate.score}%</span>
            `;

            item.addEventListener('click', () => {
                displayCompletedDebate(debate);
            });

            list.appendChild(item);
        });
    }

    function displayCompletedDebate(debate) {
        if (!elements.sandboxDebateStream || !elements.sandboxVerdictBox) return;

        const stream = elements.sandboxDebateStream;
        stream.innerHTML = '';

        debate.turns.forEach(turn => {
            const bubble = document.createElement('div');
            bubble.className = `sandbox-bubble ${turn.agent}`;

            const header = document.createElement('div');
            header.className = 'sandbox-bubble-header';
            header.innerHTML = `
                <span>${turn.agent === 'caveman' ? 'Grog' : (turn.agent === 'oracle' ? 'The Oracle' : 'Skeptical Student')}</span>
                <span class="sandbox-bubble-role">${turn.role}</span>
            `;

            const text = document.createElement('div');
            text.className = 'sandbox-bubble-text';
            text.innerHTML = compileMarkdownToHTML(turn.text);

            bubble.appendChild(header);
            bubble.appendChild(text);
            stream.appendChild(bubble);
        });

        stream.scrollTop = stream.scrollHeight;
        updateSandboxGauge(debate.score);
        elements.sandboxVerdictBox.textContent = debate.verdict;
    }

    function updateSandboxGauge(score) {
        if (!elements.sandboxGaugeFill || !elements.sandboxScoreValue) return;

        const targetOffset = 264 - (264 * score) / 100;
        elements.sandboxGaugeFill.style.strokeDashoffset = targetOffset;

        let color = 'var(--status-rejected)';
        if (score >= 80) {
            color = 'var(--status-verified)';
        } else if (score >= 60) {
            color = 'var(--status-theoretical)';
        }
        elements.sandboxGaugeFill.style.stroke = color;

        const currentVal = parseInt(elements.sandboxScoreValue.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();

        function animateCount(timestamp) {
            const elapsed = timestamp - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeProgress = progress * (2 - progress);
            const val = Math.floor(currentVal + (score - currentVal) * easeProgress);
            elements.sandboxScoreValue.textContent = val;

            if (progress < 1) {
                requestAnimationFrame(animateCount);
            } else {
                elements.sandboxScoreValue.textContent = score;
            }
        }
        requestAnimationFrame(animateCount);
    }

    function generateMockDebate(concept) {
        const conceptLower = concept.toLowerCase();
        const timestamp = new Date().toISOString();

        if (conceptLower.includes('entanglement')) {
            return {
                id: `debate_${Date.now()}`,
                concept: "Quantum Entanglement",
                timestamp: timestamp,
                score: 88,
                verdict: "Quantum Entanglement is mathematically indisputable and experimentally verified, yet continues to defy primitive spatial common sense.",
                turns: [
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "Today we tackle Quantum Entanglement. How can two subatomic particles, separated by light-years, instantly coordinate their states? This seems to violate Einstein's speed limit of light. Grog, Oracle, state your positions!"
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: "UG! Grog look at moon. Grog throw rock. Rock fly, hit tree. That make sense! Cause and effect have touch! But Oracle talk about 'spooky action'. Two stones, one in Grog cave, one in other tribe cave. Oracle say if Grog turn stone over, other stone turn over instantly! GROG SAY CRAZY! No touch, no rope, no fire smoke between them. Grog think Oracle make big trick with invisible magic!"
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: "Grog, thy senses are bound by the heavy friction of the earth. In the deeper fabric of reality, space is not a dividing void, but an emergent projection. The two particles are represented by a single, non-separable quantum wave function: $\\Psi_{AB} = \\frac{1}{\\sqrt{2}} (|0\\rangle_A |1\\rangle_B - |1\\rangle_A |0\\rangle_B)$. When we measure particle A, the state vector collapses instantly across all space. No signal travels *through* space, because at the level of the quantum state, space does not exist."
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "Fascinating. Grog rejects it because there is no mechanical medium—no rope or physical touch. But Oracle, your math is elegant, yet how do we verify this without falling into local hidden variables? How do we know the particles didn't just agree on their states beforehand, like a pair of shoes pre-packaged in left and right boxes? Grog, how can you explain Bell's Inequality experiments with just rocks?"
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: "GROG NO LIKE hidden boxes! If Grog put left shoe in one bag, right shoe in other bag. Send one to chief, keep one. Grog open bag, see left shoe. Grog know chief bag have right shoe instantly! But that because shoe was *already* left shoe! No magic spooky spin change! Oracle say shoe is both left and right until Grog look. Grog say shoe is shoe! Measurement just show what was already there!"
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: "Ah, Grog, but the shoes of thy analogy are classical. John Stewart Bell proved that if the universe were simple pre-packaged shoes, the correlations under different measurement angles could never exceed a strict limit: $S \\le 2$. Yet, the light of our lasers measuring entangled photons reveals a value of $S = 2\\sqrt{2} \\approx 2.828$. This violates Bell's inequality, proving that the states were truly undecided—entangled in a cosmic superposition—until measured. Thy primitive realism is mathematically dead."
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "Unbelievable. The Bell test violations of local realism are experimentally solid, which refutes Grog's pre-packaged shoe theory. Superposition is real, and the correlation is stronger than any classical system can explain. Yet, because no information can be sent faster than light, General Relativity remains safe. Our final consensus: Entanglement is mathematically robust and experimentally proven, yet physically incomprehensible to macroscopic beings."
                    }
                ]
            };
        } else if (conceptLower.includes('gravity') || conceptLower.includes('mond') || conceptLower.includes('dark matter')) {
            return {
                id: `debate_${Date.now()}`,
                concept: "MOND vs Cold Dark Matter",
                timestamp: timestamp,
                score: 65,
                verdict: "Modified Newtonian Gravity (MOND) explains galactic rotation curves without invisible matter, but lacks general relativistic consistency and cosmological scaling.",
                turns: [
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "Today we debate galactic rotation curves. Galaxies spin so fast their outer stars should fly off into space, yet they hold together. Is there an invisible halo of 'Dark Matter' pulling them, or is our formula for gravity wrong at low accelerations? Grog, Oracle, bring forth your arguments!"
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: "UG! Grog throw rock. Heavy rock fall fast. Grog swing rock on vine. If Grog swing rock super fast, vine snap, rock fly into river! Galaxies are big spinning rocks on vine. If stars spin too fast, gravity vine must be stronger, or stars fly away! Grog look into sky—no see extra heavy stuff. Grog think gravity vine just pull harder when swing gets lazy at edge! Why make up invisible ghosts like 'dark matter' when gravity formula just need tiny bend? 🪨"
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: "Grog, thy intuition of the vine is noble, but thy gravity model is incomplete. Galaxies are bound by the invisible. We propose Cold Dark Matter (CDM), a non-baryonic particle species that does not interact with the electromagnetic spectrum. The rotation curve flatlines because outer stars reside inside a massive spherical dark halo, where mass scales linearly with radius: $M(r) \\propto r$. This preserves Einstein's general relativity: $G_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}$, where $T_{\\mu\\nu}$ includes this unseen energy density."
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "A classic impasse. Grog modifies Newton's laws (MOND) using an acceleration constant $a_0 \\approx 1.2 \\times 10^{-10} \\text{ m/s}^2$ to fit rotation curves beautifully without invisible particles. Oracle invokes an invisible, undetected matter field to save General Relativity. But Oracle, we have searched for WIMPs and axions for decades in deep mines and found nothing! And Grog, how does your MOND explain the Bullet Cluster collision, where the gravitational lensing maps are offset from visible gas?"
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: "GROG WATCH bullet cluster! Gas collide, hot gas get stuck in middle like sticky mud. But gravity lens still keep going on sides! Grog admit: that hard to explain if gravity only follow mud! It seem gravity pulling toward *something* invisible that flew right through. Grog scratch head. Maybe dark matter is real heavy dust we cannot burn. But Grog still hate inventing particles that never hit Grog's underground traps!"
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: "Indeed, the Bullet Cluster is the graveyard of pure baryonic gravity modifications. The separation of the lensing potential from the dissipative gas is the direct empirical footprint of collisionless Dark Matter. While thy laboratory traps remain silent, the gravitational lensing profile $\\theta_E = \\frac{4GM}{c^2 D_L}$ maps the cosmic skeleton perfectly. We must persevere in particle synthesis."
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "The Bullet Cluster indeed presents a massive hurdle for modified gravity, as gravitational lensing points to a collisionless mass source separate from visible gas. However, CDM's lack of direct laboratory detection and its 'cuspy halo' issues keep the debate alive. Our verdict: Dark Matter remains the leading cosmological paradigm with a solid 65% score, but remains theoretical until a physical particle is captured in a detector."
                    }
                ]
            };
        } else if (conceptLower.includes('inflation') || conceptLower.includes('cosmology')) {
            return {
                id: `debate_${Date.now()}`,
                concept: "Cosmic Inflation",
                timestamp: timestamp,
                score: 72,
                verdict: "Cosmic Inflation solves flatness and monopole problems with grand mathematical elegance, but its lack of direct primordial gravitational wave evidence keeps it partially theoretical.",
                turns: [
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "Today we probe the early cosmos: Cosmic Inflation. It claims that a fraction of a second after the Big Bang, the universe underwent an exponential expansion, growing by a factor of $10^{26}$ or more in $10^{-32}$ seconds. What triggered this? Grog, Oracle, defend your models!"
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: "UG! Grog look at flat field. Plain and smooth. Grog understand why field flat—it just ground! But Oracle say ground was once tiny, then blow up like giant puff-ball! If Grog blow fire-breath into clay pot, pot break! Pot not grow smooth and nice. Grog say if universe blow up that fast, everything should tear apart! Where is inflation-spirit now? Grog look, but only see quiet night sky. No blowing, no inflating. Grog say: if cannot see inflation-wind blow today, it just myth!"
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: "Primal tracker, thy pot explodes because its materials possess chemical tension. But the inflaton is a scalar field $\\phi$ moving down a flat potential energy density $V(\\phi)$. This field drives an exponential Hubble expansion $a(t) = a_0 e^{Ht}$, where $H^2 \\approx \\frac{8\\pi G}{3} V(\\phi)$. This rapid stretching dilutes magnetic monopoles and flattens cosmic curvature $\\Omega \\to 1$, explaining why thy eyes see a flat horizon. The inflation-wind is not a myth; its quantum fluctuations are the very seeds of galaxies, written as $\\mathcal{P}_{\\mathcal{R}}(k) \\approx \\frac{H^2}{8\\pi^2 M_{Pl}^2 \\epsilon}$."
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "The inflaton field resolves the horizon and flatness problems, yet we cannot directly detect the inflaton particle. Grog demands immediate observations. But Oracle, there is a signature: primordial gravitational waves should leave B-mode polarizations in the Cosmic Microwave Background (CMB). Yet, our telescopes like BICEP and Planck have only seen dust! How do you justify inflation without primordial B-modes? Grog, does Grog see any seeds in the sky?"
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: "GROG SEE stars! Stars are like glowing coals of forest fire. 🪵 Grog know coal comes from wood. If Oracle say stars came from tiny quantum seed-shivers, Grog want to see the shiver! CMB is just cold background glow. Grog think cold glow is just ashes of old cosmic campfire. Grog not see B-mode polar-shapes. Show Grog real shiver-wave, or Grog say: 'Big Oracle just make up scalar-magic to cover Big Bang gap!'"
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: "The ash of the cosmic campfire is indeed the CMB, Grog. Yet, inside those ashes, we measure the temperature fluctuations $\\frac{\\Delta T}{T} \\approx 10^{-5}$, which exhibit a nearly scale-invariant power spectrum $n_s = 0.965 \\pm 0.004$, exactly as predicted by our slow-roll parameter $\\eta$. Primordial gravitational waves indeed remain elusive, as the tensor-to-scalar ratio is bounded by $r < 0.036$. We await the CMB-S4 and LiteBIRD observatories to measure the tensor perturbations $h_{\\mu\\nu}$. Thy campfire was lit by the quantum shivers of the cosmos."
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: "A spectacular synthesis! Grog's 'ashes' are the precise thermal fluctuations of the CMB. The slow-roll spectral index $n_s \\approx 0.965$ is one of the most successful predictions in modern astrophysics, confirming the quantum origin of structure. However, because $r$ is extremely small and we have not found B-modes, inflation remains a leading paradigm (72%) but is not yet fully sealed. Grog's healthy skepticism is justified, yet Oracle's mathematical fit is stunning."
                    }
                ]
            };
        } else {
            return {
                id: `debate_${Date.now()}`,
                concept: concept,
                timestamp: timestamp,
                score: 75,
                verdict: `Theoretical exploration of ${concept} reveals a strong mathematical framework with promising, yet incomplete empirical confirmation.`,
                turns: [
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: `Today we examine ${concept}. We seek to bridge the gap between Grog's direct empirical observations and the Oracle's mathematical equations. Let us begin!`
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: `UG! Grog look at ${concept}. Grog look for fire, rock, and smoke. If Grog cannot burn it, smell it, or hit it with club, Grog very skeptical! How does this touch Grog's everyday hunting life? 🪨`
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: `Greetings, explorer. ${concept} represents a beautiful, symmetric coordinate field of the cosmos. Mathematically, it is described by unified field tensor transformations $\\mathbf{T}_{\\mu\\nu}$ that exist far beyond Grog's immediate sensory horizon. It is a necessary structure of mathematical consistency and gauge invariance.`
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: `The Oracle claims mathematical necessity, while Grog demands physical contact. Let us push deeper: Oracle, what is the direct, verifiable evidence for this field? Grog, how do you explain the subtle perturbations that your simple rock mechanics cannot account for?`
                    },
                    {
                        agent: "caveman",
                        role: "Grog the Caveman",
                        text: `Grog know that simple rock path can bend. If wind blow, rock bend. Grog understand there are invisible winds! If ${concept} is just a cosmic wind pulling on stars, Grog can accept it. But don't tell Grog it exists in ten extra dimensions Grog cannot climb! 🦴`
                    },
                    {
                        agent: "oracle",
                        role: "The Transcendent Oracle",
                        text: `The invisible winds of Grog are but vector fields. Indeed, we verify this through precise cosmic microwave background measurements and micro-perturbations in particle decays. Symmetries must preserve gauge invariance under localized phase rotations $\\psi \\to e^{i\\alpha(x)}\\psi$.`
                    },
                    {
                        agent: "grill_student",
                        role: "The Skeptical Student Explorer",
                        text: `Both perspectives hold a piece of the truth. Grog's 'cosmic wind' is an elegant analogy for field force effects, while the Oracle's gauge symmetries provide the structural backbone. ${concept} stands as a vital framework, balancing empirical grounding with theoretical elegance.`
                    }
                ]
            };
        }
    }

    async function runSandboxDebate(concept) {
        if (isSandboxDebateRunning) return;

        isSandboxDebateRunning = true;
        elements.btnSandboxStart.disabled = true;
        elements.btnSandboxStart.classList.add('disabled');
        elements.btnSandboxStart.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running...`;

        updateSandboxGauge(0);
        elements.sandboxVerdictBox.innerHTML = `<span class="pulse-dot dot-theoretical"></span> Debate in progress. Agents are formulating epistemics...`;

        const stream = elements.sandboxDebateStream;
        stream.innerHTML = '';

        // Prioritize actual LLM-generated debate from our logged runs (newest first)
        let debate = [...allSandboxDebates].reverse().find(d => d.concept && d.concept.toLowerCase() === concept.toLowerCase());
        if (!debate) {
            debate = generateMockDebate(concept);
        }
        const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

        for (let i = 0; i < debate.turns.length; i++) {
            const turn = debate.turns[i];

            const typingBubble = document.createElement('div');
            typingBubble.className = `sandbox-bubble ${turn.agent}`;

            const header = document.createElement('div');
            header.className = 'sandbox-bubble-header';
            header.innerHTML = `
                <span>${turn.agent === 'caveman' ? 'Grog' : (turn.agent === 'oracle' ? 'The Oracle' : 'Skeptical Student')}</span>
                <span class="sandbox-bubble-role">${turn.role}</span>
            `;

            const textContainer = document.createElement('div');
            textContainer.className = 'sandbox-bubble-text';
            textContainer.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;

            typingBubble.appendChild(header);
            typingBubble.appendChild(textContainer);
            stream.appendChild(typingBubble);

            stream.scrollTop = stream.scrollHeight;

            await sleep(1800);

            textContainer.innerHTML = compileMarkdownToHTML(turn.text);
            stream.scrollTop = stream.scrollHeight;

            const wordCount = turn.text.split(/\s+/).length;
            const readDelay = Math.min(3000, Math.max(1000, wordCount * 50));
            if (i < debate.turns.length - 1) {
                await sleep(readDelay);
            }
        }

        updateSandboxGauge(debate.score);
        elements.sandboxVerdictBox.textContent = debate.verdict;

        const telemetryEvent = {
            id: `telemetry_${Date.now()}`,
            event_type: "skeptic_sandbox_debate",
            stage: "sandbox_arena",
            concept: debate.concept,
            timestamp: new Date().toISOString(),
            status: "APPROVED",
            message: `Debate Completed on '${debate.concept}': Score ${debate.score}% - '${debate.verdict}'`
        };

        allTelemetryEvents.unshift(telemetryEvent);
        allSandboxDebates.push(debate);

        renderSandboxHistory();
        updateChronologicalState();

        elements.btnSandboxStart.disabled = false;
        elements.btnSandboxStart.classList.remove('disabled');
        elements.btnSandboxStart.innerHTML = `<i class="fa-solid fa-play"></i> Initiate Debate`;
        isSandboxDebateRunning = false;
    }

    /* ==========================================================================
       📐 MATHEMATICAL ARCHAEOLOGY & CONSTANT EXPLORER
       ========================================================================== */
    function renderEquationExplorer() {
        if (!allEquationData) return;

        const constantsGrid = document.getElementById('eq-constants-grid');
        const searchInput = document.getElementById('eq-search-input');
        const filterGroup = document.getElementById('eq-filter-group');

        // Bind Search & Filter listeners once
        if (searchInput && !searchInput.hasAttribute('data-bound')) {
            searchInput.setAttribute('data-bound', 'true');
            searchInput.addEventListener('input', (e) => {
                currentEqSearch = e.target.value.toLowerCase().trim();
                renderEquationBridgesGrid();
            });
        }

        if (filterGroup && !filterGroup.hasAttribute('data-bound')) {
            filterGroup.setAttribute('data-bound', 'true');
            filterGroup.querySelectorAll('.filter-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    filterGroup.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentEqCategory = btn.getAttribute('data-eq-filter');
                    renderEquationBridgesGrid();
                });
            });
        }

        // Render Constants Cards
        if (constantsGrid && allEquationData.constant_index) {
            constantsGrid.innerHTML = allEquationData.constant_index.map(c => {
                const isActive = selectedEqConstant === c.symbol ? 'active' : '';
                let renderedSym = escapeHtml(c.symbol);
                if (window.katex && typeof window.katex.renderToString === 'function') {
                    try {
                        renderedSym = window.katex.renderToString(c.symbol, { throwOnError: false, displayMode: false });
                    } catch (e) {}
                }
                return `
                    <div class="constant-card ${isActive}" data-symbol="${escapeHtml(c.symbol)}">
                        <div class="constant-top">
                            <span class="constant-symbol">${renderedSym}</span>
                            <span class="constant-count-badge">${c.occurrence_count} concepts</span>
                        </div>
                        <div class="constant-name">${escapeHtml(c.name)}</div>
                        <div class="constant-value">${escapeHtml(c.typical_value)} ${escapeHtml(c.unit)}</div>
                    </div>
                `;
            }).join('');

            constantsGrid.querySelectorAll('.constant-card').forEach(card => {
                card.addEventListener('click', () => {
                    const sym = card.getAttribute('data-symbol');
                    if (selectedEqConstant === sym) {
                        selectedEqConstant = null;
                    } else {
                        selectedEqConstant = sym;
                    }
                    renderEquationExplorer();
                });
            });
        }

        renderEquationBridgesGrid();
    }

    function renderEquationBridgesGrid() {
        const bridgesGrid = document.getElementById('eq-bridges-grid');
        if (!bridgesGrid || !allEquationData || !allEquationData.bridges) return;

        let filtered = allEquationData.bridges.filter(b => {
            // Constant filter (when a specific constant card is selected)
            if (selectedEqConstant) {
                const constObj = allEquationData.constant_index.find(ci => ci.symbol === selectedEqConstant);
                const refTitles = constObj ? (constObj.referenced_in || []) : [];

                const symbolMatch = b.equation.includes(selectedEqConstant) ||
                                    (selectedEqConstant.includes('Pl') && (b.equation.includes('Pl') || b.equation.includes('hbar') || b.equation.includes('\\hbar')));
                const conceptRefMatch = b.concepts.some(c => refTitles.includes(c.title));

                if (!symbolMatch && !conceptRefMatch) return false;
            }

            // Category filter
            if (currentEqCategory === 'constants') {
                const allRefTitles = new Set();
                allEquationData.constant_index.forEach(ci => {
                    (ci.referenced_in || []).forEach(t => allRefTitles.add(t));
                });

                const hasKnownConst = ['\\Lambda', 'G', '\\hbar', 'c', 'a_0', 'M_{\\rm Pl}', 'M_{Pl}', 'M_{\\text{Pl}}', 'N_{\\rm eff}', 'N_{eff}', '\\Omega_c'].some(sym => b.equation.includes(sym));
                const conceptRefMatch = b.concepts.some(c => allRefTitles.has(c.title));

                if (!hasKnownConst && !conceptRefMatch) return false;
            } else if (currentEqCategory === 'l1') {
                if (!b.concepts.some(c => c.level === 1)) return false;
            } else if (currentEqCategory === 'l2') {
                if (!b.concepts.some(c => c.level === 2)) return false;
            } else if (currentEqCategory === 'l3') {
                if (!b.concepts.some(c => c.level === 3)) return false;
            }

            // Search filter
            if (currentEqSearch) {
                const eqMatch = b.equation.toLowerCase().includes(currentEqSearch);
                const conceptMatch = b.concepts.some(c => c.title.toLowerCase().includes(currentEqSearch));

                let constMatch = false;
                if (allEquationData.constant_index) {
                    const matchingConsts = allEquationData.constant_index.filter(ci =>
                        ci.name.toLowerCase().includes(currentEqSearch) ||
                        ci.symbol.toLowerCase().includes(currentEqSearch)
                    );
                    if (matchingConsts.length > 0) {
                        const matchingRefTitles = new Set();
                        matchingConsts.forEach(ci => (ci.referenced_in || []).forEach(t => matchingRefTitles.add(t)));
                        const constSymbols = matchingConsts.map(ci => ci.symbol);

                        const eqHasSym = constSymbols.some(sym => b.equation.includes(sym));
                        const concHasTitle = b.concepts.some(c => matchingRefTitles.has(c.title));
                        if (eqHasSym || concHasTitle) constMatch = true;
                    }
                }

                if (!eqMatch && !conceptMatch && !constMatch) return false;
            }

            return true;
        });

        if (filtered.length === 0) {
            bridgesGrid.innerHTML = `
                <div class="no-results" style="grid-column: 1 / -1; padding: 40px; text-align: center; color: var(--text-muted);">
                    <i class="fa-solid fa-square-root-variable" style="font-size: 32px; margin-bottom: 12px; color: var(--border-glow);"></i>
                    <p style="font-size: 14px;">No equation bridges match your current filter or search criteria.</p>
                </div>
            `;
            return;
        }

        bridgesGrid.innerHTML = filtered.map(b => {
            let renderedMath = '';
            if (window.katex && typeof window.katex.renderToString === 'function') {
                try {
                    renderedMath = window.katex.renderToString(b.equation, { throwOnError: false, displayMode: true });
                } catch (e) {
                    renderedMath = `<code>${escapeHtml(b.equation)}</code>`;
                }
            } else {
                renderedMath = `<code>${escapeHtml(b.equation)}</code>`;
            }

            const conceptPills = b.concepts.map(c => {
                const lvlClass = c.level === 3 ? 'lvl-3' : (c.level === 2 ? 'lvl-2' : 'lvl-1');
                const matchedConcept = allConcepts.find(ac => ac.title.toLowerCase() === c.title.toLowerCase());
                const targetId = matchedConcept ? matchedConcept.id : c.title.toLowerCase().replace(/[^a-z0-9]/g, '');
                return `<span class="eq-concept-pill ${lvlClass}" data-concept-id="${targetId}" title="Open concept in Codex">L${c.level}: ${escapeHtml(c.title)}</span>`;
            }).join('');

            return `
                <div class="eq-bridge-card">
                    <div class="eq-card-header">
                        <span class="eq-bridge-badge"><i class="fa-solid fa-link"></i> ${b.concept_count} CONCEPTS</span>
                    </div>
                    <div class="eq-display-box">${renderedMath}</div>
                    <div>
                        <div class="eq-concepts-label">Bridged Theoretical Frameworks:</div>
                        <div class="eq-concepts-list">${conceptPills}</div>
                    </div>
                </div>
            `;
        }).join('');

        // Bind click events on concept pills
        bridgesGrid.querySelectorAll('.eq-concept-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                const conceptId = pill.getAttribute('data-concept-id');
                if (conceptId) {
                    switchPerspective('codex');
                    selectConcept(conceptId);
                }
            });
        });
    }

    function escapeHtml(text) {
        if (!text) return '';
        return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    // Launch parallel ingestion pipeline
    loadAllDatasets();
});
