"""Tests for the nightly visual backfill (papers persisted without a working image)."""
import json
import tempfile
import unittest
from pathlib import Path

import src.visual_backfill as vb

PAPER = """---\ntitle: "{title}"\nlevel: 1\n---\n\n# {title}\n\n## 1. Overview\nA short verified overview of the mechanism.\n\n## 6. Visual Representation\n{visual}\n\n## 7. Related Concepts\n- other\n"""


class VisualBackfillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.kb = Path(self.tmp.name) / "knowledge_base"
        self.level = self.kb / "level_1_fundamental_physics"
        self.images = self.kb / "images"
        self.level.mkdir(parents=True)
        self.images.mkdir()
        self._old_log = vb.PROMPT_LOG_FILE
        vb.PROMPT_LOG_FILE = self.kb / "logs" / "visual_prompts.jsonl"

    def tearDown(self):
        vb.PROMPT_LOG_FILE = self._old_log
        self.tmp.cleanup()

    def _paper(self, name, visual, title="Cosmic Ray Physics", eol="\n", body=None):
        text = (body or PAPER.format(title=title, visual=visual)).replace("\n", eol)
        p = self.level / name
        p.write_bytes(text.encode("utf-8"))
        return p

    def _image(self, name):
        (self.images / name).write_bytes(b"\x89PNG fake")
        return f"../images/{name}"

    def _gen(self, name="new_0.png", calls=None):
        def generate(prompt):
            if calls is not None:
                calls.append(prompt)
            return self._image(name)
        return generate

    def _run(self, **kw):
        kw.setdefault("use_llm", False)
        kw.setdefault("recovered", {})
        return vb.run_backfill(kb_root=self.kb, **kw)

    def test_healthy_paper_is_left_alone(self):
        rel = self._image("ok.png")
        p = self._paper("ok.md", f"![Cosmic Ray Physics]({rel})")
        before = p.read_bytes()
        stats = self._run(generate=self._gen())
        self.assertEqual(stats["pending_before"], 0)
        self.assertEqual(p.read_bytes(), before)

    def test_existing_images_are_relinked_without_generation(self):
        a = self._paper("a.md", f"[VISUAL_PENDING: {self._image('a.png')}]")
        b = self._paper("b.md", f"![VISUAL_PENDING: ...]({self._image('b.png')})")
        self._image("c.png")
        c = self._paper("c.md", "![Cosmic Ray Physics](images/c.png)")
        calls = []
        stats = self._run(generate=self._gen(calls=calls))
        self.assertEqual(stats["relinked"], 3)
        self.assertEqual(calls, [])
        self.assertIn("![Cosmic Ray Physics](../images/a.png)", a.read_text(encoding="utf-8"))
        self.assertIn("![Cosmic Ray Physics](../images/b.png)", b.read_text(encoding="utf-8"))
        self.assertIn("![Cosmic Ray Physics](../images/c.png)", c.read_text(encoding="utf-8"))
        self.assertEqual(stats["pending_after"], 0)

    def test_recovered_prompt_is_used_and_marker_replaced_preserving_crlf(self):
        marker = '[VISUAL_PENDING: invalid output directory: output directory "/home/runner/x" must be relative]'
        p = self._paper("cosmic_ray_physics.md", marker, eol="\r\n")
        recovered = {"knowledge_base/level_1_fundamental_physics/cosmic_ray_physics.md": {"prompt": "ORIGINAL PROMPT"}}
        calls = []
        stats = self._run(generate=self._gen(calls=calls), recovered=recovered)
        self.assertEqual(calls, ["ORIGINAL PROMPT"])
        self.assertEqual(stats["generated"], 1)
        raw = p.read_bytes().decode("utf-8")
        self.assertIn("![Cosmic Ray Physics](../images/new_0.png)", raw)
        self.assertNotIn("VISUAL_PENDING", raw)
        self.assertNotIn("\n", raw.replace("\r\n", ""))  # still pure CRLF
        log = [json.loads(line) for line in vb.PROMPT_LOG_FILE.read_text(encoding="utf-8").splitlines()]
        self.assertEqual((log[-1]["source"], log[-1]["status"], log[-1]["prompt"]), ("recovered_log", "ok", "ORIGINAL PROMPT"))

    def test_description_in_marker_is_reused_as_prompt(self):
        desc = "A two-panel scientific schematic on a dark background showing " + "Weyl cones and chiral currents " * 10
        self._paper("chiral.md", f"[VISUAL_PENDING: {desc}]")
        calls = []
        self._run(generate=self._gen(calls=calls))
        self.assertEqual(calls, [desc.strip()])

    def test_template_prompt_when_nothing_recovered(self):
        self._paper("noether.md", "[VISUAL_PENDING: ...]", title="Noether's Theorem")
        calls = []
        self._run(generate=self._gen(calls=calls))
        self.assertIn("Noether's Theorem", calls[0])
        self.assertIn("verified overview of the mechanism", calls[0])

    def test_svg_fallback_is_discarded_and_paper_stays_pending(self):
        p = self._paper("x.md", "[VISUAL_PENDING: ...]")
        svg = self.images / "diagram_concept_abc.svg"

        def generate(prompt):
            svg.write_text("<svg/>", encoding="utf-8")
            return "../images/diagram_concept_abc.svg"

        stats = self._run(generate=generate)
        self.assertEqual((stats["generated"], stats["failed"]), (0, 1))
        self.assertFalse(svg.exists())
        self.assertIn("VISUAL_PENDING", p.read_text(encoding="utf-8"))

    def test_cap_and_stop_after_two_consecutive_failures(self):
        for i in range(5):
            self._paper(f"p{i}.md", "[VISUAL_PENDING: ...]")
        counter = iter(range(100))
        stats = self._run(generate=lambda prompt: self._image(f"g{next(counter)}.png"), max_items=3)
        self.assertEqual((stats["generated"], stats["skipped"], stats["pending_after"]), (3, 2, 2))

        calls = []

        def failing(prompt):
            calls.append(prompt)
            return "GENMEDIA_UNAVAILABLE: quota"

        stats = self._run(generate=failing, max_items=10)
        self.assertEqual((len(calls), stats["failed"], stats["skipped"]), (2, 2, 0))

    def test_paper_without_visual_section_gets_one_before_section_7(self):
        body = "---\ntitle: \"CP Violation\"\n---\n\n# CP Violation\n\n## Summary\nText.\n\n## 7. Related Concepts\n- x\n"
        p = self._paper("cp.md", "", body=body)
        self._run(generate=self._gen())
        text = p.read_text(encoding="utf-8")
        self.assertIn("## 6. Visual Representation\n![CP Violation](../images/new_0.png)\n\n## 7. Related Concepts", text)

    def test_broken_sandbox_link_is_replaced(self):
        p = self._paper("qg.md", "![Quantum Gravity](sandbox:/generated_images/qg_001.png)")
        self._run(generate=self._gen())
        text = p.read_text(encoding="utf-8")
        self.assertNotIn("sandbox:", text)
        self.assertIn("(../images/new_0.png)", text)


if __name__ == "__main__":
    unittest.main()
