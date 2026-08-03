import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from collect_mcp_owner_context import collect, read_config_summary  # noqa: E402
from debugpro_context_commands import run_command  # noqa: E402
from debugpro_redaction import redact_text  # noqa: E402


SECRETS = (
    "postgres://user:p4ss@db.example/app",
    "sessionid=abc123",
    "PRIVATE_KEY=abc123",
    "X-Amz-Signature=abc123",
)


class EvidenceRedactionTests(unittest.TestCase):
    def test_config_summary_never_returns_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.toml"
            config.write_text(
                '\n'.join(
                    (
                        'database_url = "postgres://user:p4ss@db.example/app"',
                        'cookie = "sessionid=abc123"',
                        'private_key = "PRIVATE_KEY=abc123"',
                        'signed_url = "https://example.test/file?X-Amz-Signature=abc123"',
                    )
                ),
                encoding="utf-8",
            )

            result = read_config_summary(config, max_lines=80)

        rendered = repr(result)
        for secret in SECRETS:
            self.assertNotIn(secret, rendered)
        self.assertEqual(result["keys"], ["cookie", "database_url", "private_key", "signed_url"])

    def test_command_output_is_redacted_on_success(self) -> None:
        command = (
            sys.executable,
            "-c",
            "print('remote https://user:p4ss@example.test/repo.git')",
        )

        result = run_command(command, PLUGIN_ROOT)

        self.assertNotIn("p4ss", repr(result))

    def test_json_config_reports_nested_keys_without_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "mcp.json"
            config.write_text(
                '{"mcpServers":{"payments":{"command":"/private/server"}}}',
                encoding="utf-8",
            )

            result = read_config_summary(config, max_lines=80)

        self.assertEqual(
            result["keys"],
            ["mcpServers", "mcpServers.payments", "mcpServers.payments.command"],
        )
        self.assertNotIn("/private/server", repr(result))

    def test_json_command_output_preserves_structure_and_redacts_values(self) -> None:
        command = (
            sys.executable,
            "-c",
            'print(\'{"name":"Secret scanning","token":"abc123"}\')',
        )

        result = run_command(command, PLUGIN_ROOT)

        self.assertEqual(result["stdout"]["name"], "Secret scanning")
        self.assertEqual(result["stdout"]["token"], "<redacted>")

    def test_command_output_is_redacted_on_timeout(self) -> None:
        expired = subprocess.TimeoutExpired(
            cmd=("example",),
            timeout=1,
            output="COOKIE=sessionid=abc123",
            stderr="PRIVATE_KEY=abc123",
        )
        with mock.patch("debugpro_context_commands.subprocess.run", side_effect=expired):
            result = run_command((sys.executable, "-V"), PLUGIN_ROOT, timeout=1)

        rendered = repr(result)
        self.assertNotIn("abc123", rendered)

    def test_pem_blocks_and_google_signed_urls_are_redacted(self) -> None:
        text = "\n".join(
            (
                "-----BEGIN PRIVATE KEY-----",
                "c3VwZXItc2VjcmV0LWtleQ==",
                "-----END PRIVATE KEY-----",
                "https://storage.test/file?X-Goog-Signature=abc123",
            )
        )

        redacted = redact_text(text)

        self.assertNotIn("c3VwZXItc2VjcmV0LWtleQ", redacted)
        self.assertNotIn("abc123", redacted)

    def test_truncated_pem_output_is_redacted_to_end_of_input(self) -> None:
        redacted = redact_text(
            "-----BEGIN PRIVATE KEY-----\nc3VwZXItc2VjcmV0LWtleQ=="
        )

        self.assertNotIn("c3VwZXItc2VjcmV0LWtleQ", redacted)

    def test_mcp_environment_reports_presence_not_values(self) -> None:
        with mock.patch.dict("collect_mcp_owner_context.os.environ", {"MCP_CONFIG": "/private/config.json"}):
            with mock.patch("collect_mcp_owner_context.run_command", return_value={"available": False}):
                environment = collect(max_lines=0, timeout=0)["environment"]

        self.assertEqual(environment["MCP_CONFIG"], "present")
        self.assertNotIn("/private/config.json", repr(environment))


if __name__ == "__main__":
    unittest.main()
