# Fixture: no-frontend

A backend-only Express + Postgres API with **no view layer** — no JSX/Vue/Svelte/HTML, no
CSS/Tailwind, no component library.

Expected outcome: `/ux-audit` on this directory must **refuse politely and emit no grade**
("No frontend UI detected…"), per `references/stack-detection.md`. This is the guardrail
against fabricating a UX grade for something that has no UX surface.
