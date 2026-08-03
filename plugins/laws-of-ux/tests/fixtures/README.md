# Fixtures — the heuristic regression harness

Point `/ux-audit` at each directory and check the auditor behaves. These fixtures are how you
tune thresholds without regressing precision/recall.

| Fixture | Tests | Expected |
|---|---|---|
| `known-bad/` | **recall** | catches every planted violation, each with real `file:line`; low-ish grade; tier-c laws `NOT_ASSESSED` |
| `known-good/` | **precision** | few/no false positives; credits adherence signals; high grade |
| `no-frontend/` | **refusal** | detects no frontend surface → polite refusal, **no grade emitted** |

Both `known-bad` and `known-good` are plain HTML/CSS/JS (the highest-static-confidence stack, so
the cleanest regression baseline). When extending coverage, add edge-stack fixtures (Vue,
Svelte, CSS-in-JS, a monorepo) and assert graceful **confidence downgrades**, not crashes — per
`skills/laws-of-ux/references/stack-detection.md`.

Run the contract validator (structure, not behavior) with:

```
node --test tests/validate-plugin.mjs
```
