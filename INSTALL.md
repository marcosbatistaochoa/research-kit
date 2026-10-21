# Installation: whole collection or selected parts

## Whole Claude Code plugin

In Claude Code, add the public marketplace and install its plugin:

```text
/plugin marketplace add nik110403/research-kit
/plugin install research-kit@research-kit
```

This loads the packaged seven skills and four roles from the canonical
`plugins/research-kit/` tree. It does not install Python, Poppler, pandoc, R or
optional dependencies. Do not replace your existing settings, `CLAUDE.md`,
`AGENTS.md` or permission policy with this collection's examples.

For predictable command paths, keep a checkout of
[research-kit](https://github.com/nik110403/research-kit). In a POSIX shell **at
the checkout root**, set:

```sh
KIT="$(pwd)/plugins/research-kit"
```

`KIT` below must remain an absolute path. Run `python3 "$KIT/bin/verify-quotes"
--help` to confirm the Python helper can launch. The plugin's instructions use
bare tool names: either add this directory for the current shell with
`export PATH="$KIT/bin:$PATH"` (and ensure executable permission), or explicitly
give your assistant the absolute tool path. A Markdown skill is not a PATH setup
mechanism; changing directories alone will not resolve a bare command.

## Selective skills and roles

Choose dependencies from [CATALOG.md](CATALOG.md). Copy **the full skill folder**
into your project's `.claude/skills/`, not just `SKILL.md`. For example, from the
checkout root, after confirming `PROJECT` points to your intended project:

```sh
PROJECT="/absolute/path/to/your-project"
mkdir -p "$PROJECT/.claude/skills"
cp -R "$KIT/skills/literature-notes" "$PROJECT/.claude/skills/"
```

Before copying, inspect the destination: if that skill already exists, back it
up and reconcile changes rather than nesting or overwriting it blindly. Notes
also need `template.md`, the `source-reader` role and `verify-quotes`.

For Claude roles, copy selected `.md` files to your project's `.claude/agents/`
under the same names, with the same collision precautions. For example:

```sh
mkdir -p "$PROJECT/.claude/agents"
cp "$KIT/agents/source-reader.md" "$PROJECT/.claude/agents/"
```

Alternatively, read a role as a manual contract and provide its task to an
assistant; that does not create a native agent or enforce permissions. Review
needs `claim-checker` and `skeptic` as well as `verify-quotes` and `check-claims`.
Analysis needs `pipeline-runner`; running project code is a separate trust decision.

## Selective tools and templates

Python helpers, including `build-paper`, run with `python3` and an absolute file
path, without PATH or executable permissions. On Windows PowerShell use `python`
(or `py -3`) and a quoted absolute path.

Most helpers can be copied alone, except that `check-claims` needs `verify-quotes` in the same folder. **The two scaffold tools cannot:** retain this
layout wherever you put them, selecting only the needed template subtree:

```text
chosen-kit/
  bin/new-project
  bin/new-pipeline
  templates/project/          # needed by new-project
  templates/pipeline/python/  # needed for --lang python
  templates/pipeline/r/       # needed for --lang r
```

`templates/` is a sibling of `bin/`, not inside it. Keep the entire selected
template subtree. Do not flatten the scaffold scripts into an unrelated PATH
directory without those templates.

### Run commands from the right directory

With `KIT` set above, switch your shell to the research **project root** before
using defaults for notes, bibliography, search output and `10_paper/`:

```sh
python3 "$KIT/bin/lit-search" "your research question" --since 2015 --n 25
python3 "$KIT/bin/pdf2md" 02_sources/pdf/*.pdf --out 02_sources/md/
python3 "$KIT/bin/verify-quotes" 01_notes/lit/*.md
python3 "$KIT/bin/check-docx" --root /absolute/path/to/project --inventory /absolute/path/to/new-word-quotes.csv /absolute/path/to/lecture.docx
python3 "$KIT/bin/check-claims" 10_paper/paper.md
python3 "$KIT/bin/check-bib"
python3 "$KIT/bin/build-paper" --to pdf
```

Each line is an independent stage; run only what you selected. Search writes
files and uses network; conversion writes a manifest and source Markdown;
build writes an artifact/log. Checking quotes, claims and bibliography is offline.
Keep note `source_md` paths relative to the research project root.

Scaffolding takes explicit targets and refuses nonempty ones:

```sh
python3 "$KIT/bin/new-project" /absolute/path/to/new-paper
python3 "$KIT/bin/new-pipeline" /absolute/path/to/new-pipeline --lang python
```

Run the generated pipeline **from its own directory** using `python3 run_all.py`
(or `uv run python run_all.py`), or `Rscript run_all.R` for the R variant.
The generated project instructions are a starting point for a new project,
not a replacement for instructions in an existing one.

## Platform and dependency checklist

Python 3.9+ covers the eight helpers. `pdf2md` additionally needs `pdftotext`
from Poppler; optional `ocrmypdf` handles scans and `qpdf` encrypted PDFs. Docling was removed in 0.1.3: `pdf2md --engine docling` is refused
because its output is one block marked page 1, which breaks page pinning. Search uses OpenAlex, Semantic Scholar and doi.org.
Set an optional `SEMANTIC_SCHOLAR_API_KEY` in the process environment, never
in tracked files; without a key Semantic Scholar often returns 429/403.
Inspect receipts for partial provider coverage. `LIT_SEARCH_MAILTO` is optional.

`build-paper` needs Python 3.9+ and pandoc on PATH. It prefers Typst then XeLaTeX
for PDF, and explicitly writes HTML if neither engine exists; use `--to html` or
`--to docx` to select a format. On Windows PowerShell, for example:

```powershell
$researchKit = (Resolve-Path .\plugins\research-kit)
python "$researchKit\bin\verify-quotes" --strict 01_notes/lit/lei2023financial.md
python "$researchKit\bin\build-paper" --to html
```

### Codex adapter

Install one self-contained Codex skill into an existing project; it does not alter
`AGENTS.md`, global configuration, or the Claude plugin:

```sh
python3 scripts/install-codex.py --project /absolute/path/to/project
```

```powershell
python .\scripts\install-codex.py --project C:\path\to\project
```

The installed skill is `.agents/skills/research-kit/`. Set `$researchKit` to that
path when prompting Codex to run a clean quote demo. R and any analysis packages belong to the chosen
pipeline environment; `uv` and `renv` are optional environment-management tools.

Try the [offline quote check](README.md) before adding network or build
dependencies. Other-assistant adaptation is described in [docs/adapters.md](docs/adapters.md).
