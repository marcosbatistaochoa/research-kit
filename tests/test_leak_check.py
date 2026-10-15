import sys
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "leak-check.sh"
HOME_PATH = "/ho" + "me/x/notes"  # built in pieces so this file is itself clean
IP = "10.1." + "2.3"
EMAIL = "jane@" + "example.org"
PUBLIC_HANDLE = "nik" + "110403"
PUBLIC_URLS = tuple(
    "https://github.com/" + PUBLIC_HANDLE + "/" + repo
    for repo in ("research-kit", "ai-architecture")
)
PUBLIC_DOCS = (
    "README.md",
    "INSTALL.md",
    "CATALOG.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "docs/adapters.md",
    "docs/workflow.md",
)


@unittest.skipIf(sys.platform == "win32", "leak-check.sh needs bash")
class LeakCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.deny = Path(self.tmp.name) / "denylist"
        self.deny.write_text("# comment\n\nSecretProject\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("config", "user.email", "t@users.noreply.github.com")
        self.git("config", "user.name", "t")

    def git(self, *a):
        subprocess.run(["git", *a], cwd=self.repo, check=True, capture_output=True)

    def run_check(self, content, *args, deny=True):
        (self.repo / "f.txt").write_text(content + "\n", encoding="utf-8")
        self.git("add", "f.txt")
        env = dict(
            os.environ,
            RESEARCH_KIT_DENYLIST=str(
                self.deny if deny else self.tmp.name + "/missing"
            ),
        )
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            cwd=self.repo,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

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
        (d / "paper.md").write_text("contact " + EMAIL + "\n", encoding="utf-8")
        self.assertEqual(self.run_check("clean").returncode, 0)
        (d / "paper.md").write_text(
            "contact " + EMAIL + " SecretProject\n", encoding="utf-8"
        )
        self.git("add", "-A")
        self.assertEqual(self.run_check("clean").returncode, 1)

    def test_author_lines_exempt_only_in_metadata(self):
        env = dict(os.environ, RESEARCH_KIT_DENYLIST=str(self.deny))

        def check(name, content):
            (self.repo / name).write_text(content + "\n", encoding="utf-8")
            self.git("add", name)
            r = subprocess.run(
                ["bash", str(SCRIPT)],
                cwd=self.repo,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.git("rm", "-q", "--cached", name)
            return r.returncode

        self.assertEqual(check("LICENSE", "Copyright (c) 2026 SecretProject"), 0)
        self.assertEqual(check("LICENSE", "Thanks to SecretProject"), 1)
        self.assertEqual(check("README.md", "Copyright (c) 2026 SecretProject"), 1)
        self.assertEqual(
            check("README.md", "/plugin marketplace add SecretProject/research-kit"), 0
        )
        self.assertEqual(check("README.md", "see SecretProject/research-kit"), 1)

    def test_banner_footer_default_allowed_on_exact_line_only(self):
        line = '    p.add_argument("--footer", default="secretproject.com")'
        self.deny.write_text("secretproject\n", encoding="utf-8")
        env = dict(os.environ, RESEARCH_KIT_DENYLIST=str(self.deny))
        for name, text, want in (
            ("tools/banner/bin/make-banner", line, 0),
            ("tools/banner/bin/make-banner", line + " # secretproject", 1),
            ("tools/other", line, 1),
        ):
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
            self.git("add", name)
            r = subprocess.run(["bash", str(SCRIPT)], cwd=self.repo, env=env,
                               capture_output=True, text=True)
            self.git("reset", "-q")
            self.assertEqual(r.returncode, want, name + text)

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
        (self.repo / "f.txt").write_text("host " + IP + "\n", encoding="utf-8")
        self.git("add", "f.txt")
        self.git("commit", "-qm", "x")
        (self.repo / "f.txt").write_text("clean\n", encoding="utf-8")
        self.git("commit", "-qam", "y")
        env = dict(os.environ, RESEARCH_KIT_DENYLIST=str(self.deny))
        run = lambda m: subprocess.run(
            ["bash", str(SCRIPT), m],
            cwd=self.repo,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(run("--tree").returncode, 0)
        h = run("--history")
        self.assertEqual(h.returncode, 1)
        self.assertIn("f.txt:1", h.stdout)

    def check_reference(self, name, content, expected, mode="--staged", kind=None):
        self.deny.write_text(PUBLIC_HANDLE + "\nprivatefixtureword\n", encoding="utf-8")
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")
        self.git("add", name)
        env = dict(os.environ, RESEARCH_KIT_DENYLIST=str(self.deny))
        try:
            result = subprocess.run(
                ["bash", str(SCRIPT), mode],
                cwd=self.repo,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            if kind:
                self.assertIn("[" + kind + "]", result.stdout)
        finally:
            self.git("rm", "-q", "--cached", name)
            path.unlink()

    def test_public_doc_exact_urls(self):
        for name in PUBLIC_DOCS:
            for url in PUBLIC_URLS:
                for mode in ("--staged", "--tree"):
                    with self.subTest(name=name, url=url, mode=mode):
                        self.check_reference(
                            name, "[public](" + url + ") " + url, 0, mode
                        )

    def test_public_urls_do_not_hide_other_deny_terms(self):
        for url in PUBLIC_URLS:
            for text in (
                url + " privatefixtureword",
                "PRIVATEFIXTUREWORD " + url,
                url + " " + PUBLIC_HANDLE,
            ):
                with self.subTest(text=text):
                    self.check_reference("README.md", text, 1, kind="denylist")

    def test_public_handle_bare_is_denied(self):
        for name in PUBLIC_DOCS:
            with self.subTest(name=name):
                self.check_reference(name, PUBLIC_HANDLE, 1, kind="denylist")

    def test_public_url_lookalikes_are_denied(self):
        for url in PUBLIC_URLS:
            for suffix in ("-private", "ten", ".git", "_private", "/private"):
                with self.subTest(url=url, suffix=suffix):
                    self.check_reference("README.md", url + suffix, 1, kind="denylist")
            self.check_reference("README.md", "x" + url, 1, kind="denylist")

    def test_public_urls_unexpected_files_are_denied(self):
        for name in ("other.md", "nested/README.md", "docs/other.md"):
            for url in PUBLIC_URLS:
                with self.subTest(name=name, url=url):
                    self.check_reference(name, url, 1, kind="denylist")

    def test_public_urls_keep_other_layers(self):
        for url in PUBLIC_URLS:
            for value, kind in (
                (HOME_PATH, "home-path"),
                (EMAIL, "email"),
                (IP, "ipv4"),
            ):
                with self.subTest(url=url, kind=kind):
                    self.check_reference("INSTALL.md", url + " " + value, 1, kind=kind)

    def test_install_exact_marketplace_command(self):
        command = "/plugin marketplace add " + PUBLIC_HANDLE + "/research-kit"
        self.check_reference("INSTALL.md", command, 0)
        self.check_reference(
            "INSTALL.md", command + " privatefixtureword", 1, kind="denylist"
        )
        self.check_reference(
            "INSTALL.md",
            command.replace(PUBLIC_HANDLE, "privatefixtureword"),
            1,
            kind="denylist",
        )
        self.check_reference("CATALOG.md", command, 1, kind="denylist")


if __name__ == "__main__":
    unittest.main()
