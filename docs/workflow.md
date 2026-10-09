# Workflow: stages, components, files

research-kit follows one loop. Each stage reads files the previous stage wrote, so you can
enter anywhere and use only the stages you need.

```
 brief / question
       |
       v
 [1 search]        lit-search (skill literature-search)
       |            writes 01_notes/search/<date>-<slug>.{csv,md,receipt.json}
       |            appends 07_references/references.bib   (--export-bib)
       v
 [2 get PDFs]      you: save PDFs to 02_sources/pdf/
       |
       v
 [3 convert]       pdf2md (skill pdf-to-markdown)
       |            writes 02_sources/md/<stem>.md  (<!-- page N --> markers)
       |                   02_sources/manifest.csv
       v
 [4 notes]         agent source-reader (skill literature-notes)
       |            writes 01_notes/lit/<citekey>.md  (claims + page-pinned quotes)
       |            verify-quotes checks each quote against 02_sources/md/
       v
 [5 draft]         you (+ template 10_paper/paper.md, metadata.yaml)
       |
       v
 [6 review]        check-claims, check-bib, agents claim-checker + skeptic
       |            (skill review-against-notes); reads 10_paper/paper.md,
       |            01_notes/lit/, 07_references/references.bib
       v
 [7 build]         build-paper (skill paper-build)
                    writes 10_paper/paper.pdf or paper.html + build.log

 side track, any time:
 [A analysis]      new-pipeline + agent pipeline-runner (skill analysis-pipeline)
                    pipeline/output/{figures,tables} -> linked into 10_paper/

 [0 scaffold]      new-project (skill new-research-project) creates the numbered tree
```

| Stage | Components | Reads | Writes |
|---|---|---|---|
| 0 scaffold | `new-project` | bundled template | project tree |
| 1 search | `lit-search` | OpenAlex, Semantic Scholar, doi.org | `01_notes/search/*`, `07_references/references.bib` |
| 3 convert | `pdf2md` | `02_sources/pdf/*.pdf` | `02_sources/md/*.md`, `02_sources/manifest.csv` |
| 4 notes | `source-reader`, `verify-quotes` | `02_sources/md/*.md` | `01_notes/lit/*.md` |
| 6 review | `check-claims`, `check-bib`, `claim-checker`, `skeptic` | draft, notes, `.bib` | review report |
| 7 build | `build-paper` | `10_paper/paper.md`, `.bib` | `10_paper/paper.{pdf,html}` |
| A analysis | `new-pipeline`, `pipeline-runner` | `data/raw/` | `output/figures`, `output/tables` |

The model-based steps (`source-reader`, `claim-checker`, `skeptic`) only ever read files; the
mechanical tools (`verify-quotes`, `check-claims`, `check-bib`) need no model and no network.
