"""Credential-free-source adapters for an existing GitHub-CLI VM/host.

No CLI __main__, no token discovery, no grant issuer, no stage execution.
The authenticated gh session and one-use operator approval must already
be supplied/enforced by the separate trusted execution host.
"""
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

from connected_stage_adapter import StageBlocked
from rest_fork_port import _repo

HTTP_STATUS = re.compile(r"^HTTP/\S+\s+(\d{3})\b", re.M)
POST_PATH = re.compile(
    r"^repos/opensiro-contributions/[A-Za-z0-9_.-]+/git/(trees|commits|refs)$"
)
GET_PATH = re.compile(r"^repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[^\s]*)?$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def need(ok, message):
    if not ok:
        raise StageBlocked(message)


class GitHubCLIJSONTransport:
    """Host-side gh api GET + *only* selected Git Data POST endpoints.

    A trusted host must ensure the actual gh credential principal matches
    the actor in the consumed one-use stage grant. This wrapper never checks
    credentials or creates grants. No direct user-facing CLI is included.
    """

    def __init__(self, *, runner=subprocess.run):
        need(callable(runner), "Trusted command runner required")
        self._runner = runner

    def __call__(self, method, path, body=None):
        need(method in ("GET", "POST") and type(path) is str,
             "Unsupported GitHub CLI request")
        if method == "GET":
            need(GET_PATH.fullmatch(path) is not None and body is None,
                 "Only repository-scoped read-only requests admitted")
        else:
            need(POST_PATH.fullmatch(path) is not None
                 and type(body) is dict,
                 "Only scoped Git Data POST requests admitted")
        with tempfile.TemporaryDirectory(prefix="opensiro-gh-api-") as tmp:
            args = ["gh", "api", "--include", "--method", method, path]
            if method == "POST":
                request_path = Path(tmp) / "request.json"
                request_path.write_text(json.dumps(body, ensure_ascii=False))
                request_path.chmod(0o600)
                args.extend(["--input", str(request_path)])
            try:
                completed = self._runner(args, capture_output=True, text=True,
                                         check=False, timeout=45)
            except (OSError, subprocess.TimeoutExpired):
                raise StageBlocked("GitHub CLI transport failed or timed out") from None
        raw = completed.stdout
        statuses = HTTP_STATUS.findall(raw)
        need(statuses, "GitHub CLI response lacked HTTP status")
        status = int(statuses[-1])
        # -i includes header blocks; parse only the last body, not headers.
        chunks = re.split(r"\r?\n\r?\n", raw)
        response_body = chunks[-1].strip()
        try:
            parsed = json.loads(response_body) if response_body else {}
        except (ValueError, UnicodeDecodeError):
            raise StageBlocked("Invalid GitHub API JSON body") from None
        need(type(parsed) is dict, "Non-object GitHub API response")
        # Return real provider status, including 403 and 404 distinctly.
        # Caller enforces expected status and treats no write as implicit.
        return (status, parsed)


class CleanPublicGitPatchMaterializer:
    """Apply an exact patch to a CLEAN, ephemeral Git checkout (never push).

    The production clone base is public https://github.com. A fixture-only
    alternate base may be injected by tests; not by an untrusted proposal.
    Every command is argv-only, never shell=True. The result is later
    checked against exact postimage hashes by RESTMultifilePatchPort.
    """

    def __init__(self, *, runner=subprocess.run,
                 clone_base="https://github.com"):
        need(callable(runner) and type(clone_base) is str
             and clone_base and "\x00" not in clone_base,
             "Trusted git runner and source host required")
        self._runner = runner
        self._clone_base = clone_base.rstrip("/")

    def _run(self, args, *, cwd=None, timeout=120):
        try:
            p = self._runner(args, cwd=cwd, capture_output=True,
                             text=True, check=False, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            raise StageBlocked("Isolated git materialization unavailable") from None
        need(p.returncode == 0,
             "Isolated git checkout or patch validation failed")
        return p.stdout

    def __call__(self, repo, base_sha, patch_text, changed_paths):
        repo = _repo(repo)
        need(repo.startswith("opensiro-contributions/")
             and type(base_sha) is str and SHA.fullmatch(base_sha)
             and type(patch_text) is str
             and 0 < len(patch_text.encode()) <= 131072
             and type(changed_paths) is list
             and len(changed_paths) == 2
             and len(set(changed_paths)) == 2
             and all(type(path) is str and len(path) <= 200 and
                     path.startswith("packages/") and
                     ".." not in path and "//" not in path and
                     all(part not in ("", ".", "..") for part in path.split("/"))
                     for path in changed_paths),
             "Materialization scope invalid")
        with tempfile.TemporaryDirectory(prefix="opensiro-materialize-") as tmp:
            root = Path(tmp) / "repo"
            repo_url = self._clone_base + "/" + repo + ".git"
            self._run(["git", "clone", "--quiet", "--no-checkout", "--depth", "1",
                       "--filter=blob:none", repo_url, str(root)], timeout=120)
            self._run(["git", "-C", str(root), "fetch", "--quiet", "--depth", "1",
                       "origin", base_sha], timeout=120)
            self._run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                       "checkout", "--detach", base_sha], timeout=90)
            need(self._run(["git", "-C", str(root), "rev-parse", "HEAD"]).strip()
                 == base_sha, "Checkout SHA differs from authorized base")
            need(not self._run(["git", "-C", str(root), "status", "--porcelain"]),
                 "Working checkout not clean")
            original_modes = {}
            for p in changed_paths:
                f = root / p
                if f.is_symlink():
                    raise StageBlocked("Symlink path cannot be patched")
                if f.exists():
                    need(f.is_file(), "Cannot patch non-regular path")
                    ls = self._run(["git", "-C", str(root), "ls-files", "-s",
                                    "--", p]).strip()
                    need(ls.startswith("100644 "),
                         "Preimage was not an ordinary 100644 blob")
                else:
                    need("/test/" in p, "Only new test file may be absent")
                original_modes[p] = "100644"
            patch_path = Path(tmp) / "candidate.patch"
            patch_path.write_text(patch_text, encoding="utf-8")
            self._run(["git", "-C", str(root), "apply", "--check",
                       str(patch_path)])
            self._run(["git", "-C", str(root), "apply", str(patch_path)])
            self._run(["git", "-C", str(root), "add", "--", *changed_paths])
            actual = self._run(["git", "-C", str(root),
                                "diff", "--cached", "--name-only", "-z"])
            need(sorted(x for x in actual.split("\x00") if x)
                 == sorted(changed_paths),
                 "Actual staged patch changed an unexpected path")
            self._run(["git", "-C", str(root), "diff", "--cached", "--check"])
            status_files = self._run(["git", "-C", str(root),
                                      "status", "--porcelain", "--untracked-files=all"])
            need(len(status_files.splitlines()) == 2,
                 "Untracked or unauthorized file remained after patch")
            outputs = {}
            for p in changed_paths:
                path = root / p
                need(path.is_file() and not path.is_symlink()
                     and stat.S_ISREG(path.stat().st_mode),
                     "Patched path is not an ordinary file")
                staged = self._run(["git", "-C", str(root), "ls-files",
                                    "-s", "--", p]).strip()
                need(staged.startswith("100644 "),
                     "Patch changed executable/symlink/submodule mode")
                binary = path.read_bytes()
                need(len(binary) <= 131072,
                     "Postimage exceeds admissible size")
                try:
                    outputs[p] = binary.decode("utf-8")
                except UnicodeDecodeError:
                    raise StageBlocked("Patch resulted in binary/non-UTF8 file") from None
            return {"base_sha": base_sha, "changed_paths": list(changed_paths),
                    "source_file_modes": original_modes, "files": outputs}
