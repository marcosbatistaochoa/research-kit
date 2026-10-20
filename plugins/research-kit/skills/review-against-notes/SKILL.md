---
name: review-against-notes
description: Review a draft against the project's literature notes - mechanical citation checks first, then model judgment, then an adversarial pass, ending in a dated review report. Use when the user wants a draft fact-checked against their notes before submission.
---

Requires: Python 3.9+; a draft with pandoc citations (`[@key]`) and literature notes in `01_notes/lit/` (see the literature-notes skill).

# Review against notes

Order matters: mechanical checks first, model judgment second, adversary last. Reviewers never edit the draft.

1. Verify quotes in every note:

   ```
   verify-quotes 01_notes/lit/*.md
   ```

   If not on PATH, run it from the kit's plugins/research-kit/bin/. Fix FAILs before going on.
2. Map citations to notes:

   ```
   check-claims <draft.md>
   ```

   If not on PATH, run it from the kit's plugins/research-kit/bin/. It prints a markdown table:
   OK, NO-SOURCE, or UNVERIFIED with the reason (no note, a note without quotes, a quote that fails
   `verify-quotes`, or a quoted passage of 4+ words in the paragraph that no cited source holds verbatim;
   check ellipses, `[brackets]`, case, and that every quotation mark is closed). A quote is checked
   against the sources cited in its paragraph, so cite the paper the quote comes from.
   NO-SOURCE marks a software, dataset or print-book citation whose note says `source_md: none`; it is
   not a failure. Never drop such a citation: write a note with `source_md: none` and `no_source: <reason>`.
   It also exits non-zero if the draft has no recognisable citation (`[@key]` or narrative `@key`).
   Resolve UNVERIFIED rows (write or fix the note, fix the quote, or drop the citation) before the
   model passes.
3. Delegate to the `claim-checker` agent with the cited sentences and keys. It judges each sentence against its note only
   (SUPPORTED / PARTIAL / NOT SUPPORTED / NOT ASSESSED, plus the quote relied on).
4. Delegate to the `skeptic` agent, which tries to refute the 3 strongest claims, each finding with an evidence anchor.
5. Save the report yourself to `00_admin/reviews/<date>.md` (create the folder). List findings as atomic rows
   `id | claim | verdict | evidence | fix` and end with counts that reconcile:
   supported + unsupported + not assessed = cited sentences checked.
6. Tell the user what is unsupported or partial. Do not edit the draft; the author decides.
