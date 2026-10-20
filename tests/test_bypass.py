"""Bypass corpus: each case is a known way to get a fabricated or unlinked quote past the tools.

Every bypass test asserts the SECURE behaviour (non-zero exit / FAIL / UNVERIFIED).
Controls (genuine quotes) must keep passing.
"""
import shutil
import subprocess
import sys
import tempfile
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "plugins/research-kit/bin"
FIX = Path(__file__).resolve().parent / "fixtures/bypass"
_ld = importlib.machinery.SourceFileLoader("vq", str(BIN / "verify-quotes"))
vq = importlib.util.module_from_spec(importlib.util.spec_from_loader("vq", _ld))
_ld.exec_module(vq)
SRC_MD = ROOT / "examples/basic/02_sources/md/lei2023financial.md"


class Bypass(unittest.TestCase):
    def project(self, note=None, draft=None, key=None):
        """Temp project with Lei's source md, one fixture note (saved as <key>.md) and a draft."""
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        root = Path(t.name)
        (root / "02_sources/md").mkdir(parents=True)
        (root / "01_notes/lit").mkdir(parents=True)
        shutil.copy(SRC_MD, root / "02_sources/md")
        if note:
            shutil.copy(FIX / "notes" / f"{note}.md", root / f"01_notes/lit/{key or note}.md")
        if draft:
            shutil.copy(FIX / "drafts" / f"{draft}.md", root / "draft.md")
        return root

    def run_tool(self, tool, root, target):
        return subprocess.run([sys.executable, str(BIN / tool), target], cwd=root,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def verify(self, note, key=None):
        root = self.project(note, key=key)
        return self.run_tool("verify-quotes", root, f"01_notes/lit/{key or note}.md")

    def claims(self, draft, note=None, key=None):
        root = self.project(note, draft, key)
        return self.run_tool("check-claims", root, "draft.md")

    def assertRejected(self, r):
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)

    def project_text(self, draft, notes=None, extra_md=None):
        """Project with Lei's note/source and a draft given as text. notes: {key: note text}."""
        root = self.project("lei2023financial")
        (root / "draft.md").write_text(draft, encoding="utf-8")
        for k, text in (notes or {}).items():
            (root / f"01_notes/lit/{k}.md").write_text(text, encoding="utf-8")
        return root

    def claims_text(self, draft, notes=None):
        return self.run_tool("check-claims", self.project_text(draft, notes), "draft.md")

    # controls: genuine material still passes
    def test_control_verify_quotes_genuine_passes(self):
        r = self.verify("lei2023financial")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_control_check_claims_genuine_ok(self):
        r = self.claims("genuine", "lei2023financial")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK", r.stdout)

    # bypasses
    def test_wrapped_quote_double_quoted_invented_continuation(self):
        self.assertRejected(self.verify("wrapped_dq"))

    def test_wrapped_quote_plain_invented_continuation(self):
        self.assertRejected(self.verify("wrapped_plain"))

    def test_flow_style_quotes_list(self):
        self.assertRejected(self.verify("flow"))

    def test_claims_without_quotes(self):
        self.assertRejected(self.verify("claims_only"))

    def test_fragment_quote(self):
        self.assertRejected(self.verify("fragment"))

    def test_note_bound_to_wrong_paper(self):
        # smith2020's quote is genuine Lei text; the note names Lei's source_md.
        self.assertRejected(self.verify("smith2020"))

    def test_check_claims_ok_despite_failing_quotes(self):
        root = self.project("fab2023", "fab2023")
        self.assertEqual(self.run_tool("verify-quotes", root, "01_notes/lit/fab2023.md").returncode, 1)
        self.assertRejected(self.run_tool("check-claims", root, "draft.md"))

    def test_fabricated_quote_in_draft(self):
        r = self.claims("fabricated_quote", "lei2023financial")
        self.assertTrue(r.returncode != 0 or "UNVERIFIED" in r.stdout, r.stdout)

    def test_draft_with_zero_recognised_citations(self):
        self.assertRejected(self.claims("zero_citations", "lei2023financial"))

    # round 1: quote <-> citation attachment and quote forms
    F = "Central banks always rescue labor markets in every crisis"
    REAL = "Conversely, Zeev (2019) underscores that freely depreciating exchange rates can spur exports"
    OTHER = ('---\ncitekey: other2020\nsource_md: none\nno_source: print book\nclaims:\n  - "x"\nquotes: []\n---\n')

    def assertUnverified(self, draft, notes=None):
        r = self.claims_text(draft, notes)
        self.assertNotEqual(r.returncode, 0, draft + r.stdout)
        self.assertIn("UNVERIFIED", r.stdout, draft)

    def test_quote_after_abbreviation_split(self):
        self.assertUnverified(f'As @lei2023financial et al. note, "{self.F}".\n')

    def test_citation_in_own_sentence(self):
        self.assertUnverified(f'Lei writes "{self.F}". [@lei2023financial, p. 3]\n')

    def test_other_quote_forms(self):
        for q in (f"\u2018{self.F}\u2019", f"\u00ab{self.F}\u00bb", f"&quot;{self.F}&quot;", f"<q>{self.F}</q>",
                  f"\u2039{self.F}\u203a", f"\u201e{self.F}\u201c", f"'{self.F}'"):
            self.assertUnverified(f"Lei writes {q} [@lei2023financial, p. 3].\n")

    def test_blockquote(self):
        self.assertUnverified(f"> {self.F}\n\n[@lei2023financial, p. 3]\n")
        self.assertUnverified(f"Lei writes:\n\n> {self.F}\n> [@lei2023financial, p. 3]\n")
        self.assertUnverified(f"Lei [@lei2023financial] writes:\n\n> {self.F}\n")

    def test_unclosed_quote(self):
        self.assertUnverified(f"Lei writes \u201c{self.F} [@lei2023financial, p. 3].\n")
        self.assertUnverified(f'Lei writes "{self.F} [@lei2023financial, p. 3].\n')

    def test_real_quote_misattributed(self):
        self.assertUnverified(f'Others say "{self.REAL}" [@other2020].\n', {"other2020": self.OTHER})
        r = self.claims_text(f'Others say "{self.REAL}" [@other2020; @lei2023financial].\n', {"other2020": self.OTHER})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("held by lei2023financial", r.stdout)

    def test_braced_key_and_masked_regions(self):
        self.assertUnverified(f'Lei writes "{self.F}" [@{{lei2023financial}}].\n')
        r = self.claims_text("<!-- [@lei2023financial] -->\n\n```\n[@lei2023financial]\n```\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("0 cited paragraph(s)", r.stdout)

    def test_hyphen_is_a_word_character(self):
        note = (FIX / "notes/lei2023financial.md").read_text(encoding="utf-8").replace(
            "Conversely, Zeev (2019) underscores that freely depreciating exchange rates can spur exports",
            "eurozone countries, labor market flexibility is pivotal").replace("page: 3", "page: 9")
        root = self.project("lei2023financial")
        (root / "01_notes/lit/lei2023financial.md").write_text(note, encoding="utf-8")
        self.assertRejected(self.run_tool("verify-quotes", root, "01_notes/lit/lei2023financial.md"))

    def test_non_ascii_digit_page_is_clean_failure(self):
        note = (FIX / "notes/lei2023financial.md").read_text(encoding="utf-8").replace("page: 3", 'page: "\u00b2"')
        root = self.project("lei2023financial")
        (root / "01_notes/lit/lei2023financial.md").write_text(note, encoding="utf-8")
        r = self.run_tool("verify-quotes", root, "01_notes/lit/lei2023financial.md")
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("Traceback", r.stderr)

    def test_empty_note_fails(self):
        root = self.project("lei2023financial")
        (root / "01_notes/lit/lei2023financial.md").write_text(
            "---\ncitekey: lei2023financial\nclaimz:\n  - x\nquotez: []\n---\n", encoding="utf-8")
        r = self.run_tool("verify-quotes", root, "01_notes/lit/lei2023financial.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("empty note", r.stdout)

    # round 1: hash strictness
    def hashed_project(self, edit=None, drop_hash=False, manifest_hash="same"):
        root = self.project("lei2023financial")
        md = root / "02_sources/md/lei2023financial.md"
        text = md.read_text(encoding="utf-8")
        h = vq.body_hash(text)
        text = text.replace("method: pdftotext\n", f"method: pdftotext\nmd_sha256: {h}\n", 1) if "md_sha256" not in text else text
        h = vq.body_hash(text)
        if edit:
            text += edit
        if drop_hash:
            text = "".join(l for l in text.splitlines(True) if not l.startswith("md_sha256:"))
        md.write_text(text, encoding="utf-8", newline="\n")
        mh = h if manifest_hash == "same" else manifest_hash
        (root / "02_sources/manifest.csv").write_text(
            f"stem,md_sha256\nlei2023financial,{mh}\n", encoding="utf-8")
        (root / "draft.md").write_text("Lei writes [@lei2023financial, p. 3].\n", encoding="utf-8")
        return root

    def test_strict_hash(self):
        root = self.hashed_project()
        note = "01_notes/lit/lei2023financial.md"
        self.assertEqual(self.run_tool("verify-quotes", root, note).returncode, 0)
        r = subprocess.run([sys.executable, str(BIN / "verify-quotes"), "--strict", note], cwd=root,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # delete the hash field and append a fabricated sentence
        root = self.hashed_project(edit=f"\n{self.F}.\n", drop_hash=True)
        r = subprocess.run([sys.executable, str(BIN / "verify-quotes"), "--strict", note], cwd=root,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("re-run pdf2md", r.stdout)
        self.assertRejected(self.run_tool("check-claims", root, "draft.md"))
        # a hash that does not match the manifest
        root = self.hashed_project(manifest_hash="0" * 64)
        r = subprocess.run([sys.executable, str(BIN / "verify-quotes"), "--strict", note], cwd=root,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("manifest.csv", r.stdout)
        self.assertRejected(self.run_tool("check-claims", root, "draft.md"))


if __name__ == "__main__":
    unittest.main()
