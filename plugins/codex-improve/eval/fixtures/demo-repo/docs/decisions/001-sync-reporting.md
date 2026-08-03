# Keep report generation synchronous

Report generation is intentionally synchronous because the CLI must write its final report before exiting. Revisit only if the product becomes a long-running service.
