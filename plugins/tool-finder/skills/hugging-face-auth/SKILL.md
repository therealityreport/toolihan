---
name: hugging-face-auth
description: Diagnose Hugging Face auth for Tool Finder without printing or storing tokens.
---

# Hugging Face Auth

Use this when Tool Finder needs authenticated Hugging Face Hub access for private or gated resources.

Run:

```bash
python3 scripts/huggingface_auth_helper.py --token-env HF_TOKEN --validate-token
```

Report:

- Whether `HF_TOKEN` is present.
- Whether alternate token env vars such as `HUGGING_FACE_HUB_TOKEN` are present.
- Whether Hugging Face CLI appears installed.
- Whether token validation passed when `--validate-token` is used.

Do not print tokens, write tokens to files, or download Hub assets automatically.
