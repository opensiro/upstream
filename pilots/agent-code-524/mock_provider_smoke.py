#!/usr/bin/env python3
"""Local-only provider smoke for pinned agent-code PR #69. No live credentials."""
import http.server, json, os, pathlib, subprocess, tempfile, threading

BINARY = os.environ.get("AGENT_CODE_TEST_BINARY", str(pathlib.Path.cwd() / "target/debug/agent"))
EXPECTED_AUX = int(os.environ.get("AC524_EXPECT_AUX_CALLS", "0"))
FINDINGS = json.dumps({
    "findings": [{"title": "[P1] Lost update", "body": "Concurrent updates overwrite data",
      "confidence_score": 0.91, "priority": 1,
      "code_location": {"absolute_file_path": "/tmp/synthetic-repo/src/lib.rs",
                        "line_range": {"start": 12, "end": 14}}}],
    "overall_correctness": "patch is incorrect",
    "overall_explanation": "Synthetic concurrency defect", "overall_confidence_score": 0.91
}, separators=(',', ':'))
requests = []

class Mock(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"data":[]}')
    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("content-length", "0")))
        try: msg = json.loads(raw)
        except Exception: msg = {}
        messages = msg.get("messages", [])
        system = "\n".join(str(m.get("content", "")) for m in messages if m.get("role") == "system")
        user = "\n".join(str(m.get("content", "")) for m in messages if m.get("role") == "user")
        requests.append({
            "path": self.path,
            "system_has_review_persona": "independent, read-only code reviewer" in system,
            "system_has_rubric": "introduced by this change" in system.lower(),
            "system_has_json_contract": "overall_correctness" in system,
            "system_has_general_persona": "You are an AI coding agent" in system,
            "user_has_task": "Inspect commit abc123" in user,
            "auxiliary_model_call": "independent, read-only code reviewer" not in system,
            "tool_names": [t.get("function", {}).get("name") for t in msg.get("tools", [])],
            "system_chars": len(system), "user_chars": len(user),
        })
        chunks = [
            {"choices": [{"index": 0, "delta": {"role": "assistant", "content": FINDINGS}, "finish_reason": None}]},
            {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 80, "completion_tokens": 85, "total_tokens": 165}},
        ]
        payload = b''.join(b"data: "+json.dumps(ch).encode()+b"\n\n" for ch in chunks)+b"data: [DONE]\n\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass
    def log_message(self, *args): pass

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Mock)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/v1"
try:
    with tempfile.TemporaryDirectory(prefix="ac524-mock-") as d:
        root = pathlib.Path(d)
        work = root / "project"
        work.mkdir()
        (work / "README.md").write_text("Synthetic review fixture\n")
        overlay = root / "readonly.toml"
        overlay.write_text('[permissions]\ndefault_mode = "plan"\nallowed_tools = ["FileRead", "Grep", "Glob", "Bash"]\ndisallowed_tools = ["FileWrite", "FileEdit", "WebFetch", "Agent", "Task"]\n')
        env = {"HOME": str(root), "PATH": "/usr/bin:/bin", "AGENT_CODE_SUBAGENT": "1",
               "AGENT_CODE_SUBAGENT_TYPE": "review", "AGENT_CODE_REQUIRE_PERMISSIONS_OVERLAY": "1",
               "NO_COLOR": "1"}
        args = [BINARY, "--prompt", "Inspect commit abc123 in this synthetic project.",
                "--output-format", "json", "--provider", "openai",
                "--api-base-url", url, "--api-key", "synthetic-local-test-only",
                "--model", "gpt-4o-mini", "-C", str(work), "--permission-mode", "plan",
                "--permissions-overlay", str(overlay)]
        # Security regressions: a mandatory overlay must fail before any model call.
        absent = subprocess.run(args[:-2], env=env, capture_output=True, text=True, timeout=20)
        assert absent.returncode != 0 and "overlay" in absent.stderr.lower()
        assert len(requests) == 0, "Missing-overlay path reached the provider"
        overlay.write_text("[not valid TOML")
        malformed = subprocess.run(args, env=env, capture_output=True, text=True, timeout=20)
        assert malformed.returncode != 0 and "overlay" in malformed.stderr.lower()
        assert len(requests) == 0, "Malformed-overlay path reached the provider"
        overlay.write_text('[permissions]\ndefault_mode = "plan"\nallowed_tools = ["FileRead", "Grep", "Glob", "Bash"]\ndisallowed_tools = ["FileWrite", "FileEdit", "WebFetch", "Agent", "Task"]\n')
        proc = subprocess.run(args, env=env, capture_output=True, text=True, timeout=45)
        events = []
        for line in proc.stdout.splitlines():
            try: events.append(json.loads(line))
            except: events.append({"type": "INVALID", "snippet": line[:100]})
        types = [x.get("type") for x in events]
        deltas = "".join(x.get("content", "") for x in events if x.get("type") == "text_delta")
        output = {"process_exit": proc.returncode,
                  "missing_overlay_pre_provider_rejected": absent.returncode != 0,
                  "malformed_overlay_pre_provider_rejected": malformed.returncode != 0,
                  "provider_requests": requests,
                  "auxiliary_requests": sum(r["auxiliary_model_call"] for r in requests),
                  "memory_lock_created": bool(list(root.rglob(".consolidate-lock"))),
                  "event_types": types, "delta_exactly_schema": deltas == FINDINGS,
                  "session_end_exit_code": [x.get("exit_code") for x in events if x.get("type")=="session_end"],
                  "stdout_jsonl_lines": len(events),
                  "stderr_tail": proc.stderr[-700:],
                  "empty_worktree_except_fixture": sorted(x.name for x in work.iterdir())==["README.md"]}
        # Deliberately do not log real request content or authentication material.
        print(json.dumps(output, indent=2))
        assert proc.returncode == 0, "Child must run successfully with mocked provider"
        reviewer_requests = [r for r in requests if r["system_has_review_persona"]]
        assert len(reviewer_requests) == 1, "Exactly one actual review model request"
        assert output["auxiliary_requests"] == EXPECTED_AUX, "Unexpected auxiliary LLM traffic"
        assert reviewer_requests[0]["system_has_json_contract"] and reviewer_requests[0]["system_has_rubric"]
        assert reviewer_requests[0]["user_has_task"] and not reviewer_requests[0]["system_has_general_persona"]
        assert set(reviewer_requests[0]["tool_names"]) == {"Bash", "FileRead", "Grep", "Glob"}
        assert deltas == FINDINGS
        assert "session_end" in types and [x.get("exit_code") for x in events if x.get("type")=="session_end"] == [0]
        assert output["empty_worktree_except_fixture"], "Review must not write to synthetic repo"
finally:
    server.shutdown()
