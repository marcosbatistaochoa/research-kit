import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "plugins/research-kit/bin/check-claims"

OK_NOTE = '---\ncitekey: {k}\nclaims:\n  - "A claim."\nquotes: []\n---\nbody\n'
QUOTE_NOTE = '---\ncitekey: {k}\nclaims: []\nquotes:\n  - page: 1\n    text: "Q."\n---\n'
THIN_NOTE = '---\ncitekey: {k}\nclaims: []\nquotes: []\n---\nbody\n'


class CheckClaims(unittest.TestCase):
    def run_draft(self, draft, notes):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "01_notes/lit").mkdir(parents=True)
            for k, body in notes.items():
                (root / f"01_notes/lit/{k}.md").write_text(body.format(k=k), encoding="utf-8")
            (root / "10_draft.md").write_text(draft, encoding="utf-8")
            return subprocess.run([sys.executable, str(TOOL), str(root / "10_draft.md")],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace")

    def row(self, r, key):
        return next(l for l in r.stdout.splitlines() if f"| {key} |" in l)

    def test_multiple_keys(self):
        r = self.run_draft("Money evolved [@a; @b, p. 12]. Prices rise [@c].\n",
                           {"a": OK_NOTE, "b": QUOTE_NOTE, "c": OK_NOTE})
        self.assertEqual(r.returncode, 0, r.stdout)
        for k in "abc":
            self.assertIn("OK", self.row(r, k))
        self.assertIn("2 cited sentence(s)", r.stdout)

    def test_missing_note(self):
        r = self.run_draft("Claim one [@a]. Claim two [@ghost].\n", {"a": OK_NOTE})
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNSUPPORTED", self.row(r, "ghost"))
        self.assertIn("OK", self.row(r, "a"))

    def test_thin_note(self):
        r = self.run_draft("A claim [@thin].\n", {"thin": THIN_NOTE})
        self.assertEqual(r.returncode, 1)
        self.assertIn("THIN", self.row(r, "thin"))

    def test_uncited_sentences_ignored_and_period_in_locator(self):
        r = self.run_draft("No citation here. Cited [@a, p. 3]. Also none.\n", {"a": OK_NOTE})
        self.assertEqual(r.returncode, 0)
        self.assertIn("1 cited sentence(s)", r.stdout)

    def test_usage(self):
        r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
