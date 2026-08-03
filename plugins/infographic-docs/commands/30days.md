---
name: 30days
description: Create a last-30-days community pulse HTML doc for a topic
---

The user wants a last-30-days community pulse about: $ARGUMENTS

Invoke the `community-30-days` skill from this plugin.

Follow this routing:

1. If `$ARGUMENTS` names a topic, use it.
2. If `$ARGUMENTS` is empty or says "this", "that", "our current topic", or "whatever we are talking about", infer the topic from the active conversation. Ask one concise question only if the topic is genuinely unclear.
3. Research the last 30 calendar days of public/community discussion across Reddit, X/Twitter, GitHub, Hacker News, YouTube, blogs/news, and other relevant public sources.
4. Generate a folder-based HTML doc in `${KB_ROOT}/info-docs/<topic-slug>/`. The folder must contain `index.html` and `meta.json`; loose single-page documents are not supported.
5. Use the shared `infographic-doc` style guide: separate HTML tab files, copied `assets/styles.css`, copied `assets/nav-script.js`, `meta.json`, glossary, sources tab, and library-index refresh.
6. Include the default tabs: Overview, Signal Map, Source Detail, GitHub / Builder Signal when relevant, Glossary, and Sources.
7. In the final chat response, link only the generated `index.html`, summarize the main takeaway, and call out any source limits.

Do not produce a raw social-media dump. The value is synthesis: what people keep saying, what changed this month, what appears noisy, and what the reader should do next.
