import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "plugins/research-kit/bin/verify-quotes"

SOURCE = """---
title: Test
---
<!-- page 1 -->
Money is a social
convention that evolved over many cen-
turies of trade.

<!-- page 2 -->
Inflation   is always and everywhere
a monetary phenomenon.
"""


def note(quotes, source="02_sources/md/a.md"):
    items = "".join(f'  - page: {p}\n    text: "{t}"\n' for p, t in quotes)
    return (f'---\ncitekey: a\nsource_md: {source}\nread_scope: full_text\n'
            f'claims: []\nquotes:\n{items}---\nbody\n')


class VerifyQuotes(unittest.TestCase):
    def run_note(self, quotes, source_text=SOURCE, source_ref="02_sources/md/a.md"):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            if source_text is not None:
                (root / "02_sources/md").mkdir(parents=True)
                (root / "02_sources/md/a.md").write_text(source_text, encoding="utf-8")
            (root / "01_notes/lit").mkdir(parents=True)
            n = root / "01_notes/lit/a.md"
            n.write_text(note(quotes, source_ref), encoding="utf-8")
            return subprocess.run([sys.executable, str(TOOL), str(n)],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_exact_match(self):
        r = self.run_note([(2, "a monetary phenomenon")])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("PASS", r.stdout)

    def test_whitespace_and_linebreak(self):
        r = self.run_note([(2, "Inflation is always and everywhere a monetary phenomenon.")])
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_hyphenation(self):
        r = self.run_note([(1, "evolved over many centuries of trade")])
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_wrong_page(self):
        r = self.run_note([(1, "a monetary phenomenon")])
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL", r.stdout)
        self.assertIn("different page", r.stdout)

    def test_fabricated(self):
        r = self.run_note([(1, "Money was invented by aliens")])
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL", r.stdout)

    def test_missing_source(self):
        r = self.run_note([(1, "Money is a social")], source_text=None)
        self.assertEqual(r.returncode, 1)
        self.assertIn("source_md not found", r.stdout)

    def test_any_fail_fails_all(self):
        r = self.run_note([(1, "Money is a social"), (1, "nonsense text")])
        self.assertEqual(r.returncode, 1)
        self.assertIn("PASS", r.stdout)
        self.assertIn("FAIL", r.stdout)

    def test_usage(self):
        r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
