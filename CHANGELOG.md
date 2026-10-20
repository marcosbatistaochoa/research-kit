# Changelog

## 0.1.2

- Cosmetic release, no behaviour change. Terminal-transcript images now wrap at
  word boundaries (`tools/banner/bin/make-banner`), the licensing map covers the
  banner fonts, and a duplicated sentence is gone from the README.

## Unreleased

- `check-claims`: draft-quote findings (UNCITED rows, and UNVERIFIED rows caused only by a quotation in
  the draft) are advisory by default: printed as `UNVERIFIED (advisory)` / `UNCITED (advisory)` with an
  `advisory:` line, exit 0. `--strict-quotes` makes them fail. Note-level failures still always exit 1.
- `verify-quotes`: the project root comes from the note and is the outermost ancestor holding
  `02_sources/` (a planted `01_notes/02_sources/` no longer shadows it); under `--strict` a source md in a
  subdirectory of `02_sources/md/` fails.
- 2026-10-15: Documentation only. README restructured with banner, terminal
  transcript and plugin tables per the public repository template; `tools/banner`
  added for regenerating the images. Plugin version stayed 0.1.1 at that point.
- Expand collection documentation with a complete catalog, whole and selective
  installation, contributor guidance and non-Claude manual adapters.
- Clarify support assets, tool paths, template layout, review dependencies,
  Docling pagination and the limits of Windows test evidence.
- Correct the README's stale version reference to existing plugin version 0.1.1.
  These documentation changes do not constitute a new version or live install.

## 0.1.1

- UTF-8 handling for standalone Python tools, including Windows locale handling.
- Optional Semantic Scholar API-key support.

## 0.1.0

- Initial research-kit collection: seven skills, four agent roles, eight tools,
  project and Python/R pipeline templates, and research examples.
