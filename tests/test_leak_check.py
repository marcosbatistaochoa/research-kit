import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "leak-check.sh"
HOME_PATH = "/ho" + "me/x/notes"  # built in pieces so this file is itself clean
IP = "10.1." + "2.3"
EMAIL = "jane@" + "example.org"


class LeakCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.deny = Path(self.tmp.name) / "denylist"
        self.deny.write_text("# comment\n\nSecretProject\n")
        self.git("init", "-q")
        self.git("config", "user.email", "t@users.noreply.github.com")
        self.git("config", "user.name", "t")

    def git(self, *a):
        subprocess.run(["git", *a], cwd=self.repo, check=True, capture_output=True)

    def run_check(self, content, *args, deny=True):
        (self.repo / "f.txt").write_text(content + "\n")
        self.git("add", "f.txt")
        env = dict(os.environ, RESEARCH_KIT_DENYLIST=str(self.deny if deny else self.tmp.name + "/missing"))
        return subprocess.run(["bash", str(SCRIPT), *args], cwd=self.repo, env=env, capture_output=True, text=True)

    def test_home_path(self):
        r = self.run_check("see " + HOME_PATH)
        self.assertEqual(r.returncode, 1)
        self.assertIn("f.txt:1", r.stdout)

    def test_ip(self):
        self.assertEqual(self.run_check("host " + IP + " here").returncode, 1)

    def test_loopback_and_version_ok(self):
        self.assertEqual(self.run_check("127.0.0.1 0.0.0.0 v1.2.3.4").returncode, 0)

    def test_personal_email(self):
        self.assertEqual(self.run_check("mail " + EMAIL).returncode, 1)

    def test_source_md_email_exempt_but_denylist_not(self):
        d = self.repo / "02_sources" / "md"
        d.mkdir(parents=True)
        (d / "paper.md").write_text("contact " + EMAIL + "\n")
        self.assertEqual(self.run_check("clean").returncode, 0)
        (d / "paper.md").write_text("contact " + EMAIL + " SecretProject\n")
        self.git("add", "-A")
        self.assertEqual(self.run_check("clean").returncode, 1)

    def test_author_lines_exempt_only_in_metadata(self):
        env = dict(os.environ, RESEARCH_KIT_DENYLIST=str(self.deny))
        def check(name, content):
            (self.repo / name).write_text(content + "\n")
            self.git("add", name)
            r = subprocess.run(["bash", str(SCRIPT)], cwd=self.repo, env=env, capture_output=True, text=True)
            self.git("rm", "-q", "--cached", name)
            return r.returncode
        self.assertEqual(check("LICENSE", "Copyright (c) 2026 SecretProject"), 0)
        self.assertEqual(check("LICENSE", "Thanks to SecretProject"), 1)
        self.assertEqual(check("README.md", "Copyright (c) 2026 SecretProject"), 1)
        self.assertEqual(check("README.md", "/plugin marketplace add SecretProject/research-kit"), 0)
        self.assertEqual(check("README.md", "see SecretProject/research-kit"), 1)

    def test_denylist_case_insensitive(self):
        self.assertEqual(self.run_check("about SECRETPROJECT today").returncode, 1)

    def test_noreply_ok(self):
        r = self.run_check("12345+u@users.noreply.github.com and noreply@example.org")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_clean_ok(self):
        self.assertEqual(self.run_check("nothing here").returncode, 0)

    def test_missing_denylist_still_runs(self):
        r = self.run_check("clean", deny=False)
        self.assertEqual(r.returncode, 0)
        self.assertIn("skipping denylist", r.stderr)
        self.assertEqual(self.run_check(EMAIL, deny=False).returncode, 1)

    def test_tree_and_history(self):
        (self.repo / "f.txt").write_text("host " + IP + "\n")
        self.git("add", "f.txt")
        self.git("commit", "-qm", "x")
        (self.repo / "f.txt").write_text("clean\n")
        self.git("commit", "-qam", "y")
        env = dict(os.environ, RESEARCH_KIT_DENYLIST=str(self.deny))
        run = lambda m: subprocess.run(["bash", str(SCRIPT), m], cwd=self.repo, env=env, capture_output=True, text=True)
        self.assertEqual(run("--tree").returncode, 0)
        h = run("--history")
        self.assertEqual(h.returncode, 1)
        self.assertIn("f.txt:1", h.stdout)


if __name__ == "__main__":
    unittest.main()
