# Using the collection with other assistants

The native packaged route is the Claude Code plugin: seven skills and four
Claude-format roles. The command-line tools also run without any assistant.
For another assistant, distinguish **manual workflow adaptation** from **native
skill discovery**. Neither imports Claude's agent permissions automatically.

## Manual workflow and role adaptation

1. Choose a stage from the [catalog](../CATALOG.md). Read its `SKILL.md`, support
   assets and required role contracts from `plugins/research-kit/`.
2. Give the assistant the actual project paths and absolute tool paths. Translate
   commands to the available terminal interface; run them from the research
   project root, or from the pipeline directory for `run_all.py` / `run_all.R`.
3. For source reading and review, preserve read-only roles, untrusted-source
   treatment, honest reading scope, evidence anchors and the returned-text
   contract. The main session saves notes/reports and runs mechanical checks.
4. If using `AGENTS.md` for project guidance, merge only the selected workflow
   rules into the existing file after reviewing it. Do not overwrite permissions
   or translate a Claude `tools:` front matter line into an assumed native API.

When no role-dispatch mechanism is available, a person can run separate reading
and review tasks using those contracts. Label this manual adaptation; do not
claim native agents or independently enforced read-only access. `pipeline-runner`
requires shell execution, and the pipeline may write outputs even though the
role itself does not edit code. Only execute trusted project code.

## Optional native skill discovery

These are documented discovery paths, not tested integrations of this collection:

| Assistant | Documented path | Source and evidence scope |
|---|---|---|
| OpenCode | Project `.opencode/skills/<name>/SKILL.md`; documented `.claude/skills/` and `.agents/skills/` equivalents also exist | [Official skills documentation](https://opencode.ai/docs/skills/) |
| Codex | `.agents/skills/`; scans from the current directory up to the repository root | [Official skills documentation](https://developers.openai.com/codex/skills/) (redirected to the current build-skills documentation during preparation) |

The preparation review observed these official sources on **2026-10-14**.
This document records those supplied observations; this documentation pass did
not independently retrieve the pages or test native discovery. Recheck current
documentation before relying on a path in a different version.

Copy the **whole chosen skill folder**, including assets such as
`literature-notes/template.md`, to the selected supported discovery directory.
Discovery makes instructions available; it does not install bare-name helper
commands, support templates or role implementations. Review each skill's Claude
delegation steps and adapt them explicitly before execution.

## Dependencies survive adaptation

- Skills invoke helpers by bare name. Make the kit's `bin/` available on PATH
  to the assistant's shell, or supply absolute paths and use `python3` for Python
  helpers / `sh` for `build-paper`. Do not assume the plugin cache is on PATH.
- `new-project` and `new-pipeline` need `templates/` as a **sibling of `bin/`**.
  Moving only a script breaks its template lookup.
- Notes require the local note template, `source-reader` contract and
  `verify-quotes`. Review requires `verify-quotes`, `check-claims`,
  `claim-checker` and `skeptic`. `check-bib` remains a separate useful check.
- Agent `.md` formats, model names and permission declarations are not universally
  imported. Configure equivalent capabilities in the host assistant according to
  its documentation; otherwise use the contracts manually and disclose the gap.

The [install guide](../INSTALL.md) gives tool/dependency details. No native
non-Claude compatibility, full Windows support or performance result follows
from these path observations.
