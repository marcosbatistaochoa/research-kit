# Checking ordinary Word quotations

`check-docx` reads an existing saved `.docx`; it never changes it. It is for a
lecture or manuscript with ordinary typed author--year citations and references.
It does **not** use Zotero, Better BibTeX, a library export, or literature notes.

First inventory the supported double-quoted passages. `--root` is required and
selects the source collection, even when the Word file is elsewhere.

```sh
python3 "/absolute/path/to/research-kit/plugins/research-kit/bin/check-docx" \
  --root "/absolute/path/to/project" --inventory "/absolute/path/to/new-word-quotes.csv" \
  "/absolute/path/to/lecture.docx"
```

Open the new CSV and explicitly fill `source_md` (a path below
`02_sources/md/`) and the positive source `page` for every row. You, not an
assistant, select that mapping. The checker does not infer it from typed
citations or references. Then verify, optionally creating fresh reports:

```powershell
& python "C:\absolute\path\to\research-kit\plugins\research-kit\bin\check-docx" `
  --root "C:\research\project" --bindings "C:\research\word-quotes.csv" `
  --report "C:\research\word-check" "C:\lecture.docx"
```

The source conversion's canonical hash and manifest are enforced, each mapped
quote must occur verbatim on its selected page, and source paths must resolve
inside `02_sources/md/`. `QUOTE_MATCH` means only that user-selected mapping
matches the converted source page; it is not a global citation, bibliography or
document-identity pass.

It reads body/table paragraphs and referenced positive footnotes/endnotes,
including text split across Word runs. Deleted text is ignored and inserted text
is included. Headers, footers, text boxes, fields, embedded/altChunk content and
unsupported/unbalanced quote forms are coverage warnings and make the command
non-success rather than silently claiming coverage. Outputs are new-only.
For spreadsheet safety, every CSV cell beginning with an apostrophe, `=`, `+`,
`-`, `@`, tab, or carriage return is prefixed with one apostrophe. The checker
reverses that prefix when it reads a bindings CSV, so quote hashes and matching
always use the original text.

Run the bundled offline demonstration with `python3 examples/word/RUN.py --out
/tmp/research-kit-word-demo`. It needs local `pandoc` but no network or model.
