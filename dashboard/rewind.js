/* ==========================================================================
   🌌 SINGULARITY REWIND SIMULATOR CONTROLLER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('rewind-canvas');
    const ctx = canvas.getContext('2d');

    const slider = document.getElementById('time-slider');
    const btnPlayPause = document.getElementById('btn-play-pause');
    const presetBtns = document.querySelectorAll('.preset-btn');

    // Display elements
    const timeDisplay = document.getElementById('val-time-display');
    const rhoPhiDisplay = document.getElementById('val-rho-phi-display');
    const holoDisplay = document.getElementById('val-holo-display');
    const sliderEpochReadout = document.getElementById('slider-epoch-readout');
    const hudEpochTitle = document.getElementById('hud-epoch-title');

    const valBitDensity = document.getElementById('val-bit-density');
    const holoProgressFill = document.getElementById('holo-progress-fill');
    const holoProgressText = document.getElementById('holo-progress-text');
    const expFriedmann = document.getElementById('exp-friedmann');

    let isPlaying = false;
    let animId = null;
    let particles = [];
    const NUM_PARTICLES = 400;

    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
        initParticles();
    }

    window.addEventListener('resize', resizeCanvas);

    function initParticles() {
        particles = [];
        for (let i = 0; i < NUM_PARTICLES; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 1.5,
                vy: (Math.random() - 0.5) * 1.5,
                radius: Math.random() * 2 + 1,
                color: Math.random() > 0.5 ? '#00f2fe' : (Math.random() > 0.5 ? '#ffab00' : '#e0aaff')
            });
        }
    }

    // Scrubber scale: 1000 = Present Day (13.8 Gyr), 0 = Singularity (t -> 0)
    function getEpochData(val) {
        const factor = val / 1000.0; // 1.0 (today) to 0.0 (origin)

        let timeStr = '';
        let rhoPhi = 0; // % of critical density
        let bitDensityStr = '';
        let holoPct = 0;
        let hudText = '';
        let expText = '';

        if (factor > 0.6) {
            // Present Day (13.8 Gyr) down to CMB Recombination (380k yr)
            const alpha = (factor - 0.6) / 0.4; // 1.0 down to 0.0
            if (alpha > 0.95) {
                timeStr = `t = 13.8 Gyr`;
            } else if (alpha > 0.05) {
                const yr = (0.00038 + alpha * 13.79962).toFixed(1);
                timeStr = `t = ${yr} Gyr`;
            } else {
                timeStr = `t = 380k yr`;
            }
            rhoPhi = (68.3 + (1 - alpha) * 11.7).toFixed(1);
            bitDensityStr = `${(1.24 * Math.pow(10, 8 + (1 - alpha) * 6)).toExponential(2)} bits/m³`;
            holoPct = (0.001 + (1 - alpha) * 11.499).toFixed(3);
            hudText = `EPOCH: LATE-TIME COSMIC WEB (${timeStr}) — Filaments & Neural Isomorphisms`;
            expText = `At late times ($t = 13.8\\text{ Gyr}$), dark energy ($\\Lambda$) and dark matter ($\\rho_m$) drive cosmic web structure formation.`;
        } else if (factor > 0.2) {
            // CMB Recombination (380k yr) down to BBN (1 s)
            const alpha = (factor - 0.2) / 0.4; // 1.0 down to 0.0
            if (alpha > 0.9) {
                timeStr = `t = 380k yr`;
            } else if (alpha < 0.1) {
                timeStr = `t = 1.00 s`;
            } else {
                const kYr = Math.round(1 + alpha * 379);
                timeStr = `t = ${kYr}k yr`;
            }
            rhoPhi = (80.0 + (1 - alpha) * 15.2).toFixed(1);
            bitDensityStr = `${(1.0 * Math.pow(10, 14 + (1 - alpha) * 11)).toExponential(2)} bits/m³`;
            holoPct = (11.5 + (1 - alpha) * 76.0).toFixed(2);
            hudText = `EPOCH: CMB RECOMBINATION & PLASMA (${timeStr}) — Gaussian Density Perturbations`;
            expText = `Matter density ($\\rho_m$) rises as photon-baryon fluid decouples at $z \\approx 1100$, generating cosmic microwave background fluctuations.`;
        } else if (factor > 0.02) {
            // BBN (1 s) down to Inflation (10^-35 s)
            const alpha = (factor - 0.02) / 0.18; // 1.0 down to 0.0
            if (alpha > 0.8) {
                timeStr = `t = 1.00 s`;
            } else if (alpha < 0.1) {
                timeStr = `t = 10⁻³⁵ s`;
            } else {
                const sec = (alpha * 1.0).toFixed(2);
                timeStr = `t = ${sec} s`;
            }
            rhoPhi = (95.2 + (1 - alpha) * 4.7).toFixed(1);
            bitDensityStr = `${(1.0 * Math.pow(10, 25 + (1 - alpha) * 50)).toExponential(2)} bits/m³`;
            holoPct = (87.5 + (1 - alpha) * 12.4).toFixed(1);
            hudText = `EPOCH: BIG BANG NUCLEOSYNTHESIS & INFLATION (${timeStr}) — Radiation Dominated Era`;
            expText = `Classical matter density vanishes ($\\rho_m \\to 0$). Radiation and Integrated Information scalar ($\\Phi$) dominate Friedmann expansion.`;
        } else {
            // Pure Singularity Rewind (t -> 0)
            timeStr = `t → 0 (Planck Origin)`;
            rhoPhi = '100.0';
            bitDensityStr = `1.42 × 10¹⁰⁶ bits/m³ (Planck Bit Density)`;
            holoPct = '100.0';
            hudText = `EPOCH: PURE INFORMATION SINGULARITY (t → 0) — Holographic Saturation (100%)`;
            expText = `Classical matter density $\\rho_m \\equiv 0$. The expansion rate $H^2(t)$ is driven entirely by Pure Information Critical Density $\\rho_c = \\frac{3H^2}{8\\pi G}$, 100% saturating the Bekenstein Holographic Bound.`;
        }

        return { factor, timeStr, rhoPhi, bitDensityStr, holoPct, hudText, expText };
    }

    function updateSimulation() {
        const val = parseFloat(slider.value);
        const data = getEpochData(val);

        // Update Text Readouts
        timeDisplay.textContent = data.timeStr;
        rhoPhiDisplay.textContent = `${data.rhoPhi}% ρ_c`;
        holoDisplay.textContent = `${data.holoPct}%`;
        sliderEpochReadout.textContent = data.timeStr;
        hudEpochTitle.textContent = data.hudText;

        valBitDensity.textContent = data.bitDensityStr;
        holoProgressFill.style.width = `${Math.min(data.holoPct, 100)}%`;
        holoProgressText.textContent = `Holographic Limit Saturation: ${data.holoPct}%`;
        expFriedmann.textContent = data.expText;

        renderCanvas(data.factor);
    }

    function renderCanvas(factor) {
        ctx.fillStyle = '#050811';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;

        // As factor -> 0 (rewind to origin), particles collapse toward center!
        const collapseRadius = Math.max(30, factor * (canvas.width * 0.45));

        // Draw connections (cosmic web filaments)
        if (factor > 0.05) {
            ctx.strokeStyle = `rgba(0, 242, 254, ${0.15 * factor})`;
            ctx.lineWidth = 0.5;
            for (let i = 0; i < particles.length; i += 4) {
                for (let j = i + 1; j < particles.length; j += 12) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 100 * factor) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
        }

        // Draw Particles / Core
        particles.forEach(p => {
            // Update position towards center as factor shrinks
            const targetX = cx + (p.x - cx) * 0.98;
            const targetY = cy + (p.y - cy) * 0.98;

            p.x += p.vx * factor + (cx - p.x) * (1 - factor) * 0.05;
            p.y += p.vy * factor + (cy - p.y) * (1 - factor) * 0.05;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = factor < 0.1 ? '#ffd700' : p.color;
            ctx.fill();
        });

        // Singularity Holographic Core at t -> 0
        if (factor < 0.2) {
            const coreGlow = (1 - factor) * 60;
            const grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, coreGlow);
            grad.addColorStop(0, '#ffffff');
            grad.addColorStop(0.3, '#ffd700');
            grad.addColorStop(0.7, 'rgba(255, 215, 0, 0.3)');
            grad.addColorStop(1, 'transparent');

            ctx.beginPath();
            ctx.arc(cx, cy, coreGlow, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();
        }
    }

    // Slider listener
    slider.addEventListener('input', updateSimulation);

    // Preset buttons
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            presetBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const preset = btn.dataset.preset;
            if (preset === '13.8gyr') slider.value = 1000;
            else if (preset === '380kyr') slider.value = 500;
            else if (preset === '1sec') slider.value = 150;
            else if (preset === 'inflation') slider.value = 30;
            else if (preset === 'singularity') slider.value = 0;

            updateSimulation();
        });
    });

    // Play / Pause Animation
    btnPlayPause.addEventListener('click', () => {
        isPlaying = !isPlaying;
        btnPlayPause.innerHTML = isPlaying ? '<i class="fa-solid fa-pause"></i>' : '<i class="fa-solid fa-play"></i>';

        if (isPlaying) stepAnimation();
    });

    function stepAnimation() {
        if (!isPlaying) return;
        let currentVal = parseFloat(slider.value);
        currentVal -= 4;
        if (currentVal <= 0) {
            currentVal = 0;
            isPlaying = false;
            btnPlayPause.innerHTML = '<i class="fa-solid fa-play"></i>';
        }
        slider.value = currentVal;
        updateSimulation();

        if (isPlaying) requestAnimationFrame(stepAnimation);
    }

    // Init
    resizeCanvas();
    updateSimulation();
});
