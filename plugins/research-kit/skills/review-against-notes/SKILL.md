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
   UNSUPPORTED (no note), THIN (note without claims or quotes), OK. Resolve UNSUPPORTED/THIN rows
   (write the note, or drop the citation) before the model passes.
3. Delegate to the `claim-checker` agent with the cited sentences and keys. It judges each sentence against its note only
   (SUPPORTED / PARTIAL / NOT SUPPORTED / NOT ASSESSED, plus the quote relied on).
4. Delegate to the `skeptic` agent, which tries to refute the 3 strongest claims, each finding with an evidence anchor.
5. Save the report yourself to `00_admin/reviews/<date>.md` (create the folder). List findings as atomic rows
   `id | claim | verdict | evidence | fix` and end with counts that reconcile:
   supported + unsupported + not assessed = cited sentences checked.
6. Tell the user what is unsupported or partial. Do not edit the draft; the author decides.
