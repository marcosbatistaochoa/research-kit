import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "plugins/research-kit/bin/check-claims"

SOURCE = """---
source: {k}.pdf
---
<!-- page 1 -->
Money is a social convention that evolved over many centuries of trade.
Prices rise. Inflation is always and everywhere a monetary phenomenon.
"""
OK_NOTE = ('---\ncitekey: {k}\nsource_md: 02_sources/md/{k}.md\nclaims:\n  - "A claim."\nquotes:\n'
           '  - page: 1\n    text: "Money is a social convention that evolved over many centuries"\n---\nbody\n')
CLAIMS_ONLY = '---\ncitekey: {k}\nsource_md: 02_sources/md/{k}.md\nclaims:\n  - "A claim."\nquotes: []\n---\nbody\n'
EMPTY_NOTE = '---\ncitekey: {k}\nclaims: []\nquotes: []\n---\nbody\n'
BAD_QUOTE = OK_NOTE.replace("evolved over many centuries", "invented by aliens in space")


class CheckClaims(unittest.TestCase):
    def run_draft(self, draft, notes):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "01_notes/lit").mkdir(parents=True)
            (root / "02_sources/md").mkdir(parents=True)
            for k, body in notes.items():
                (root / f"01_notes/lit/{k}.md").write_text(body.format(k=k), encoding="utf-8")
                (root / f"02_sources/md/{k}.md").write_text(SOURCE.format(k=k), encoding="utf-8")
            (root / "10_draft.md").write_text(draft, encoding="utf-8")
            return subprocess.run([sys.executable, str(TOOL), str(root / "10_draft.md")],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace")

    def row(self, r, key):
        return next(l for l in r.stdout.splitlines() if f"| {key} |" in l)

    def test_multiple_keys(self):
        r = self.run_draft("Money evolved [@a; @b, p. 12]. Prices rise [@c].\n",
                           {"a": OK_NOTE, "b": OK_NOTE, "c": OK_NOTE})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for k in "abc":
            self.assertIn("| OK |", self.row(r, k))
        self.assertIn("2 cited sentence(s)", r.stdout)

    def test_missing_note_is_unverified(self):
        r = self.run_draft("Claim one [@a]. Claim two [@ghost].\n", {"a": OK_NOTE})
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNVERIFIED", self.row(r, "ghost"))
        self.assertIn("| OK |", self.row(r, "a"))

    def test_claims_only_note_is_unverified(self):
        r = self.run_draft("A claim [@a].\n", {"a": CLAIMS_ONLY})
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNVERIFIED", self.row(r, "a"))

    def test_empty_note_is_unverified(self):
        r = self.run_draft("A claim [@a].\n", {"a": EMPTY_NOTE})
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNVERIFIED", self.row(r, "a"))

    def test_failing_quote_is_unverified(self):
        r = self.run_draft("A claim [@a].\n", {"a": BAD_QUOTE})
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNVERIFIED", self.row(r, "a"))

    def test_narrative_key_recognised(self):
        r = self.run_draft("As @a argues, money evolved.\n", {"a": OK_NOTE})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("| OK |", self.row(r, "a"))
        r = self.run_draft("As @ghost argues, money evolved.\n", {"a": OK_NOTE})
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNVERIFIED", self.row(r, "ghost"))

    def test_draft_quote_must_be_in_source(self):
        r = self.run_draft('Money is "a social convention that evolved" [@a].\n', {"a": OK_NOTE})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = self.run_draft('Money is \u201ca social convention that never evolved\u201d [@a].\n', {"a": OK_NOTE})
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNVERIFIED", self.row(r, "a"))
        self.assertIn("never evolved", r.stdout)

    def test_period_inside_draft_quote_does_not_split(self):
        r = self.run_draft('The text says "Prices rise. Inflation is always" [@a].\n', {"a": OK_NOTE})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("1 cited sentence(s)", r.stdout)

    def test_zero_citations_fails(self):
        r = self.run_draft("No citation here at all.\n", {"a": OK_NOTE})
        self.assertEqual(r.returncode, 1)

    def test_uncited_sentences_ignored_and_period_in_locator(self):
        r = self.run_draft("No citation here. Cited [@a, p. 3]. Also none.\n", {"a": OK_NOTE})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("1 cited sentence(s)", r.stdout)

    def test_usage(self):
        r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
