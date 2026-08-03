---
name: compare-tools
description: Compare candidate tools, connectors, MCPs, skills, plugins, agents, CLIs, or hooks and recommend the best fit for a specific project or job.
---

# Compare Tools

Compare candidates on:

- Capability fit.
- Availability.
- Installation and auth complexity.
- Safety and permission scope.
- Maintenance.
- Integration fit.
- Improvement leverage.

Use `scripts/compare_candidates.py` when candidates are available as normalized JSON.
For dense result sets, open `assets/comparison-ui/index.html` and paste the normalized JSON payload to compare candidates side by side.

Return:

- Best overall choice.
- Best callable-now choice.
- Best installable choice.
- Best reference-only example.
- Tradeoffs.
- Rejected options with concise reasons.
