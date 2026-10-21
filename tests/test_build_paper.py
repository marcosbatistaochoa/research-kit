import sys
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "plugins/research-kit/bin/build-paper"
TEMPLATE = ROOT / "plugins/research-kit/templates/project"

BIB = "@article{a2020x, author={Doe, Jane}, title={Title}, journal={J}, year={2020}}\n"


@unittest.skipUnless(shutil.which("pandoc"), "pandoc not installed")
class BuildPaper(unittest.TestCase):
    def project(self, paper):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        root = Path(t.name) / "p"
        shutil.copytree(TEMPLATE, root)
        (root / "07_references/references.bib").write_text(BIB, encoding="utf-8")
        if paper is not None:
            (root / "10_paper/paper.md").write_text(paper, encoding="utf-8")
        return root

    def build(self, root, *args):
        return subprocess.run(
            [sys.executable, str(TOOL), *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def out(self, root):
        return list((root / "10_paper").glob("paper.pdf")) + list(
            (root / "10_paper").glob("paper.html")
        )

    def test_good_build(self):
        root = self.project("# Intro\n\nAs shown by @a2020x.\n")
        r = self.build(root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(self.out(root))
        self.assertIn("pandoc:", r.stdout)

    def test_template_builds(self):
        r = self.build(self.project(None))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_unresolved_citation_fails(self):
        r = self.build(self.project("# Intro\n\nSee [@ghost].\n"))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("unresolved citations", r.stderr)

    def test_triple_question_marks_fail(self):
        r = self.build(self.project("# Intro\n\nTODO ??? here.\n"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("???", r.stderr)

    def test_missing_image_fails_and_soft_passes(self):
        root = self.project("# Intro\n\n![fig](../05_figures/nope.png)\n")
        self.assertEqual(self.build(root).returncode, 1)
        self.assertEqual(self.build(root, "--soft").returncode, 0)

    def test_requested_html_and_docx_are_not_mislabeled(self):
        root = self.project("# Intro\n\nAs shown by @a2020x.\n")
        self.assertEqual(self.build(root, "--to", "html").returncode, 0)
        self.assertTrue((root / "10_paper/paper.html").is_file())
        self.assertEqual(self.build(root, "--to", "docx").returncode, 0)
        self.assertTrue((root / "10_paper/paper.docx").is_file())


if __name__ == "__main__":
    unittest.main()
