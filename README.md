# research-kit

Turn a reading list into source-grounded notes, check a draft against those notes,
and build a paper. Start with the offline quote check below: it checks 14 real
quotations and rejects a planted fabrication without a model or network connection.

This is a collection of **7 skills, 4 agent roles, 8 command-line tools and project,
Python and R templates**. Install the whole Claude Code plugin or take the parts
you need. The skills and roles are Markdown instructions; the helpers are seven
Python programs and one POSIX shell script. Reading a skill does not execute a tool.

**Status:** early-stage plugin **0.1.1**. This documentation candidate is staged;
it does not announce a new release or an already-published collection update.

## Install the whole collection in Claude Code

In Claude Code:

```text
/plugin marketplace add nik110403/research-kit
/plugin install research-kit@research-kit
```

Then ask it to start a research project, search the literature, or verify notes.
The plugin packages all seven skills and four roles. Command-line dependencies
still need to be available; see [INSTALL.md](INSTALL.md) for tool paths, selective
installation and existing-settings precautions.

## Try it offline first

Download or clone the public [research-kit repository](https://github.com/nik110403/research-kit).
With Python 3.9+ installed, run from its root:

```sh
cd examples/basic
python3 ../../plugins/research-kit/bin/verify-quotes 01_notes/lit/*.md
python3 ../../plugins/research-kit/bin/verify-quotes 01_notes/negative/*.md
```

The first command should print **14 of 14 PASS** and exit 0. The second should
report the fabricated quotation as **FAIL** and exit 1; that failure is expected.
The source conversions are bundled, so this check needs neither PDF software nor
an API key. See the [example walkthrough](examples/basic/RUN.md) and
[source attribution](examples/basic/SOURCES.md). Quote matching checks converted
text and page markers, not whether a claim follows from the quotation.

## Take only what you need

| Want to… | Start here |
|---|---|
| Check quotations without an assistant | [verify-quotes](plugins/research-kit/bin/verify-quotes) |
| Search and save a reading list | [lit-search](plugins/research-kit/bin/lit-search), [literature-search](plugins/research-kit/skills/literature-search/SKILL.md) |
| Read a source into a structured note | [literature-notes](plugins/research-kit/skills/literature-notes/SKILL.md), [source-reader](plugins/research-kit/agents/source-reader.md) |
| Review a draft against notes | [review-against-notes](plugins/research-kit/skills/review-against-notes/SKILL.md) |
| Start a repeatable analysis | [analysis-pipeline](plugins/research-kit/skills/analysis-pipeline/SKILL.md), [pipeline templates](plugins/research-kit/templates/pipeline/) |

The [complete catalog](CATALOG.md) lists every component's inputs, outputs and
dependencies. The [workflow](docs/workflow.md) shows how files connect; the
[adapter guide](docs/adapters.md) covers manual use with other assistants.

## Dependencies and limits

- Python helpers require Python 3.9+ and use the standard library, except the
  optional Docling conversion backend. Search needs internet access. Semantic
  Scholar can reject keyless requests; an optional `SEMANTIC_SCHOLAR_API_KEY`
  helps, and receipts report provider failures and partial coverage.
- PDF conversion needs Poppler's `pdftotext`; scans may need `ocrmypdf`, encrypted
  files `qpdf`. Docling currently emits one block marked page 1, not original PDF
  pagination. Recheck page pins against the PDF.
- Paper builds need POSIX `sh` and pandoc; XeLaTeX enables PDF output, otherwise
  the tool builds HTML. On Windows, use Git Bash or WSL for `build-paper`.
  UTF-8 Python tests do not establish whole-workflow Windows support.
- R pipelines need R; Python pipelines can use `uv`. Running a pipeline executes
  project code with your permissions. Model steps also depend on your assistant's
  access and may incur its usual costs. No native non-Claude integration or
  cross-platform performance guarantee is claimed.

## License and contributions

Code, skills, agents and templates are [MIT](LICENSE). Documentation under
`docs/` is [CC BY 4.0](LICENSE-docs); bundled papers and conversions retain their
authors' attribution. See the [licensing map](LICENSING.md). The new root guides
use MIT, the same license as this README.

[CONTRIBUTING.md](CONTRIBUTING.md) covers checks, privacy and licensing;
[CHANGELOG.md](CHANGELOG.md) distinguishes released changes from these docs.
The companion [ai-architecture](https://github.com/nik110403/ai-architecture)
repository is an early preview, not a promise that this collection update is live.
