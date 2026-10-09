# Live smoke run (2026-10-09)

Not part of the test suite (tests use recorded fixtures). Run from an empty project directory:

```sh
lit-search "central bank credibility inflation expectations" --since 2018 --n 10
lit-search --export-bib 10.1017/s1365100522000207 10.1000/nonexistent-zzz
```

Result:
- OpenAlex READY, 10 hits; Semantic Scholar UNAVAILABLE (HTTP 429 after 3 attempts: the keyless
  endpoint shares a rate limit and was throttled). Receipt status `partial`, exit 0, 6 unique items
  written to CSV, MD and receipt JSON. This is the documented degraded path, not a silent fallback.
- Bib export: the real DOI was appended to `07_references/references.bib` via doi.org content
  negotiation; the made-up DOI was reported `NOT RESOLVED` (HTTP 404) and nothing was invented.
- Both-index merge is covered by the fixture tests only; re-run the smoke later to see it live.
