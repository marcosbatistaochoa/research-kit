---
name: research-kit
description: Source-grounded research workflows with installed, local Python helpers.
---

# research-kit for Codex

This skill is self-contained. Its installed directory is
`<project>/.agents/skills/research-kit`. In shell examples, set `researchKit` to
that directory. Its `bin/` and `templates/` directories must remain siblings.
Use actual quoted paths, never bare helper names or `CLAUDE_PLUGIN_ROOT`.

Use `$research-kit` only as the Codex skill trigger, not as a shell variable. In a
POSIX shell, for example, set `researchKit="/absolute/path/to/.agents/skills/research-kit"`.
In PowerShell, set `$researchKit = "C:\absolute\path\to\.agents\skills\research-kit"`.

On macOS/Linux use `python3 "$researchKit/bin/verify-quotes" ...`. In PowerShell
use `& python "$researchKit\bin\verify-quotes" ...` (or `& py -3` if `python` is not
available). The copied workflows in `workflows/` and role contracts in `agents/`
are instructions, not imported permissions. If independent roles are unavailable,
run their steps serially and label the result non-independent.

Useful local checks:

```text
python3 "$researchKit/bin/verify-quotes" --strict 01_notes/lit/*.md
python3 "$researchKit/bin/check-claims" --root . 10_paper/paper.md
python3 "$researchKit/bin/build-paper" --to html
```

On PowerShell, pass explicit note paths instead of relying on shell glob expansion:

```powershell
& python "$researchKit\bin\verify-quotes" --strict 01_notes/lit/example.md
& python "$researchKit\bin\build-paper" --to html
```

`build-paper --grounding` runs local quote and citation checks, but it is not proof
of a complete draft. Canonical workflow command examples use the installed helper
paths above; consult the copied `workflows/` folders for their full assets.
