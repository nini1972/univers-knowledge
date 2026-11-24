#!/usr/bin/env python3
"""
Convert archival concept PNG images in knowledge_base/images/ to WebP,
update markdown references, rebuild knowledge_base/database.json and _index.md,
and verify zero broken image references remain.
"""

import json
import os
import re
import sys
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.index_utils import synchronize_index

EXCLUDED_PNGS = {"reverse_time_graph.png"}
PNG_TOKEN_RE = re.compile(r"([A-Za-z0-9_.\-]+\.png)")
MD_IMG_LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def folder_bytes(directory: Path) -> int:
    return sum(p.stat().st_size for p in directory.rglob("*") if p.is_file())


def convert_png_to_webp(src_path: Path, quality: int = 82) -> tuple[bool, Path]:
    dst_path = src_path.with_suffix(".webp")
    tmp_path = src_path.with_name(f"{src_path.stem}.webp.tmp")

    with Image.open(src_path) as im:
        save_im = im if im.mode in ("RGB", "RGBA") else im.convert("RGB")
        save_im.save(tmp_path, format="WEBP", quality=quality, method=6)

    with Image.open(tmp_path) as check_im:
        check_im.verify()

    if tmp_path.stat().st_size <= 0:
        tmp_path.unlink(missing_ok=True)
        return False, src_path

    os.replace(tmp_path, dst_path)
    if dst_path.stat().st_size < src_path.stat().st_size:
        src_path.unlink()
        return True, dst_path

    dst_path.unlink(missing_ok=True)
    return False, src_path


def rewrite_markdown_references(kb_dir: Path, converted_map: dict[str, str]) -> int:
    if not converted_map:
        return 0

    def _replace(match: re.Match) -> str:
        name = match.group(1)
        return converted_map.get(name, name)

    updated_files = 0
    for md_path in sorted(kb_dir.rglob("*.md")):
        original = md_path.read_text(encoding="utf-8", errors="replace")
        updated = PNG_TOKEN_RE.sub(_replace, original)
        if updated != original:
            md_path.write_text(updated, encoding="utf-8")
            updated_files += 1
    return updated_files


def verify_links(kb_dir: Path) -> list[str]:
    errors: list[str] = []
    db_path = kb_dir / "database.json"
    concepts = json.loads(db_path.read_text(encoding="utf-8"))
    for c in concepts:
        img_rel = c.get("image_path")
        if img_rel:
            norm = img_rel.replace("../", "").lstrip("/")
            if not (kb_dir / norm).is_file():
                errors.append(f"database.json concept '{c.get('id')}' missing image: {img_rel}")

    for md_path in sorted(kb_dir.rglob("*.md")):
        if md_path.name == "_index.md":
            continue
        text = md_path.read_text(encoding="utf-8", errors="replace")
        for m in MD_IMG_LINK_RE.finditer(text):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "data:")):
                continue
            resolved = (md_path.parent / target).resolve()
            if not resolved.is_file() and (kb_dir / target.replace("../", "")).is_file():
                continue
            if not resolved.is_file():
                errors.append(f"{md_path.relative_to(kb_dir)} broken image link: {target}")
    return errors


def main() -> int:
    kb_dir = REPO_ROOT / "knowledge_base"
    images_dir = kb_dir / "images"
    before_bytes = folder_bytes(images_dir)

    converted_map: dict[str, str] = {}
    skipped: list[str] = []

    for png_path in sorted(images_dir.glob("*.png")):
        if png_path.name in EXCLUDED_PNGS:
            skipped.append(png_path.name)
            continue
        ok, final_path = convert_png_to_webp(png_path)
        if ok:
            converted_map[png_path.name] = final_path.name
        else:
            skipped.append(png_path.name)

    updated_md_count = rewrite_markdown_references(kb_dir, converted_map)
    synchronize_index("knowledge_base/_index.md", REPO_ROOT)

    after_bytes = folder_bytes(images_dir)
    broken = verify_links(kb_dir)

    print(f"Images directory before: {before_bytes / 1e6:.2f} MB")
    print(f"Images directory after:  {after_bytes / 1e6:.2f} MB ({after_bytes / max(1, before_bytes) * 100:.1f}%)")
    print(f"Converted PNG -> WebP:   {len(converted_map)} files (skipped: {len(skipped)})")
    print(f"Markdown files updated:  {updated_md_count}")
    print(f"Broken image references: {len(broken)}")
    for err in broken[:20]:
        print(f"  BROKEN: {err}")

    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
