---
name: paper-build
description: Build the paper from 10_paper/paper.md with pandoc citations to PDF or HTML, and check the bibliography. Use when the user wants to compile, cite-check or tidy the .bib of a research paper project.
---

Requires: Python 3.9+; pandoc (xelatex optional, for PDF; without it the build produces HTML).

# Paper build

Layout: `10_paper/paper.md` (abstract, introduction, literature, data, method, results, discussion,
conclusion), `10_paper/metadata.yaml` (title, author, date, bibliography path). No CSL file is
bundled: pandoc's default citation style is used; drop a `.csl` into `10_paper/` and add `csl:` to
`metadata.yaml` to change it.

1. Check the bibliography first, from the project root:

   ```
   check-bib
   ```

   If not on PATH, run it from the kit's plugins/research-kit/bin/. It reports duplicate keys,
   entries missing author/title/year, malformed DOIs, keys cited but absent (error) and keys
   present but uncited (note). Exit 1 on any error.
2. Build:

   ```
   build-paper
   ```

   If not on PATH, run it from the kit's plugins/research-kit/bin/. It logs tool versions, runs
   `pandoc --citeproc` and writes `10_paper/paper.pdf` (or `.html`). The compile guard fails on
   literal `???`, unresolved citations and missing image/include files. `--soft` downgrades
   failures to warnings (exit 0) for hooks.
3. Fix each reported problem at its source; never silence the guard.

Bib discipline: one `.bib` per project, ideally exported by the reference manager. Verify author,
year, title and venue against the DOI landing page or the PDF before adding an entry; an entry
that cannot be verified is not written. Citekeys are stable once cited.
