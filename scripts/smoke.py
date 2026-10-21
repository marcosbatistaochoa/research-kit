#!/usr/bin/env python3
"""Run a portable smoke test against a fresh copy of the bundled example."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PYTHON = "python" if sys.platform == "win32" else "python3"


def run(tool, *args, cwd):
    launcher = [PYTHON] if sys.platform != "win32" else [PYTHON]
    result = subprocess.run(
        [*launcher, str(ROOT / "plugins/research-kit/bin" / tool), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise SystemExit(result.stdout + result.stderr)
    return result


def main():
    if not shutil.which("pandoc") or not shutil.which("pdftotext"):
        raise SystemExit("smoke: pandoc and pdftotext are required")
    with tempfile.TemporaryDirectory() as temp:
        example = Path(temp) / "basic"
        shutil.copytree(ROOT / "examples/basic", example)
        paper_dir = example / "10_paper"
        paper_dir.mkdir(exist_ok=True)
        (paper_dir / "paper.md").write_text("# Smoke test\n", encoding="utf-8")
        verified = run(
            "verify-quotes", "--strict", "01_notes/lit/lei2023financial.md", cwd=example
        )
        if "PASS" not in verified.stdout:
            raise SystemExit("smoke: known-good quote did not pass")
        run("build-paper", "--to", "html", cwd=example)
        if not (paper_dir / "paper.html").is_file():
            raise SystemExit("smoke: HTML build was not created")
    print("smoke: PASS")


if __name__ == "__main__":
    main()
