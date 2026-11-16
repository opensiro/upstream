#!/usr/bin/env python3
"""Bounded issue-watch batch from a complete, verified fork portfolio."""
import argparse
import json
import os
from pathlib import Path
import sys
from aggregate import APIError
from issue_watch import GitHub, GitHubWriter, apply_change, load_target, observe


def discover(snapshot, max_targets=20):
    cov = snapshot.get("coverage") or {}
    if (snapshot.get("scope") != "public_organization_repositories" or
        cov.get("scan_complete") is not True or cov.get("errors") or cov.get("filtered_by_attention")):
        raise ValueError("Incomplete or filtered portfolio; refuse scheduled watch")
    targets = sorted((f["working_fork"], r["id"]) for f in snapshot["forks"]
                     for r in f["contributions"] if r.get("issue_watch"))
    if len(targets) > max_targets or len(set(targets)) != len(targets):
        raise ValueError("Too many or duplicate issue watches")
    return targets


def run(client_factory, targets, *, apply=False):
    results = []
    for fork, ident in targets:
        try:
            client = client_factory(fork, apply)
            target = load_target(client, fork, ident)
            observed = observe(client, target)
            if apply and observed["alert"]:
                observed.update(apply_change(client, target, observed,
                                  actor="OpenSiro GitHub Actions issue-watch"))
            elif observed["alert"]:
                observed["preview_only"] = True
            results.append({"fork": fork, "contribution": ident, **observed})
        except (ValueError, APIError, PermissionError, RuntimeError, OSError) as exc:
            results.append({"fork": fork, "contribution": ident, "status": "UNKNOWN",
                            "applied": False, "alert": False, "error": type(exc).__name__,
                            "details": str(exc)[:250]})
    return {"checked": len(results),
            "failures": sum(r["status"] == "UNKNOWN" for r in results),
            "persisted_alerts": sum(bool(r.get("applied")) for r in results),
            "preview_changes": sum(bool(r.get("preview_only")) for r in results),
            "observations": results}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--portfolio", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--allow-fork-write", action="store_true")
    p.add_argument("--max-targets", type=int, default=20)
    args = p.parse_args(argv)
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if args.apply and (not args.allow_fork_write or not token):
        p.error("--apply requires explicit grant and fork-scoped credential")
    try:
        targets = discover(json.loads(args.portfolio.read_text()), args.max_targets)
        result = run(lambda fork, apply: GitHubWriter(token, fork) if apply else GitHub(token),
                     targets, apply=args.apply)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({k: result[k] for k in ("checked", "failures",
                                                 "persisted_alerts", "preview_changes")}))
        for item in result["observations"]:
            if item.get("applied"):
                print("::notice::Source decision change: " +
                      ", ".join(item.get("source_links", [])))
        return 2 if result["failures"] else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        p.error(str(exc))


if __name__ == "__main__":
    sys.exit(main())
