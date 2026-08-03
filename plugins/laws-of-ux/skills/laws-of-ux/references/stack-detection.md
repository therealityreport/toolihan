# Stack detection, design-system crediting, sampling, refusal

Detect the stack **first**, then choose parsing strategy and confidence. Never grade a repo
with no frontend surface.

## 1. Detect the stack

Read, in order:

- `package.json` dependencies:
  - `react` + `next` → **Next.js**; `react` + `react-router` / Vite → **React SPA**
  - `vue` (+ `nuxt`) → **Vue / Nuxt**; `svelte` (+ `@sveltejs/kit`) → **Svelte / SvelteKit**
  - `@angular/core` → **Angular**; `astro` → **Astro**; `solid-js` → **Solid**
  - styling: `tailwindcss` (+ `tailwind.config.*`), `styled-components`/`@emotion` (CSS-in-JS),
    `sass`, CSS modules (`*.module.css`)
  - component libraries: shadcn (`components.json` + `@radix-ui/*`), `@mui/material`,
    `@chakra-ui/react`, `antd`, `@mantine/core`, `@radix-ui/*`, `bootstrap`
- Config/route markers: `next.config.*`, `app/` + `pages/` (Next), `src/routes` (SvelteKit /
  Remix), `angular.json`, `vite.config.*`, `astro.config.*`.
- Plain sites: an `index.html` with `<link rel="stylesheet">` and no framework deps → **plain
  HTML/CSS**.

Record the stack, the file globs to scan, and a confidence note per strategy (below).

## 2. What to scan (UI surface)

Components (`**/*.{tsx,jsx,vue,svelte,astro,html}`), styles/tokens (`tailwind.config.*`,
`**/*.css`, theme files), routing/nav config, forms, buttons, and async/loading code. Prefer
**routes/pages + shared layout/nav/form/button components** — the highest-UX-leverage files.

## 3. Parsing strategy & confidence by stack

- **Plain HTML/CSS** — real selectors in real CSS → **highest** static confidence. Best default
  fixture.
- **Tailwind** — sizes/spacing live in class strings (`min-h-11`, `gap-2`, `p-4`). Resolve
  utilities against the project's `tailwind.config` scale (teams customize it). Arbitrary values
  (`min-h-[44px]`) and `cn()`/`clsx` conditional classes are hard → **lower** confidence; note it.
- **CSS-in-JS** (styled-components/emotion) — styles in template literals/objects, often
  prop-driven and runtime-computed → **partial** static extraction, **lower** confidence. Strong
  case for the `--url` pass.
- **Component libraries** — see crediting below.
- **Monorepos** — detect workspaces (`pnpm-workspace.yaml`, `turbo.json`, `workspaces` in
  `package.json`); identify the actual frontend app(s); audit per-app and let the user target a
  package. A design-system package and a consuming app need different treatment.

## 4. Design-system crediting

When a component resolves to a known-good primitive (shadcn/Radix button, MUI `<Select>`,
Chakra `<Button>`), those libraries already satisfy some laws (accessible focus, Fitts-adequate
hit areas, built-in loading/skeleton primitives). **Credit the library:** mark the relevant law
`PASS (via design-system)` at high confidence rather than re-flagging.

But this is also a trap: the library guarantees the *primitive*, not its *composition*. You can
still cram 15 good buttons into one toolbar (Hick's), place two filled CTAs in one view (Von
Restorff), or skip loading states the library offers (Doherty). **Credit the primitive; audit
the composition.**

## 5. Large-codebase sampling

Don't audit thousands of components. Prioritize: (1) routes/pages, (2) shared layout/nav/form/
button components ranked by import-frequency, (3) cap and sample. **State the sample in the
report** ("audited 40 highest-traffic components of 600; results are indicative, not
exhaustive"). Never imply full coverage you didn't do. A default cap (e.g. ~60 files) may be
overridden via `.lawsofux.json`.

## 6. No-frontend refusal (do this — don't fake a grade)

If there is **no** frontend framework, no JSX/Vue/Svelte/Astro/HTML view files, and no
CSS/Tailwind — and the deps are backend/library/CLI (express, fastify, django, rails, a pure
SDK/library, a docs-only repo) — **stop and say so**, e.g.:

> No frontend UI detected in this repository, so a Laws-of-UX audit doesn't apply. (Found:
> <what you saw>.) Point me at a frontend app or a `--url` to audit a running interface.

Emit **no grade**. Same for a library/SDK repo with no UI and a docs-only repo.
