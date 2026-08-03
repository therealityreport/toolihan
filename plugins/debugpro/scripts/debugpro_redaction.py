"""Shared secret-safe text handling for DebugPro evidence collectors."""

from __future__ import annotations

import json
import re


SENSITIVE_KEY = re.compile(
    r"(?:api[_-]?key|authorization|cookie|database[_-]?url|private[\s_-]?key|"
    r"redis[_-]?url|session|signed[_-]?url|token|secret|password|passwd|pwd|"
    r"connection[_-]?string|webhook)",
    re.IGNORECASE,
)
URL_CREDENTIALS = re.compile(r"(?P<scheme>[a-z][a-z0-9+.-]*://)[^\s/@:]+:[^\s/@]+@", re.IGNORECASE)
SIGNED_QUERY = re.compile(
    r"(?P<key>[?&](?:x-amz-signature|x-goog-signature|signature|sig|token|key)=)[^&\s]+",
    re.IGNORECASE,
)
PEM_BLOCK = re.compile(
    r"-----BEGIN (?P<label>[^-\r\n]*PRIVATE KEY)-----.*?(?:-----END (?P=label)-----|\Z)",
    re.IGNORECASE | re.DOTALL,
)
BEARER = re.compile(r"(?P<prefix>\bBearer\s+)[A-Za-z0-9._~+/-]+=*", re.IGNORECASE)
CONFIG_KEY = re.compile(r'^\s*["\']?([A-Za-z_][A-Za-z0-9_.-]*)["\']?\s*[:=]')


def as_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def redact_scalar(value: object) -> str:
    text = as_text(value)
    text = PEM_BLOCK.sub("<redacted private key>", text)
    text = URL_CREDENTIALS.sub(r"\g<scheme><redacted>@", text)
    text = SIGNED_QUERY.sub(r"\g<key><redacted>", text)
    return BEARER.sub(r"\g<prefix><redacted>", text)


def redact_text(value: object) -> str:
    text = redact_scalar(value)
    redacted: list[str] = []
    for line in text.splitlines():
        if SENSITIVE_KEY.search(line):
            redacted.append("<redacted sensitive line>")
            continue
        redacted.append(line)
    return "\n".join(redacted)


def redact_json(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: "<redacted>" if SENSITIVE_KEY.search(str(key)) else redact_json(child)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [redact_json(item) for item in value]
    if isinstance(value, str):
        return redact_scalar(value)
    return value


def redact_output(value: object) -> object:
    text = as_text(value)
    try:
        return redact_json(json.loads(text))
    except json.JSONDecodeError:
        return redact_text(text)


def config_key_names(text: str) -> list[str]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError:
        document = None
    if isinstance(document, dict):
        keys: set[str] = set()

        def visit(value: object, prefix: str = "") -> None:
            if not isinstance(value, dict):
                return
            for key, child in value.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                keys.add(path)
                visit(child, path)

        visit(document)
        return sorted(keys)
    return sorted({match.group(1) for line in text.splitlines() if (match := CONFIG_KEY.match(line))})
