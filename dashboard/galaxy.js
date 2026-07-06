/* ═══════════════════════════════════════════════════════════════════
   GALAXY.JS — Milky Way Galaxy Engine
   Univers Knowledge — Separate galaxy visualization page
   ═══════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    /* ─────────────────────────────────────────────────────────────────
       SPIRAL ARM DEFINITIONS
       8 arms, each covering one thematic cluster of physics concepts.
       Colors are carefully chosen to be distinct and space-appropriate.
       ───────────────────────────────────────────────────────────────── */
    const ARMS = [
        {
            name:   'Neutrino Physics',
            stroke: 'hsl(310, 90%, 62%)',
            fill:   'hsl(310, 80%, 10%)',
            glow:   'rgba(255,50,215,0.55)',
            nebula: [255, 35, 200],
            match:  id => id.includes('neutrino')
        },
        {
            name:   'Quantum Gravity',
            stroke: 'hsl(270, 90%, 68%)',
            fill:   'hsl(270, 80%, 10%)',
            glow:   'rgba(150,75,255,0.55)',
            nebula: [120, 55, 255],
            match:  id => id.includes('quantum_gravity') || id.includes('loop_quantum') ||
                          id.includes('causal_dynamical') || id.includes('asymptotic_safety') ||
                          id.includes('string_theory') || id.includes('spin_foam')
        },
        {
            name:   'Cosmology',
            stroke: 'hsl(38, 95%, 58%)',
            fill:   'hsl(38, 80%, 8%)',
            glow:   'rgba(255,158,38,0.55)',
            nebula: [255, 140, 28],
            match:  id => id.includes('cosmol') || id.includes('inflat') ||
                          id.includes('big_bang') || id.includes('cmb') ||
                          id.includes('baryon') || id.includes('lithium') ||
                          id.includes('primordial') || id.includes('nucleosynthesis')
        },
        {
            name:   'Standard Model',
            stroke: 'hsl(50, 95%, 58%)',
            fill:   'hsl(50, 80%, 8%)',
            glow:   'rgba(255,215,45,0.55)',
            nebula: [255, 200, 30],
            match:  id => id.includes('standard_model') || id.includes('higgs') ||
                          id.includes('fermion') || id.includes('electroweak') ||
                          id.includes('qcd') || id.includes('quark') ||
                          id.includes('boson') || id.includes('gauge_symmetry') ||
                          id.includes('spontaneous_symmetry')
        },
        {
            name:   'Dark Sector',
            stroke: 'hsl(220, 80%, 62%)',
            fill:   'hsl(220, 70%, 9%)',
            glow:   'rgba(75,125,255,0.55)',
            nebula: [55, 110, 255],
            match:  id => id.includes('dark') || id.includes('axion') ||
                          id.includes('wimp') || id.includes('cosmological_constant')
        },
        {
            name:   'Spacetime & GR',
            stroke: 'hsl(25, 95%, 60%)',
            fill:   'hsl(25, 80%, 8%)',
            glow:   'rgba(255,108,28,0.55)',
            nebula: [255, 90, 18],
            match:  id => id.includes('general_relativ') || id.includes('black_hole') ||
                          id.includes('spacetime') || id.includes('gravitational_wave') ||
                          id.includes('holograph')
        },
        {
            name:   'Beyond Std Model',
            stroke: 'hsl(285, 85%, 65%)',
            fill:   'hsl(285, 70%, 9%)',
            glow:   'rgba(195,75,255,0.55)',
            nebula: [175, 55, 255],
            match:  id => id.includes('supersymmet') || id.includes('beyond_standard') ||
                          id.includes('extra_dimension') || id.includes('hierarchy_problem') ||
                          id.includes('cp_violation') || id.includes('leptogenesis')
        },
        {
            name:   'Quantum Foundations',
            stroke: 'hsl(180, 100%, 50%)',
            fill:   'hsl(180, 60%, 8%)',
            glow:   'rgba(0,238,250,0.55)',
            nebula: [0, 215, 235],
            match:  () => true   // catch-all must be last
        }
    ];

    function getArmIndex(conceptId) {
        const id = conceptId.toLowerCase();
        for (let i = 0; i < ARMS.length - 1; i++) {
            if (ARMS[i].match(id)) return i;
        }
        return ARMS.length - 1;
    }

    /* ─────────────────────────────────────────────────────────────────
       STATE
       ───────────────────────────────────────────────────────────────── */
    const canvas = document.getElementById('galaxy-canvas');
    const ctx    = canvas.getContext('2d');

    let allConcepts  = [];
    let allRuns      = [];
    let chronoRuns   = [];
    let currentEpoch = 0;
    let visibleIds   = new Set();
    let starMap      = new Map();   // conceptId -> star data
    let birthTimes   = new Map();   // conceptId -> Date.now() of appearance
    let bgStars      = [];

    // Camera
    let zoom      = 0.88;
    let panX      = 0, panY = 0;
    let isPanning = false, lastMX = 0, lastMY = 0;
    let hoveredId = null;

    // Animation
    let rotAngle  = 0;
    const ROT_SPEED = 0.00022;  // radians per frame at ~60fps

    // Galaxy tilt: Y-axis compression that makes everything look like a real galaxy
    // photograph — viewed from ~25 degrees above the equatorial plane.
    // Applied globally so arms, core, nebulae all share the same perspective.
    const TILT_Y = 0.44;

    // Playback
    let isPlaying = false;
    let playTimer = null;
    let playSpeed = 1200;

    // RAF handle
    let rafId = null;

    /* ─────────────────────────────────────────────────────────────────
       SPIRAL MATH
       Logarithmic-style: r grows linearly, theta winds 2.4π from core to edge
       Inner radius: 88 world units | Outer radius: 88+440=528 world units
       ───────────────────────────────────────────────────────────────── */
    const INNER_R = 88;
    const ARM_LEN = 440;
    const WINDS   = 2.4 * Math.PI;   // how far each arm curves around the core

    function spiralPos(armIdx, t, extraRot) {
        const base  = armIdx * (2 * Math.PI / 8);
        const r     = INNER_R + t * ARM_LEN;
        const theta = base + t * WINDS + (extraRot || 0);
        return { x: r * Math.cos(theta), y: r * Math.sin(theta) };
    }

    function starRadius(degree) {
        if (degree >= 10) return 7.5;
        if (degree >= 6)  return 5.5;
        if (degree >= 3)  return 4.0;
        return 3.0;
    }

    /* ─────────────────────────────────────────────────────────────────
       BUILD STAR MAP — deterministic placement, zero collisions
       ───────────────────────────────────────────────────────────────── */
    function buildStarMap(concepts) {
        // Group by arm
        const groups = Array.from({ length: 8 }, () => []);
        concepts.forEach(c => {
            groups[getArmIndex(c.id)].push({ ...c, degree: (c.related || []).length });
        });

        // Sort: highest degree → innermost position (closest to galactic core)
        groups.forEach(g => g.sort((a, b) => b.degree - a.degree));

        starMap.clear();
        groups.forEach((group, armIdx) => {
            const n = group.length;
            group.forEach((c, i) => {
                // t: evenly distributed 0.04..0.97, with tiny deterministic jitter
                const tBase = n <= 1 ? 0.30 : (i / (n - 1)) * 0.88 + 0.05;
                let hash = 0;
                for (let k = 0; k < c.id.length; k++) hash = (hash * 31 + c.id.charCodeAt(k)) & 0xFFFFFF;
                const tJitter = ((hash % 1000) / 1000 - 0.5) * 0.052;
                const t = Math.max(0.02, Math.min(0.98, tBase + tJitter));

                const pos = spiralPos(armIdx, t, 0);
                starMap.set(c.id, {
                    x: pos.x, y: pos.y,
                    r: starRadius(c.degree),
                    t, armIdx,
                    arm: ARMS[armIdx],
                    concept: c
                });
            });

            // Update legend count badge
            const lcEl = document.getElementById(`lc-${armIdx}`);
            if (lcEl) lcEl.textContent = group.length;
        });
    }

    /* ─────────────────────────────────────────────────────────────────
       BACKGROUND DECORATIVE STARS (not concept stars)
       ───────────────────────────────────────────────────────────────── */
    function buildBgStars() {
        bgStars = [];
        for (let i = 0; i < 450; i++) {
            bgStars.push({
                x:       (Math.random() - 0.5) * 2800,
                y:       (Math.random() - 0.5) * 2800,
                r:        Math.random() * 1.18 + 0.22,
                opacity:  Math.random() * 0.44 + 0.08,
                phase:    Math.random() * Math.PI * 2
            });
        }
    }

    /* ─────────────────────────────────────────────────────────────────
       DRAW PIPELINE
       ───────────────────────────────────────────────────────────────── */
    function draw() {
        const DPR = window.devicePixelRatio || 1;
        const W   = canvas.width  / DPR;
        const H   = canvas.height / DPR;

        ctx.save();
        ctx.scale(DPR, DPR);

        // Background fill
        ctx.fillStyle = 'hsl(228, 28%, 3%)';
        ctx.fillRect(0, 0, W, H);

        // World transform: center + pan + zoom
        ctx.save();
        ctx.translate(W / 2 + panX * zoom, H / 2 + panY * zoom);
        ctx.scale(zoom, zoom);

        // Galaxy perspective tilt: compress Y so the whole galaxy looks like it's
        // viewed at ~25° above the equatorial plane — arms AND core on the same plane.
        ctx.scale(1, TILT_Y);

        drawBgStars();
        drawNebulae();
        drawCore();
        drawConceptStars();

        ctx.restore();
        ctx.restore();
    }

    function drawBgStars() {
        const t = Date.now() * 0.00092;
        bgStars.forEach(s => {
            ctx.save();
            ctx.globalAlpha = s.opacity * (0.62 + 0.38 * Math.sin(t + s.phase));
            ctx.fillStyle   = '#ffffff';
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        });
    }

    function drawNebulae() {
        // For each arm, draw soft radial gradient clouds at 4 sample points
        ARMS.forEach((arm, armIdx) => {
            [0.14, 0.38, 0.62, 0.84].forEach(t => {
                const pos    = spiralPos(armIdx, t, rotAngle);
                const radius = 90 + t * 120;
                const grad   = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, radius);
                const [r, g, b] = arm.nebula;
                grad.addColorStop(0,   `rgba(${r},${g},${b},0.042)`);
                grad.addColorStop(0.5, `rgba(${r},${g},${b},0.018)`);
                grad.addColorStop(1,   'transparent');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
                ctx.fill();
            });
        });
    }

    function drawCore() {
        // Outer halo glow
        const halo = ctx.createRadialGradient(0, 0, 0, 0, 0, 108);
        halo.addColorStop(0,   'rgba(218, 188, 255, 0.20)');
        halo.addColorStop(0.4, 'rgba(135, 75, 255, 0.10)');
        halo.addColorStop(1,   'transparent');
        ctx.fillStyle = halo;
        ctx.beginPath(); ctx.arc(0, 0, 108, 0, Math.PI * 2); ctx.fill();

        // Central bulge
        const bulge = ctx.createRadialGradient(0, 0, 0, 0, 0, 46);
        bulge.addColorStop(0,    'rgba(255,248,230,0.96)');
        bulge.addColorStop(0.20, 'rgba(255,225,185,0.66)');
        bulge.addColorStop(0.52, 'rgba(175,115,255,0.28)');
        bulge.addColorStop(1,    'transparent');
        ctx.fillStyle = bulge;
        ctx.beginPath(); ctx.arc(0, 0, 46, 0, Math.PI * 2); ctx.fill();

        // Accretion disk: rotating particles on a flattened ellipse
        const t = Date.now() * 0.00135;
        for (let i = 0; i < 28; i++) {
            const rDisk  = 7 + i * 3.0;
            const speed  = 1.85 / (rDisk * 0.062 + 0.82);
            const angle  = t * speed + i * (Math.PI * 2 / 28);
            const px     = rDisk * Math.cos(angle);
            const py     = rDisk * Math.sin(angle);  // circular — global TILT_Y handles the flattening
            const alpha  = 0.42 + 0.58 * Math.abs(Math.sin(angle * 2.4));
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle   = i % 3 === 0 ? 'hsl(270,90%,76%)' :
                              i % 3 === 1 ? 'hsl(310,90%,71%)' : '#ffffff';
            ctx.beginPath();
            ctx.arc(px, py, 1.32, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    function drawConceptStars() {
        const nowMs  = Date.now();
        const cosR   = Math.cos(rotAngle);
        const sinR   = Math.sin(rotAngle);

        starMap.forEach((star, conceptId) => {
            if (!visibleIds.has(conceptId)) return;

            // Rotate with the galaxy
            const rx = star.x * cosR - star.y * sinR;
            const ry = star.x * sinR + star.y * cosR;

            // Store rotated position for hover detection
            star._rx = rx;
            star._ry = ry;

            const isHov      = hoveredId === conceptId;
            const isVerified = star.concept.status === 'VERIFIED' || star.concept.status === '[VERIFIED]';

            // Birth flash (1.8 seconds after first appearing)
            const bornAt  = birthTimes.get(conceptId);
            const elapsed = bornAt ? (nowMs - bornAt) / 1000 : 99;
            const newborn = elapsed < 1.8 ? Math.max(0, (1.8 - elapsed) / 1.8) : 0;

            // Gentle twinkle
            const twinkle = 0.88 + 0.12 * Math.sin(nowMs * 0.00115 + star.armIdx * 1.32 + star.t * 7.4);
            const drawR   = star.r * twinkle * (isHov ? 1.75 : 1) + newborn * star.r * 2.2;

            // Outer halo
            if (isHov || newborn > 0.04 || isVerified) {
                const hR    = drawR + (isHov ? 12 : 6) + newborn * 20;
                const hGrad = ctx.createRadialGradient(rx, ry, 0, rx, ry, hR);
                const alpha = isHov ? 0.30 : (newborn > 0.04 ? newborn * 0.24 : 0.11);
                const glowColor = star.arm.glow.replace(/[\d.]+\)$/, `${alpha.toFixed(2)})`);
                hGrad.addColorStop(0, glowColor);
                hGrad.addColorStop(1, 'transparent');
                ctx.fillStyle = hGrad;
                ctx.beginPath();
                ctx.arc(rx, ry, hR, 0, Math.PI * 2);
                ctx.fill();
            }

            // Star core with radial gradient (white center → arm colour → arm fill)
            ctx.save();
            ctx.beginPath();
            ctx.arc(rx, ry, drawR, 0, Math.PI * 2);
            const cGrad = ctx.createRadialGradient(
                rx - drawR * 0.28, ry - drawR * 0.28, 0,
                rx, ry, drawR
            );
            cGrad.addColorStop(0,    'rgba(255,255,255,0.97)');
            cGrad.addColorStop(0.38, star.arm.stroke);
            cGrad.addColorStop(1,    star.arm.fill);
            ctx.fillStyle  = cGrad;
            ctx.shadowColor = star.arm.glow;
            ctx.shadowBlur  = isHov ? 18 : (isVerified ? 10 : 5);
            ctx.fill();

            // Verified stars get a crisp ring
            if (isVerified) {
                ctx.strokeStyle = star.arm.stroke;
                ctx.lineWidth   = 0.85;
                ctx.stroke();
            }
            ctx.restore();

            // Birth flash expanding ring
            if (newborn > 0.04) {
                ctx.save();
                ctx.globalAlpha  = newborn * 0.78;
                ctx.strokeStyle  = star.arm.stroke;
                ctx.lineWidth    = 1.7;
                ctx.beginPath();
                ctx.arc(rx, ry, star.r * (1 + (1 - newborn) * 9.5), 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();
            }
        });
    }

    /* ─────────────────────────────────────────────────────────────────
       ANIMATION LOOP
       ───────────────────────────────────────────────────────────────── */
    function tick() {
        rotAngle += ROT_SPEED;
        draw();
        rafId = requestAnimationFrame(tick);
    }

    /* ─────────────────────────────────────────────────────────────────
       TIMELINE / EPOCH LOGIC
       ───────────────────────────────────────────────────────────────── */
    function conceptMatchesRun(cTitle, rConcept) {
        if (!cTitle || !rConcept) return false;
        const clean = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
        const a = clean(cTitle), b = clean(rConcept);
        return a === b || (a.length > 8 && b.length > 8 && (a.includes(b) || b.includes(a)));
    }

    function updateEpoch() {
        const prevVisible = new Set(visibleIds);
        visibleIds.clear();

        // Concepts approved up to current epoch
        const approvedIds = new Set();
        chronoRuns.slice(0, currentEpoch).forEach(run => {
            if (run.status === 'approved') {
                allConcepts.forEach(c => {
                    if (conceptMatchesRun(c.title, run.concept)) approvedIds.add(c.id);
                });
            }
        });

        // Pre-existing concepts (no run at all) are always visible
        allConcepts.forEach(c => {
            const hasAnyRun = allRuns.some(r => conceptMatchesRun(c.title, r.concept));
            if (!hasAnyRun || approvedIds.has(c.id)) visibleIds.add(c.id);
        });

        // Record birth times for newly revealed stars
        const nowMs = Date.now();
        visibleIds.forEach(id => {
            if (!prevVisible.has(id)) birthTimes.set(id, nowMs);
        });

        refreshHUD();
    }

    function refreshHUD() {
        const total = chronoRuns.length;
        const pct   = total > 0 ? (currentEpoch / total) * 100 : 0;

        document.getElementById('stat-visible').textContent = visibleIds.size;
        document.getElementById('tl-fill').style.width      = `${pct}%`;
        document.getElementById('tl-thumb').style.left      = `${pct}%`;
        document.getElementById('epoch-badge').textContent  = `EPOCH ${currentEpoch} / ${total}`;

        if (currentEpoch === 0) {
            document.getElementById('tl-concept').textContent = 'Big Bang — Pre-Science Era';
            document.getElementById('tl-status').textContent  = '';
        } else {
            const run = chronoRuns[currentEpoch - 1];
            document.getElementById('tl-concept').textContent =
                `${run.concept} (Attempt #${run.attempt || 1})`;
            const sEl = document.getElementById('tl-status');
            sEl.textContent = run.status === 'approved' ? '\u2713 APPROVED' : '\u2717 REJECTED';
            sEl.className   = `tl-status ${run.status === 'approved' ? 's-approved' : 's-rejected'}`;
        }
    }

    /* ─────────────────────────────────────────────────────────────────
       PLAYBACK
       ───────────────────────────────────────────────────────────────── */
    function play() {
        if (isPlaying) return;
        if (currentEpoch >= chronoRuns.length) { currentEpoch = 0; updateEpoch(); }
        isPlaying = true;
        document.getElementById('tl-play').innerHTML = '<i class="fa-solid fa-pause"></i>';
        playTimer = setInterval(() => {
            if (currentEpoch < chronoRuns.length) { currentEpoch++; updateEpoch(); }
            else pause();
        }, playSpeed);
    }

    function pause() {
        isPlaying = false;
        clearInterval(playTimer); playTimer = null;
        document.getElementById('tl-play').innerHTML = '<i class="fa-solid fa-play"></i>';
    }

    /* ─────────────────────────────────────────────────────────────────
       HOVER / HIT DETECTION
       ───────────────────────────────────────────────────────────────── */
    function hitTest(clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        const cx   = clientX - rect.left;
        const cy   = clientY - rect.top;
        const W    = canvas.clientWidth;
        const H    = canvas.clientHeight;

        // Screen → world (account for TILT_Y compression on the Y axis)
        const wx = (cx - W / 2) / zoom - panX;
        const wy = (cy - H / 2) / (zoom * TILT_Y) - panY;

        // Un-rotate to match stored star positions
        const cosNeg = Math.cos(-rotAngle);
        const sinNeg = Math.sin(-rotAngle);
        const ux = wx * cosNeg - wy * sinNeg;
        const uy = wx * sinNeg + wy * cosNeg;

        let best = null, bestDist = Infinity;
        const pad = 10 / zoom;  // click radius in world units

        starMap.forEach((star, id) => {
            if (!visibleIds.has(id)) return;
            const dx = star.x - ux, dy = star.y - uy;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < Math.max(star.r + pad, pad * 1.5) && dist < bestDist) {
                bestDist = dist; best = id;
            }
        });
        return best;
    }

    function showTip(id, clientX, clientY) {
        const star = starMap.get(id);
        if (!star) return;
        const c   = star.concept;
        const arm = star.arm;

        document.getElementById('tip-name').textContent = c.title;
        document.getElementById('tip-name').style.color = arm.stroke;

        const sEl = document.getElementById('tip-status');
        const verified = c.status === 'VERIFIED' || c.status === '[VERIFIED]';
        sEl.textContent = verified ? 'VERIFIED' : 'THEORETICAL';
        sEl.className   = `tip-badge ${verified ? 'badge-verified' : 'badge-theoretical'}`;

        const aEl = document.getElementById('tip-arm');
        aEl.textContent         = arm.name.toUpperCase();
        aEl.style.color         = arm.stroke;
        aEl.style.borderColor   = arm.stroke;
        aEl.style.background    = arm.fill;

        document.getElementById('tip-conn').textContent = `${(c.related || []).length} CONNECTIONS`;

        const tip  = document.getElementById('star-tip');
        tip.style.borderColor = arm.stroke;

        const tipW = 285, tipH = 95;
        const left = clientX + 18 + tipW > window.innerWidth  ? clientX - tipW - 12 : clientX + 18;
        const top  = clientY + 12 + tipH > window.innerHeight ? clientY - tipH - 8  : clientY + 12;
        tip.style.left    = `${left}px`;
        tip.style.top     = `${top}px`;
        tip.style.display = 'block';
        canvas.style.cursor = 'pointer';
    }

    function hideTip() {
        document.getElementById('star-tip').style.display = 'none';
        canvas.style.cursor = '';
    }

    /* ─────────────────────────────────────────────────────────────────
       CANVAS RESIZE
       ───────────────────────────────────────────────────────────────── */
    function resizeCanvas() {
        const W = window.innerWidth;
        const H = window.innerHeight - 54 - 80;   // header 54px + timeline 80px
        canvas.style.width  = `${W}px`;
        canvas.style.height = `${H}px`;
        canvas.width  = Math.round(W * (window.devicePixelRatio || 1));
        canvas.height = Math.round(H * (window.devicePixelRatio || 1));
    }

    /* ─────────────────────────────────────────────────────────────────
       DATA LOADING
       ───────────────────────────────────────────────────────────────── */
    async function loadData() {
        try {
            const bust = `?t=${Date.now()}`;
            const [dbRes, evalRes] = await Promise.all([
                fetch(`../knowledge_base/database.json${bust}`),
                fetch(`../knowledge_base/logs/evaluation_runs.jsonl${bust}`)
            ]);

            if (!dbRes.ok) throw new Error(`database.json fetch failed (${dbRes.status})`);
            allConcepts = await dbRes.json();
            document.getElementById('stat-total').textContent = allConcepts.length;

            if (evalRes.ok) {
                const text = await evalRes.text();
                allRuns = text.split('\n')
                    .map(l => l.trim()).filter(Boolean)
                    .map(l => { try { return JSON.parse(l); } catch { return null; } })
                    .filter(Boolean);
            }

            chronoRuns   = [...allRuns].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            currentEpoch = chronoRuns.length;   // start at the present

            buildStarMap(allConcepts);
            buildBgStars();
            updateEpoch();

        } catch (err) {
            console.error('Galaxy data load failed:', err);
            document.getElementById('error-overlay').style.display = 'flex';
        }
    }

    /* ─────────────────────────────────────────────────────────────────
       EVENT LISTENERS
       ───────────────────────────────────────────────────────────────── */

    // Pan (click + drag)
    canvas.addEventListener('mousedown', e => {
        isPanning = true; lastMX = e.clientX; lastMY = e.clientY;
    });
    canvas.addEventListener('mousemove', e => {
        if (isPanning) {
            panX += (e.clientX - lastMX) / zoom;
            panY += (e.clientY - lastMY) / zoom;
            lastMX = e.clientX; lastMY = e.clientY;
            hideTip(); hoveredId = null;
            canvas.style.cursor = 'grabbing';
        } else {
            const hit = hitTest(e.clientX, e.clientY);
            if (hit !== hoveredId) {
                hoveredId = hit;
                if (hit) showTip(hit, e.clientX, e.clientY);
                else     hideTip();
            } else if (hit) {
                // Keep tooltip updated with cursor position
                showTip(hit, e.clientX, e.clientY);
            }
        }
    });
    canvas.addEventListener('mouseup',    () => { isPanning = false; });
    canvas.addEventListener('mouseleave', () => { isPanning = false; hideTip(); hoveredId = null; });

    // Scroll to zoom
    canvas.addEventListener('wheel', e => {
        e.preventDefault();
        const factor = e.deltaY > 0 ? 0.88 : 1.13;
        zoom = Math.max(0.11, Math.min(6.5, zoom * factor));
    }, { passive: false });

    // Zoom buttons
    document.getElementById('zoom-in').addEventListener('click',    () => { zoom = Math.min(6.5, zoom * 1.22); });
    document.getElementById('zoom-out').addEventListener('click',   () => { zoom = Math.max(0.11, zoom * 0.82); });
    document.getElementById('zoom-reset').addEventListener('click', () => { zoom = 0.88; panX = 0; panY = 0; });

    // Timeline controls
    document.getElementById('tl-play').addEventListener('click', () => isPlaying ? pause() : play());
    document.getElementById('tl-prev').addEventListener('click', () => {
        pause();
        if (currentEpoch > 0) { currentEpoch--; updateEpoch(); }
    });
    document.getElementById('tl-next').addEventListener('click', () => {
        pause();
        if (currentEpoch < chronoRuns.length) { currentEpoch++; updateEpoch(); }
    });
    document.getElementById('speed-select').addEventListener('change', e => {
        playSpeed = parseInt(e.target.value);
        if (isPlaying) { pause(); play(); }
    });

    // Track scrubbing
    let scrubbing = false;
    const track   = document.getElementById('tl-track');
    function scrubTo(clientX) {
        const rect = track.getBoundingClientRect();
        const pct  = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        currentEpoch = Math.round(pct * chronoRuns.length);
        updateEpoch();
    }
    track.addEventListener('mousedown', e => { scrubbing = true; pause(); scrubTo(e.clientX); });
    document.addEventListener('mousemove', e => { if (scrubbing) scrubTo(e.clientX); });
    document.addEventListener('mouseup',   () => { scrubbing = false; });

    // Keyboard shortcuts
    document.addEventListener('keydown', e => {
        if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') return;
        switch (e.key) {
            case 'ArrowRight': pause(); if (currentEpoch < chronoRuns.length) { currentEpoch++; updateEpoch(); } break;
            case 'ArrowLeft':  pause(); if (currentEpoch > 0) { currentEpoch--; updateEpoch(); } break;
            case ' ':          e.preventDefault(); isPlaying ? pause() : play(); break;
            case '0':          zoom = 0.88; panX = 0; panY = 0; break;
            case '+': case '=': zoom = Math.min(6.5, zoom * 1.22); break;
            case '-':           zoom = Math.max(0.11, zoom * 0.82); break;
        }
    });

    // Resize
    window.addEventListener('resize', resizeCanvas);

    /* ─────────────────────────────────────────────────────────────────
       INIT
       ───────────────────────────────────────────────────────────────── */
    resizeCanvas();
    loadData().then(() => tick());
});
