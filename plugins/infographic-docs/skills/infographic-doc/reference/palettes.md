# Palette guide

The design system is the **shadcn/ui neutral palette** (HSL tokens, automatic light/dark via `prefers-color-scheme`). **Neutral is the default and the house style** — every reference doc (ponytail, neon, the style guide, …) ships with **no palette change at all**. The near-black `--primary` plus the multicolor `--accent-*` tokens give docs their look; a colored `--primary` is the **exception**, not the norm. Default to neutral unless the user explicitly asks for a tint.

When you DO tint — only on explicit request or a strong brand color — override **only `--primary` and `--ring`**, as a bare HSL triple (`H S% L%` — *no* `hsl()` wrapper, that's how shadcn tokens are stored). Put the override in a `<style>` block in the page's `<head>`, after the `<link>` to `styles.css`, identical on every page (and identical across all docs in the same family — never a different tint per sibling doc):

```html
<style>
  :root {
    --primary: 173 80% 36%;   /* the brand hue */
    --ring:    173 80% 36%;   /* keep equal to --primary */
  }
</style>
```

The stylesheet derives everything else from these: `--brand`, the active-tab fill, link colors, the hero numerics, and the section accents all map off `--primary`. You never set `--brand`, `--brand-glow`, `--brand-deep`, or `--brand-dim` directly anymore — those are bridge variables computed for you.

The `--accent-*` variables (cyan, green, amber, rose, blue, violet, lime) stay as-is. They color secondary cards in lists and grids — you want that variety in every doc regardless of brand.

## Presets

Drop the `--primary` / `--ring` triple from the matching row into the `<style>` block. (Leave it out entirely for the default neutral look.)

| Topic | `--primary` / `--ring` |
|---|---|
| **Neutral (default)** — most docs, multi-tool recaps | *omit the override* |
| **Codex teal** — OpenAI, Codex, infra | `173 80% 36%` |
| **Deep purple** — knowledge mgmt, memory, second-brain | `262 83% 58%` |
| **Anthropic warm** — Claude, AI assistants | `17 60% 47%` |
| **Stripe indigo** — payments, fintech, billing | `244 75% 58%` |
| **AWS orange** — AWS, cloud, deployment | `36 100% 45%` |
| **GitHub blue** — repos, version control, dev workflow | `221 83% 53%` |
| **Linear iris** — project management, planning | `234 56% 56%` |
| **Supabase emerald** — Supabase, Postgres, data | `153 60% 40%` |
| **Tailwind sky** — Tailwind, frontend, CSS | `199 89% 45%` |
| **Vercel mono** — Vercel, edge, high-contrast | *omit (the neutral near-black primary already is this)* |

## Rolling a new palette

When none of the presets fit:

1. Take the topic's actual brand color (their logo / landing-page accent) and convert it to HSL.
2. Set `--primary` to that `H S% L%`. Keep saturation up (saturated, not pastel) and lightness in the **35–58%** range so the color has enough contrast on a white card *and* reads on the dark-mode surface. If the brand color is very light (a yellow or pale green), drop the lightness into the low 40s.
3. Set `--ring` to the same triple.
4. That's it — do not add any other variable. If a specific element needs a one-off accent, reach for an existing `--accent-*` token rather than inventing a color.

Sanity-check the result by eye:
- The active tab in the tab bar should pop; inactive tabs fade back.
- The hero numerics and `.page-number` eyebrows should read as the brand, not muddy.
- The auxiliary `--accent-*` colors in timelines/grids should still feel like they belong.
- Toggle your OS to dark mode and confirm the doc is still legible (the neutral surfaces flip automatically; your `--primary` stays fixed).

## Don't touch

- The shadcn neutral tokens (`--background`, `--foreground`, `--card`, `--border`, `--muted`, `--secondary`, `--radius`, …) and their dark-mode block — the whole system depends on them.
- The bridge variables (`--brand*`, `--bg-*`, `--text-*`, `--border-*`) — they're computed from the tokens above; override `--primary` instead.
- `--accent-*` (cyan/green/amber/rose/blue/violet/lime) — their variety is the point.
