---
citekey: kireyev2026pricebench
source_md: 02_sources/md/kireyev2026pricebench.md
read_scope: full_text
claims:
  - "PriceBench recovers an LLM's price, quality and brand preferences from its hotel-booking choices with a logit choice model, applied to 28 LLMs from 8 providers on 3,600 tasks built from 179 real NYC hotels."
  - "Capability is associated with how consistently an LLM chooses, not with what it chooses: more capable LLMs hold stronger, more consistent preferences, but the price-versus-quality lean is unrelated to capability."
  - "Five of 28 LLMs are position-locked at temperature zero, so a platform that controls listing order controls 88-100% of their bookings and no usable preferences can be estimated for them."
  - "Among engaged LLMs, price sensitivity and willingness to pay for a review-score point vary by more than an order of magnitude, even between same-family siblings, and move mean booked nightly price from $247 to $393 on identical tasks."
  - "Brand preferences persist after controlling for price and quality but are unrelated to the provider (permutation p = 0.48)."
  - "The engaged LLMs value a review-score point far above the documented human range, so an agent's valuations must be measured rather than assumed human-like; the author notes that the capability results are only cross-sectional associations."
quotes:
  - page: 1
    text: "We find that capability is associated with how consistently an LLM chooses, not with what it chooses: more capable LLMs hold stronger, more consistent preferences,"
  - page: 1
    text: "price sensitivity spans more than an order of magnitude, and the price/quality trade-off moves mean booked nightly price from $247 to $393 on identical tasks."
  - page: 4
    text: "Whatever its cause, these LLMs behave as constants and are directly exploitable"
  - page: 6
    text: "how decisively an LLM chooses says nothing about which way it leans."
  - page: 6
    text: "What an identical set of listings sells for thus depends on which LLM is shopping it."
  - page: 6
    text: "two LLMs from the same provider are, on average, no more alike in brand preference than two from different providers"
  - page: 7
    text: "they value the same point at $68 to $1,071 (median $269), so even the most frugal sits above the top of the documented per-point range,"
  - page: 8
    text: "The capability results are cross-sectional associations across 28 LLMs: training-data composition, alignment recipe, and architecture could jointly determine capability and choice consistency."
---

# kireyev2026pricebench

Kireyev (LSE, 2026), "PriceBench: A Diagnostic Benchmark for Price, Quality, and Brand Preferences in LLM Booking Agents". The benchmark has 1,800 binary and 1,800 ternary hotel-choice tasks. Each task is scored in both option orderings. The author fits per-LLM logit choice models on attribute differences, with an intercept that absorbs position bias. Appendices cover the following.

- **Prompt:** the template used for every task.
- **Engagement triage:** the first-shown selection rates per LLM.
- **Price response:** extended results, including three price functional forms (linear, log, nonparametric deciles).
- **Quality coefficients:** the full coefficient panel.
- **Brand coefficients:** per-LLM brand estimates.
- **Robustness:** prompt-format, temperature and five-option checks, plus bootstrap and multiplicity audits.
- **Human anchors:** conversions behind the human reference range.
- **Datasheet:** documentation of the released data.

Key reported numbers:
- Log-price coefficients run from -7.02 (GPT-5.4) to -0.40 (Qwen3 30B-A3B).
- Willingness to pay for one review-score point at a $250 nightly rate spans about 16x, from $68 to $1,071.
- Mean booked price is $247 for GPT-5.4 and $393 for Phi-4 Mini.

Scope limits stated by the author:
- NYC hotels only.
- Elicitation is neutral and at temperature 0.
- No human choices were collected on the tasks.
- The capability results are observational.
