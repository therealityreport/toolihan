# Doherty Threshold

**Principle · weight 3 · tier b static / a live · SCORED · owner: Interaction**

- **Definition / why it matters:** Productivity soars when system response stays under ~400ms
  so neither user nor computer waits. Perceived performance drives satisfaction.
- **Applies when:** the UI performs async work — data fetches, mutations, navigation, search.
- **Adherence signals:** loading/pending UI around async — `isLoading`/`isPending`,
  `<Suspense>`, skeleton components, spinners, `aria-busy`; optimistic UI on mutations;
  debounced inputs; route-level loading (`loading.tsx` in Next).
- **Violation signals:** `await`/fetch in a handler or effect with **no** pending UI nearby;
  mutations with no optimistic update; un-debounced search. Locate: `await`, `fetch(`,
  `useMutation`, `onSubmit` handlers; then check for a loading state.
- **Confidence:** **b static** (you detect *pattern presence*, not real timing) / **a live**
  (the `--url` pass measures real LCP/INP with `lighthouse_audit` + performance traces and
  grades against the 400ms / Core Web Vitals thresholds). Before flagging "no loading state",
  **trace up the tree** and check data libraries — React Query/SWR/`<Suspense>` often provide it
  far from the fetch.
- **Example fix:** add an `isLoading` skeleton around the fetch; optimistic update on the
  mutation; debounce the search input.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Principles). Scoring: `references/scoring-rubric.md`._
