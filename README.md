# research-kit

A Claude Code plugin for source-grounded research: search the literature, convert PDFs to
page-marked markdown, write notes whose quotes are verified verbatim against the source, review a
draft against those notes, and build the paper. It also scaffolds a reproducible analysis pipeline
(Python or R). Early stage (0.1.0). The stages and the files that flow between them are in
[docs/workflow.md](docs/workflow.md).

## Take what you need

Every piece works on its own. Tools are single files: copy one onto your PATH (`chmod +x`), and
`<tool> --help` prints usage and dependencies. All tools need python3 >= 3.9 (stdlib only) unless
noted; `build-paper` is a POSIX shell script.

| Stage | Component (path) | Problem it fixes | Standalone use |
|---|---|---|---|
| scaffold | `plugins/research-kit/bin/new-project` | Every project starts with a different folder layout | Copy `bin/new-project` and `templates/project/` side by side (it finds the template next to itself); run `new-project my-paper` |
| scaffold | `skills/new-research-project` | Asking Claude to start a project | Copy the folder into `.claude/skills/`; needs `new-project` on PATH |
| search | `bin/lit-search` | Searching two indexes, deduping, ranking, spotting retracted papers, getting BibTeX | Copy onto PATH; needs internet (OpenAlex, Semantic Scholar, doi.org), no API keys |
| search | `skills/literature-search` | Running that search as a repeatable, receipted step | Copy into `.claude/skills/`; needs `lit-search` |
| convert | `bin/pdf2md` | PDFs are expensive to read and cannot be quoted by page | Copy onto PATH; needs `pdftotext` (poppler); optional `ocrmypdf` (scans), `qpdf` (encrypted PDFs), `docling` |
| convert | `skills/pdf-to-markdown` | Choosing between text extraction and OCR | Copy into `.claude/skills/`; needs `pdf2md` |
| notes | `agents/source-reader.md` | One agent reads one source and returns a note with page-pinned quotes | Copy into your project's `.claude/agents/`; read-only tools (Read, Grep, Glob) |
| notes | `bin/verify-quotes` | Invented or misquoted quotes in notes | Copy onto PATH; checks notes against source markdown with `<!-- page N -->` markers |
| notes | `skills/literature-notes` (with `template.md`) | A consistent note format with claims and quotes | Copy the folder into `.claude/skills/`; needs `verify-quotes` |
| review | `bin/check-claims` | Cited sentences with no supporting note | Copy onto PATH; expects `01_notes/lit/<citekey>.md` |
| review | `bin/check-bib` | Duplicate keys, missing fields, bad DOIs, cited-but-missing keys | Copy onto PATH |
| review | `agents/claim-checker.md` | Does the note really support the cited sentence | Copy into `.claude/agents/`; read-only |
| review | `agents/skeptic.md` | Nobody tries to refute the draft's key claims | Copy into `.claude/agents/`; read-only |
| review | `skills/review-against-notes` | Ordering: mechanical checks, then judgment, then adversary | Copy into `.claude/skills/`; needs the two tools and two agents above |
| build | `bin/build-paper` | Silent unresolved citations and missing figures in the build | Copy onto PATH; needs `pandoc`; optional `xelatex` (PDF, otherwise HTML) |
| build | `skills/paper-build` | Compile plus bibliography check in one step | Copy into `.claude/skills/`; needs `build-paper`, `check-bib` |
| analysis | `bin/new-pipeline` | Ad-hoc analysis scripts that cannot be rerun | Copy `bin/new-pipeline` and `templates/pipeline/` side by side; `new-pipeline dir --lang python\|r`; R variant needs R |
| analysis | `agents/pipeline-runner.md` | Running a pipeline and reporting results; it never edits your code (the pipeline itself writes `output/`) | Copy into `.claude/agents/`; needs python3 (or R); it runs project code, so trust the pipeline |
| analysis | `skills/analysis-pipeline` | Conventions: frozen raw data, stable outputs, one command | Copy into `.claude/skills/`; needs `new-pipeline` |

Skills call tools by bare name; if a tool is not on PATH, run it from `plugins/research-kit/bin/`.

## Full install

```
/plugin marketplace add nik110403/research-kit
/plugin install research-kit@research-kit
```

Then ask Claude to start a new research project (skill `new-research-project`).

## Quickstart: the quote check

`examples/basic` holds two open-access papers, their conversions and notes
(see [examples/basic/RUN.md](examples/basic/RUN.md) for the full walk-through). From the repo root:

```sh
plugins/research-kit/bin/pdf2md examples/basic/02_sources/pdf/*.pdf --out /tmp/md-demo   # needs pdftotext
cd examples/basic
../../plugins/research-kit/bin/verify-quotes 01_notes/lit/*.md        # 14 of 14 PASS, exit 0
../../plugins/research-kit/bin/verify-quotes 01_notes/negative/*.md   # fabricated quote: FAIL, exit 1
```

`make check` runs the test suite, plugin validation (if the `claude` CLI is present), the
example quote check and the leak gate.

## Contributing

Enable the leak gate with `git config core.hooksPath .githooks`. It blocks home paths, IPs, personal
emails and terms from your private denylist (`$RESEARCH_KIT_DENYLIST`); run `scripts/leak-check.sh --history` for a full scan.
