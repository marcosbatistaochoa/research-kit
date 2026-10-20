"""Bypass corpus: each case is a known way to get a fabricated or unlinked quote past the tools.

Every bypass test asserts the SECURE behaviour (non-zero exit / FAIL / UNVERIFIED).
Controls (genuine quotes) must keep passing.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "plugins/research-kit/bin"
FIX = Path(__file__).resolve().parent / "fixtures/bypass"
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


if __name__ == "__main__":
    unittest.main()
