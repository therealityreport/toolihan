---
name: hugging-face-provider
description: Search Hugging Face Hub models, datasets, and Spaces through Tool Finder's direct Hugging Face provider.
---

# Hugging Face Provider

Use this when the user asks Tool Finder to find Hugging Face models, datasets, Spaces, or ML assets.

Run:

```bash
python3 scripts/search_huggingface.py "<query>" --kind all --limit 5
```

Use `--kind models`, `--kind datasets`, or `--kind spaces` for narrower searches.

Use `scripts/huggingface_auth_helper.py --validate-token` before searches that need private or gated Hub access. Public model, dataset, and Space searches do not require a token.

Hugging Face results use provider-specific ranking signals including downloads, likes, task pipeline, SDK/runtime, tags, license metadata, recency, and gated/private status.

Results are references only. Do not download models, datasets, or Space code automatically. Review licenses, model cards, dataset cards, and Space runtimes before adoption.
