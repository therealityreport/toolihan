---
name: runtime-connector-catalog
description: Export or normalize a runtime connector catalog so Tool Finder can include callable plugin connectors such as GitHub and Hugging Face.
---

# Runtime Connector Catalog

Use this when Tool Finder needs to include plugin connector tools from the current Codex session.

Create a fillable template:

```bash
python3 scripts/export_runtime_connector_catalog.py --template
```

Normalize a filled catalog:

```bash
python3 scripts/export_runtime_connector_catalog.py runtime-tools-raw.json
```

Then pass the catalog to the all-provider search:

```bash
python3 scripts/search_all_providers.py "<query>" --runtime-catalog runtime-connectors.json
```

Results from GitHub and Hugging Face plugin connectors are labeled `providerSource: connector-plugin`. Direct API results remain labeled `providerSource: direct-api`.
