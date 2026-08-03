# Miller's Law

**Heuristic · weight 2 · tier b · SCORED · owner: IA**

- **Definition / why it matters:** The average person holds ~7 (±2) items in working memory.
  Long, unstructured sets overflow it. (Don't cite "7±2" as a hard rule — it's a prompt to
  chunk, not a cap.) Score as a composite with **Chunking + Working Memory**.
- **Applies when:** the UI shows lists, groups of fields, or digit-strings (phone, card, code).
- **Adherence signals:** content chunked into labeled groups/sections; `<fieldset>`/`<legend>`;
  phone/card/OTP inputs with masking/`inputMode`/auto-formatting; long lists sectioned.
- **Violation signals:** > ~7 ungrouped form inputs in one `<form>`; long flat lists with no
  grouping; raw digit inputs with no chunking/mask. Locate: `<form`, `<input`, `<fieldset`.
- **Confidence:** b.
- **Example fix:** wrap related inputs in `<fieldset>`; split a 15-field form into steps;
  auto-format the card field into `#### #### #### ####`.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Heuristics). Scoring: `references/scoring-rubric.md`._
