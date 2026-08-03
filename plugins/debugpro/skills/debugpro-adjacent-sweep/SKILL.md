---
name: debugpro-adjacent-sweep
description: Use when an approved fix needs a bounded same-surface adjacent-defect check.
---

# DebugPro Adjacent Sweep

Use only after a fix is approved and the touched surface is known. Prefer `find-bugs-plus` when available.

## Boundary

Search only defects sharing the touched files/flow, root-cause family, contract, state transition, auth boundary, error path, or test seam.
Use `../debugpro/references/capability-router.md` only to select same-surface tools and fallbacks; do not broaden the sweep.

Stop at unrelated refactors, style cleanup, broad review, or speculative hunting.

## Procedure

1. Restate the original bug and fix boundary.
2. Identify same-surface search terms and files.
3. Use targeted reads, tests, and searches only.
4. Report only evidence-backed adjacent defects.
5. Fix only same-surface defects within the approved scope.
6. Verify the original fix and each adjacent fix separately.

## Output

```markdown
## Adjacent Sweep
- Boundary:
- Searches/probes run:
- Related defects found:
- Fixes made:
- Verification:
- Out of scope:
```
