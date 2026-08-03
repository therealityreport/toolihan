---
name: community-30-days
description: Activates when the user asks for a "30 days" or "last 30 days" community pulse, community discussion report, mention scan, social signal doc, or "what are people saying about X" explainer. Researches the last 30 days of public/community discussion across Reddit, X/Twitter, GitHub, Hacker News, YouTube, blogs/news, and other relevant public sources, then produces a multi-page HTML document using the infographic-docs style guide. It is for public conversation synthesis, not private account monitoring, paid trading advice, or live dashboards.
allowed-tools: Bash, Read, Write, WebSearch
---

# 30 Days Community Pulse

Use this skill when the user wants a **last-30-days community discussion document** about the current topic, product, person, repo, company, feature, controversy, launch, or decision.

The deliverable is a **multi-page HTML doc** in the same style system as `infographic-doc`, saved under:

`${KB_ROOT}/info-docs/<topic-slug>/`

The deliverable is always a folder containing at least `index.html` and `meta.json`; loose single-page documents and sidecar metadata are retired. This skill does not replace `infographic-doc`; it specializes it for live community signal. Use the existing `infographic-doc` layout rules, stylesheet, components, glossary expectations, root tag/index behavior, and verification checklist unless this file narrows them.

## Template Pack

Reusable templates live in `skills/community-30-days/templates/`.

Start from those templates when building a standard report:

- `index.html` - overview, hero, themes, timeline, and practical takeaway.
- `signal-map.html` - praise, adoption, requests, pain, confusion, and counter-signals.
- `source-detail.html` - source-by-source public-channel detail.
- `github.html` - builder/repository signal.
- `glossary.html` - plain-English definitions.
- `sources.html` - cited source cards.

Copy the templates into the output folder, replace every `{{PLACEHOLDER}}`, and then run `rg '{{' <doc-folder>` before final response. Omit or rewrite a tab only when the topic genuinely needs a different structure.

## Source Standard

Research the last 30 calendar days from today's date. If the user gives a different window, use their window and state it in the doc.

Cover the public sources that fit the topic:

- **Reddit** - threads, comments, subreddit context, upvotes, repeated complaints or praise.
- **X/Twitter** - public posts, creator/operator commentary, repeated phrasing, launch reactions, backlash, memes, and quote-post themes.
- **GitHub** - repository commits, pull requests, issues, discussions, releases, stars, forks, and maintainer activity.
- **Hacker News** - technical community reactions and comment debates.
- **YouTube / podcasts** - video titles, transcripts or summaries when accessible, view counts, comments when surfaced.
- **Blogs/news/forums** - supporting context, announcements, documentation, changelogs, and source-of-record pages.
- **Prediction or market sources** only when directly relevant; label them as market sentiment, not truth.

Prefer direct source pages and official APIs when available. Use WebSearch for discovery, then open direct URLs whenever possible. For GitHub, use `gh api`, `gh repo view`, `gh search`, or the GitHub REST API when useful. If a source is unavailable, say so in the doc's methods note rather than pretending coverage exists.

## Research Rules

1. **Start from the active topic.** If the user says "whatever we are talking about," infer the topic from the current conversation. Ask one concise question only if there is no clear topic.
2. **Use current evidence.** Do not rely on memory, old docs, or stale assumptions for community sentiment. Search live.
3. **Keep the date window explicit.** The doc must show "Last 30 days: YYYY-MM-DD to YYYY-MM-DD" in the hero or methods block.
4. **Separate signal from noise.** Do not list every mention. Group repeated themes and cite representative examples.
5. **Preserve disagreement.** Include counter-signals and minority views when they materially change the interpretation.
6. **Do not overclaim source coverage.** If X/Twitter is inaccessible except through search snippets, label it as snippet-limited.
7. **No private data.** Do not imply private DMs, private analytics, login-only dashboards, or unpublished account metrics were inspected.
8. **No trailing source dump in chat.** Put citations in the generated Sources tab; the chat final should link the local doc and summarize the result.

## Default Doc Structure

Use these tabs unless the topic needs a different shape:

1. **Overview** (`index.html`) - the executive pulse: what the community is saying, where the energy is, and the practical takeaway.
2. **Signal Map** (`signal-map.html`) - themes grouped by praise, pain, confusion, requests, controversy, and adoption signals.
3. **Source Detail** (`source-detail.html`) - source-by-source cards for Reddit, X/Twitter, Hacker News, YouTube, and web/news.
4. **GitHub / Builder Signal** (`github.html`) - repo activity, issues, releases, PRs, discussions, maintainer/user requests. Omit only when GitHub is irrelevant.
5. **Glossary** (`glossary.html`) - plain-English terms used in the report.
6. **Sources** (`sources.html`) - cited links with source type, date, and why each link mattered.

If the topic is a tool, library, SDK, framework, or repo whose value is adoptable in the user's projects, also add the existing **Use Cases** tab from `infographic-doc`.

## Overview Content

The Overview tab should include:

- A hero with the topic, date window, and one-sentence verdict.
- Four stats or counters, chosen honestly from the evidence. Examples: "12 Reddit threads", "7 active GitHub issues", "3 repeated asks", "2 strong counter-signals". Use "N/A" only if a source was unavailable.
- A "What people keep saying" section with 4-6 theme cards.
- A "What changed this month" timeline when there are notable events, releases, posts, or controversies.
- A "So what" section that tells the reader what to do with the signal.

## Signal Map Content

Group the community signal into practical buckets:

- **Praise** - what people like and why.
- **Pain** - bugs, friction, confusion, missing docs, pricing complaints, workflow blockers.
- **Requests** - features, integrations, guides, examples, defaults, fixes people ask for repeatedly.
- **Adoption evidence** - real usage, demos, repos, tutorials, testimonials, forks, stars, issue velocity.
- **Counter-signals** - skepticism, thin evidence, quiet channels, abandoned repos, conflicting claims.

Each bucket should cite representative links, not raw search results. Include short quotes only when they are useful and legally safe; paraphrase by default.

## GitHub / Builder Signal

When GitHub is relevant, inspect:

- Main repo metadata: stars, forks, latest push, release tags, open issues, pull requests.
- Recent commits or releases from the last 30 days.
- Issues/discussions that show repeated user needs.
- Forks only when they materially improve or diverge from the original.

Use GitHub as builder evidence, not as a popularity proxy by itself. A quiet repo can still have a loud Reddit thread; a popular repo can still have weak recent community discussion.

## Sources Tab

Every cited source card should include:

- Source name and link.
- Source type: Reddit, X/Twitter, GitHub, HN, YouTube, blog/news, docs, forum, other.
- Date or "accessed today" when publication date is unavailable.
- One sentence explaining why it mattered.

Do not include uncited links just to pad the page.

## Output Contract

When finished, the final chat response should be short:

- Name the doc that was created or updated.
- Link the local `index.html` file.
- Mention the date window and the main practical takeaway.
- Mention any source limitations, if any.

Do not paste the whole report into chat.
