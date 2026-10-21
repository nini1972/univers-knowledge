"""Nightly self-healing for papers whose visual was never saved.

Between roughly 2026-07 and 2026-10-11 the image tool failed in several ways (absolute output directory,
chatty model replies, sandbox paths, ...), so some papers were persisted with a ``[VISUAL_PENDING: ...]``
marker or a broken image link instead of a picture. This module repairs a few of them per nightly run:

1. ``relink``      - the image file exists but the markdown points at it wrongly -> fix the link only.
2. ``regenerate``  - no usable image -> generate one and put it in "## 6. Visual Representation".

Prompt priority for regeneration:
  a. the original prompt recovered from the GitHub Actions logs (``src/data/recovered_visual_prompts.json``),
  b. a real image description left inside the VISUAL_PENDING marker,
  c. a new prompt written by the visualizer LLM from the paper's title and overview,
  d. a deterministic template (title + overview + house style).

Only a real raster image counts as success; the SVG text-card fallback of the image tool is discarded so the
paper stays pending and is retried on a later night. Every attempt is appended to
``knowledge_base/logs/visual_prompts.jsonl`` so prompts are never lost again.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KB_ROOT = REPO_ROOT / "knowledge_base"
RECOVERED_PROMPTS_FILE = REPO_ROOT / "src" / "data" / "recovered_visual_prompts.json"
PROMPT_LOG_FILE = KB_ROOT / "logs" / "visual_prompts.jsonl"

RASTER_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
IMAGE_TAG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
PENDING_RE = re.compile(r"!?\[VISUAL_PENDING:[^\]\n]*\](?:\([^)\n]*\))?")
VISUAL_HEADING_RE = re.compile(r"(?m)^##\s*(?:6\.\s*)?Visual[^\n]*$")
SECTION_7_RE = re.compile(r"(?m)^##\s*7\.\s")
NON_DESCRIPTION_PREFIXES = (
    "...", "invalid output", "genmedia_unavailable", "the image generat", "here is", "here's",
    "../images", "images/", "quantum fisher information bounds diagram",
)

HOUSE_STYLE = (
    "Cinematic deep-space aesthetic on a premium dark obsidian backdrop; vibrant curated neon highlights "
    "(quantum cyan, stellar ultraviolet, glowing nebular violet, supernova orange); technical schematic "
    "line-art, glassmorphism lenses and geometric overlay patterns; immersive, layered, multi-dimensional; "
    "a vivid, structurally accurate visual metaphor of the physical mechanism. No text paragraphs in the image."
)


# ── Detection ────────────────────────────────────────────────────────────────

def _paper_title(text: str, path: Path) -> str:
    m = re.search(r'(?m)^title:\s*["\']?(.+?)["\']?\s*$', text)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if m:
        return m.group(1).strip()
    return path.stem.replace("_", " ").title()


def _is_local_raster(paper: Path, target: str) -> bool:
    if target.startswith(("http://", "https://", "sandbox:")):
        return False
    resolved = (paper.parent / target).resolve()
    return resolved.suffix.lower() in RASTER_EXTENSIONS and resolved.is_file()


def inspect_paper(paper: Path) -> dict | None:
    """Return a repair plan for ``paper`` or None when it already shows a working image."""
    text = paper.read_text(encoding="utf-8", errors="replace")
    title = _paper_title(text, paper)
    pending = PENDING_RE.search(text)

    for m in IMAGE_TAG_RE.finditer(text):
        alt, target = m.group(1), m.group(2)
        if _is_local_raster(paper, target):
            if alt.startswith("VISUAL_PENDING"):
                return {"action": "relink", "old": m.group(0), "image": target, "title": title}
            return None  # healthy image
        # e.g. "images/x.png" written relative to knowledge_base instead of the level folder
        fixed = f"../images/{Path(target).name}"
        if not target.startswith(("http://", "https://")) and _is_local_raster(paper, fixed):
            return {"action": "relink", "old": m.group(0), "image": fixed, "title": title}

    if pending:
        inner = re.search(r"VISUAL_PENDING:\s*([^\]\n]*)", pending.group(0)).group(1).strip()
        path_m = re.search(r"\.\./images/[\w.\-]+", inner)
        if path_m and _is_local_raster(paper, path_m.group(0)):
            return {"action": "relink", "old": pending.group(0), "image": path_m.group(0), "title": title}

    broken = next((m.group(0) for m in IMAGE_TAG_RE.finditer(text)), None)
    return {
        "action": "regenerate",
        "old": pending.group(0) if pending else broken,
        "title": title,
        "marker_text": inner if pending else "",
    }


def find_papers_needing_visual(kb_root: Path = KB_ROOT) -> list[tuple[Path, dict]]:
    out = []
    for level_dir in sorted(kb_root.glob("level_*")):
        for paper in sorted(level_dir.glob("*.md")):
            plan = inspect_paper(paper)
            if plan:
                out.append((paper, plan))
    return out


# ── Prompt sources ───────────────────────────────────────────────────────────

def _paper_key(paper: Path) -> str:
    try:
        return paper.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return f"knowledge_base/{paper.parent.name}/{paper.name}"


def load_recovered_prompts(path: Path = RECOVERED_PROMPTS_FILE) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[VISUAL BACKFILL] Could not read recovered prompts: {exc}")
        return {}


def _description_from_marker(marker_text: str) -> str:
    text = (marker_text or "").strip()
    if len(text) < 200 or text.lower().startswith(NON_DESCRIPTION_PREFIXES):
        return ""
    return text


def _overview(text: str, limit: int = 1800) -> str:
    body = re.sub(r"(?s)^---.*?---", "", text, count=1)
    m = re.search(r"(?ms)^##\s*(?:1\.\s*)?(?:Overview|Definition[^\n]*|Summary)\s*$(.*?)(?=^##\s)", body)
    chunk = m.group(1) if m else body
    chunk = re.sub(r"\$\$.*?\$\$", " ", chunk, flags=re.S)
    chunk = re.sub(r"\s+", " ", chunk).strip()
    return chunk[:limit]


def template_prompt(title: str, overview: str) -> str:
    return (
        f"A scientific concept illustration of '{title}'. Visualize the core physical mechanism: "
        f"{overview[:900]} {HOUSE_STYLE}"
    )


def llm_prompt(title: str, overview: str) -> str:
    """Ask the visualizer LLM for a one-paragraph prompt; empty string on any failure."""
    try:
        try:
            from agents.universe_agents import _get_llm
        except ImportError:
            from src.agents.universe_agents import _get_llm
        llm = _get_llm("visualizer")
        if llm is None:
            return ""
        reply = llm.call([
            {"role": "system", "content": "You write image-generation prompts for scientific concept art."},
            {"role": "user", "content": (
                f"Concept: {title}\n\nVerified overview: {overview}\n\n"
                "Write ONE highly detailed paragraph (150-300 words) that is an image-generation prompt "
                "visualizing the core physical mechanism of this concept. Style rules: " + HOUSE_STYLE +
                "\nReturn only the prompt paragraph, no preamble."
            )},
        ])
        reply = str(reply or "").strip().strip('"')
        return reply if len(reply) >= 150 else ""
    except Exception as exc:
        print(f"[VISUAL BACKFILL] LLM prompt generation failed: {exc}")
        return ""


def choose_prompt(paper: Path, plan: dict, recovered: dict, use_llm: bool = True) -> tuple[str, str]:
    rec = recovered.get(_paper_key(paper))
    if rec and rec.get("prompt"):
        return rec["prompt"], "recovered_log"
    desc = _description_from_marker(plan.get("marker_text", ""))
    if desc:
        return desc, "pending_marker"
    overview = _overview(paper.read_text(encoding="utf-8", errors="replace"))
    if use_llm:
        prompt = llm_prompt(plan["title"], overview)
        if prompt:
            return prompt, "llm"
    return template_prompt(plan["title"], overview), "template"


# ── Editing ──────────────────────────────────────────────────────────────────

def apply_image(paper: Path, plan: dict, image_rel: str) -> None:
    """Write ``![title](image_rel)`` into the paper, preserving its line endings."""
    raw = paper.read_bytes().decode("utf-8", errors="replace")
    eol = "\r\n" if "\r\n" in raw else "\n"
    tag = f"![{plan['title']}]({image_rel})"
    old = plan.get("old")
    if old and old in raw:
        new = raw.replace(old, tag, 1)
    else:
        heading = VISUAL_HEADING_RE.search(raw)
        if heading:
            pos = heading.end()
            new = raw[:pos] + eol + tag + eol + raw[pos:]
        else:
            section = f"## 6. Visual Representation{eol}{tag}{eol}{eol}"
            s7 = SECTION_7_RE.search(raw)
            if s7:
                new = raw[:s7.start()] + section + raw[s7.start():]
            else:
                new = raw.rstrip() + eol + eol + section
    paper.write_bytes(new.encode("utf-8"))


def log_prompt_event(record: dict, path: Path | None = None) -> None:
    path = path or PROMPT_LOG_FILE
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **record}
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"[VISUAL BACKFILL] Could not write prompt log: {exc}")


def _default_generate(prompt: str) -> str:
    try:
        from tools.genmedia_tools import _generate_image_async
    except ImportError:
        from src.tools.genmedia_tools import _generate_image_async
    return asyncio.run(_generate_image_async(prompt))


def _accept_image(result: str, paper: Path) -> str:
    """Return the relative image path when ``result`` is a real raster image; discard SVG fallbacks."""
    result = (result or "").strip()
    if not result or result.startswith("GENMEDIA_UNAVAILABLE"):
        return ""
    if "diagram_concept_" in result and result.endswith(".svg"):
        try:
            (paper.parent / result).resolve().unlink(missing_ok=True)
        except Exception:
            pass
        return ""
    return result if _is_local_raster(paper, result) else ""


# ── Runner ───────────────────────────────────────────────────────────────────

def run_backfill(max_items: int | None = None, generate=None, use_llm: bool = True,
                 kb_root: Path = KB_ROOT, recovered: dict | None = None) -> dict:
    """Repair up to ``max_items`` papers needing image generation (relinks are free and always done)."""
    if max_items is None:
        max_items = int(os.getenv("VISUAL_BACKFILL_MAX", "8"))
    generate = generate or _default_generate
    recovered = load_recovered_prompts() if recovered is None else recovered

    todo = find_papers_needing_visual(kb_root)
    stats = {"pending_before": len(todo), "relinked": 0, "generated": 0, "failed": 0, "skipped": 0}
    print(f"\n--- VISUAL BACKFILL: {len(todo)} paper(s) without a working image ---")

    # Recovered original prompts first, then everything else (oldest file name order is stable).
    todo.sort(key=lambda item: (item[1]["action"] != "relink", _paper_key(item[0]) not in recovered))
    consecutive_failures = 0
    for paper, plan in todo:
        if plan["action"] == "relink":
            apply_image(paper, plan, plan["image"])
            stats["relinked"] += 1
            print(f"[VISUAL BACKFILL] relinked existing image in {paper.name}")
            log_prompt_event({"paper": _paper_key(paper), "source": "relink", "image": plan["image"], "status": "ok"})
            continue
        if stats["generated"] + stats["failed"] >= max_items or consecutive_failures >= 2:
            stats["skipped"] += 1
            continue

        prompt, source = choose_prompt(paper, plan, recovered, use_llm=use_llm)
        started = time.time()
        try:
            result = generate(prompt)
        except Exception as exc:
            result = f"GENMEDIA_UNAVAILABLE: {exc}"
        image = _accept_image(result, paper)
        record = {"paper": _paper_key(paper), "source": source, "prompt": prompt,
                  "seconds": round(time.time() - started, 1)}
        if image:
            apply_image(paper, plan, image)
            stats["generated"] += 1
            consecutive_failures = 0
            print(f"[VISUAL BACKFILL] generated image for {paper.name} (prompt: {source})")
            log_prompt_event({**record, "image": image, "status": "ok"})
        else:
            stats["failed"] += 1
            consecutive_failures += 1
            print(f"[VISUAL BACKFILL] no image for {paper.name}: {str(result)[:160]}")
            log_prompt_event({**record, "status": "failed", "result": str(result)[:300]})

    stats["pending_after"] = len(find_papers_needing_visual(kb_root))
    print(f"[VISUAL BACKFILL] summary: {json.dumps(stats)}")
    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Repair papers without a working image.")
    parser.add_argument("--list", action="store_true", help="Only list papers needing a visual")
    parser.add_argument("--max", type=int, default=None, help="Max images to generate this run")
    args = parser.parse_args()
    if args.list:
        recovered = load_recovered_prompts()
        for paper, plan in find_papers_needing_visual():
            has_prompt = "recovered" if _paper_key(paper) in recovered else "-"
            print(f"{plan['action']:<10} {has_prompt:<9} {_paper_key(paper)}")
        return
    run_backfill(max_items=args.max)


if __name__ == "__main__":
    main()
