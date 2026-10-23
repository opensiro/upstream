#!/usr/bin/env python3
"""Offline process-level smoke for the OpenSiro agent-code #524 native patch.

Only a loopback, deliberately unreachable model URL is configured; this checks
startup role/overlay invariants, not the quality of a model-generated review.
"""
import argparse
import os
import pathlib
import subprocess
import tempfile

def invoke(binary, root, *, reviewer, overlay=None):
    cwd = root / "repo"
    cwd.mkdir(exist_ok=True)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(root / "home"),
        "XDG_CONFIG_HOME": str(root / "home" / "config"),
        "XDG_CACHE_HOME": str(root / "home" / "cache"),
        "AGENT_CODE_API_KEY": "local-mock-only",
        "NO_COLOR": "1",
    }
    if reviewer:
        env.update(
            AGENT_CODE_SUBAGENT="1",
            AGENT_CODE_SUBAGENT_TYPE="review",
            AGENT_CODE_REQUIRE_PERMISSIONS_OVERLAY="1",
        )
    args = [
        str(binary),
        "--cwd", str(cwd),
        "--api-base-url", "http://127.0.0.1:9/v1",
        "--provider", "openai",
        "--model", "local-mock",
        "--dump-system-prompt",
    ]
    if overlay is not None:
        args.extend(["--permissions-overlay", str(overlay)])
    return subprocess.run(args, env=env, cwd=cwd, capture_output=True, text=True, timeout=45)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=pathlib.Path, required=True)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="agent-code-524-offline-") as d:
        root = pathlib.Path(d)
        (root / "home").mkdir()
        overlay = root / "read-only.toml"
        overlay.write_text(
            '[permissions]\ndefault_mode = "plan"\n'
            'allowed_tools = ["FileRead", "Grep", "Glob", "Bash"]\n'
        )
        main_role = invoke(binary, root, reviewer=False)
        assert main_role.returncode == 0, (main_role.stderr[-1200:], main_role.stdout[-300:])
        assert "You are an AI coding agent." in main_role.stdout

        review = invoke(binary, root, reviewer=True, overlay=overlay)
        assert review.returncode == 0, (review.stderr[-1200:], review.stdout[-300:])
        assert "You are an independent, read-only code reviewer." in review.stdout
        assert "You are an AI coding agent." not in review.stdout
        assert "no prior conversation history" in review.stdout.lower()
        assert "patch is incorrect" in review.stdout
        assert "## FileRead" in review.stdout
        assert "## FileWrite" not in review.stdout

        missing = invoke(binary, root, reviewer=True)
        assert missing.returncode != 0, missing.stdout
        assert "missing required --permissions-overlay" in missing.stderr

        malformed = root / "bad-overlay.toml"
        malformed.write_text("not valid toml = [")
        invalid = invoke(binary, root, reviewer=True, overlay=malformed)
        assert invalid.returncode != 0, invalid.stdout
        assert "--permissions-overlay" in invalid.stderr

        print("OFFLINE_MAIN_ROLE_PROMPT=PASS")
        print("OFFLINE_REVIEWER_ROLE_REPLACEMENT=PASS")
        print("OFFLINE_CHILD_REQUIRED_OVERLAY_MISSING=REJECTED")
        print("OFFLINE_CHILD_MALFORMED_OVERLAY=REJECTED")
        print("NETWORK_OR_MODEL_CALLS=NOT_EXERCISED")

if __name__ == "__main__":
    main()
