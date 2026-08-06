/* ==========================================================================
   🌌 REVERSE-TIME GRAPH FULLSCREEN INTERACTIVE CONTROLLER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const viewport = document.getElementById('rt-viewport');
    const stage = document.getElementById('rt-image-stage');
    const sidebar = document.getElementById('rt-sidebar');
    const toggleBtn = document.getElementById('btn-toggle-sidebar');
    const seedContainer = document.getElementById('seed-list-container');

    const btnZoomIn = document.getElementById('btn-rt-zoom-in');
    const btnZoomOut = document.getElementById('btn-rt-zoom-out');
    const btnReset = document.getElementById('btn-rt-reset');

    let scale = 1.0;
    let panX = 0;
    let panY = 0;
    let isDragging = false;
    let startX = 0;
    let startY = 0;

    function updateTransform() {
        stage.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
    }

    // Zoom Controls
    btnZoomIn.addEventListener('click', () => {
        scale = Math.min( scale * 1.2, 4.0 );
        updateTransform();
    });

    btnZoomOut.addEventListener('click', () => {
        scale = Math.max( scale / 1.2, 0.5 );
        updateTransform();
    });

    btnReset.addEventListener('click', () => {
        scale = 1.0;
        panX = 0;
        panY = 0;
        updateTransform();
    });

    // Mouse Wheel Zoom
    viewport.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 1.1 : 0.9;
        scale = Math.min(Math.max(scale * delta, 0.5), 4.0);
        updateTransform();
    }, { passive: false });

    // Drag & Pan Controls
    viewport.addEventListener('mousedown', (e) => {
        if (e.target.closest('#rt-sidebar') || e.target.closest('.rt-zoom-hud') || e.target.closest('.sidebar-toggle-btn')) return;
        isDragging = true;
        startX = e.clientX - panX;
        startY = e.clientY - panY;
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        panX = e.clientX - startX;
        panY = e.clientY - startY;
        updateTransform();
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
    });

    // Toggle Sidebar
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // Fetch and Render Seed Crystals from reverse_time_graph.json
    fetch('../knowledge_base/reverse_time_graph.json')
        .then(res => res.json())
        .then(data => {
            if (!data || !data.symbols) return;

            const seedSymbols = data.symbols.filter(s => s.is_seed_crystal);
            seedContainer.innerHTML = seedSymbols.map(s => `
                <div class="seed-card">
                    <div style="display:flex; flex-direction:column; gap:2px;">
                        <span class="seed-sym" id="sym-${s.symbol.replace(/\\/g, '')}">${s.symbol}</span>
                        <span class="seed-desc" title="${s.description}">${s.description}</span>
                    </div>
                    <span class="seed-count">${s.concept_count} concepts</span>
                </div>
            `).join('');

            // Render KaTeX for math symbols
            if (window.katex) {
                seedSymbols.forEach(s => {
                    const elem = document.getElementById(`sym-${s.symbol.replace(/\\/g, '')}`);
                    if (elem) {
                        try {
                            katex.render(s.symbol, elem, { throwOnError: false });
                        } catch (err) {
                            elem.textContent = s.symbol;
                        }
                    }
                });
            }
        })
        .catch(err => {
            console.warn('Could not load reverse_time_graph.json:', err);
        });
});
