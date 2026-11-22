#!/usr/bin/env python3
"""Read-only first-party GitHub destination/channel preflight for Roadmap proposals.

This checks only channel feasibility. A PASS never approves external publication.
"""
import argparse
import base64
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
KINDS = ("fork_issue", "original_issue", "original_discussion")


def route_errors(target, original, kind, purpose, repo, templates=None, config=None, categories=None):
    """Pure fail-closed route predicate. Pass first-party GitHub snapshots, not guesses."""
    errors = []
    if not REPO.fullmatch(target) or not REPO.fullmatch(original):
        return ["INVALID_REPOSITORY_IDENTITY"]
    if kind not in KINDS or purpose != "feature_request":
        return ["UNSUPPORTED_ACTION_OR_PURPOSE"]
    if not isinstance(repo, dict) or repo.get("full_name") != target:
        return ["REPOSITORY_IDENTITY_UNVERIFIED"]
    if repo.get("private") is not False:
        errors.append("PUBLIC_REPOSITORY_NOT_VERIFIED")
    if repo.get("archived") is not False or repo.get("disabled") is not False:
        errors.append("REPOSITORY_NOT_ACTIVE")
    if kind == "fork_issue":
        if target == original or repo.get("fork") is not True:
            errors.append("NOT_A_WORKING_FORK")
        if not isinstance(repo.get("parent"), dict) or repo["parent"].get("full_name") != original:
            errors.append("FORK_PARENT_MISMATCH")
    else:
        if target != original or repo.get("fork") is True:
            errors.append("ORIGINAL_REPOSITORY_MISMATCH")
    if kind.endswith("_issue"):
        if repo.get("has_issues") is not True:
            errors.append("ISSUES_DISABLED")
        if kind == "original_issue":
            if templates is None or config is None:
                errors.append("ISSUE_CHANNEL_EVIDENCE_UNVERIFIED")
            else:
                template_names = {x.get("name", "").lower() for x in templates
                                  if isinstance(x, dict)}
                feature_template = any("feature" in name and "request" in name
                                       for name in template_names)
                discussion_route = bool(re.search(
                    r"(?is)https?://github\.com/[^/\s\"']+/[^/\s\"']+/discussions/"
                    r"(?:categories/[^ \n\"']*feature|[^ \n\"']*feature)", config))
                if discussion_route and not feature_template:
                    errors.append("FEATURE_REQUEST_ROUTED_TO_DISCUSSIONS")
                if discussion_route and feature_template:
                    errors.append("FEATURE_REQUEST_CHANNEL_AMBIGUOUS")
                if not feature_template and not discussion_route:
                    errors.append("FEATURE_REQUEST_TEMPLATE_OR_CHANNEL_UNVERIFIED")
    elif kind == "original_discussion":
        if repo.get("has_discussions") is not True:
            errors.append("DISCUSSIONS_DISABLED")
        if categories is None:
            errors.append("DISCUSSION_CATEGORY_UNVERIFIED")
        elif not any(isinstance(c, dict) and c.get("slug") == "feature-requests" and c.get("id")
                     for c in categories):
            errors.append("FEATURE_REQUEST_DISCUSSION_CATEGORY_MISSING")
    return errors


def feature_form_requirements(text):
    """Parse conservative GitHub Issue Form subset; unknown fields fail closed."""
    if not text or not re.search(r"(?m)^body:\s*$", text):
        raise ValueError("FEATURE_FORM_BODY_UNVERIFIED")
    m = re.search(r"(?m)^title:\s*[\"']?([^\\n\"']+)", text)
    sections = re.split(r"(?m)^  - type: ", text)[1:]
    if not sections:
        raise ValueError("FEATURE_FORM_FIELDS_UNVERIFIED")
    spec = {"title_prefix": m.group(1).strip() if m else "",
            "required_fields": [], "required_checkboxes": [], "dropdown_choices": {}}
    for block in sections:
        kind = block.splitlines()[0].strip()
        if kind == "markdown":
            continue
        if kind not in ("textarea", "input", "dropdown", "checkboxes"):
            raise ValueError("UNRECOGNIZED_FEATURE_FORM_FIELD: "+kind)
        label_match = re.search(r"(?m)^      label:\s*(.+?)\s*$", block)
        if not label_match:
            raise ValueError("FORM_LABEL_MISSING")
        label = label_match.group(1).strip().strip("\"'")
        if kind == "checkboxes":
            for option in re.split(r"(?m)^        - label:\s*", block)[1:]:
                if re.search(r"(?m)^          required:\s*true\s*$", option):
                    spec["required_checkboxes"].append(option.splitlines()[0].strip().strip("\"'"))
        elif re.search(r"(?m)^      required:\s*true\s*$", block):
            spec["required_fields"].append(label)
        if kind == "dropdown":
            choices = re.findall(r"(?m)^        - (?!label:)(.+?)\s*$", block)
            spec["dropdown_choices"][label] = [v.strip().strip("\"'") for v in choices]
    return spec


def feature_form_payload_errors(spec, title, body):
    """Syntactic fit only; checked human box is not proof a human reviewed."""
    errors = []
    if spec.get("title_prefix") and not title.strip().startswith(spec["title_prefix"]):
        errors.append("NATIVE_FEATURE_TITLE_PREFIX_MISMATCH")
    for label in spec["required_fields"]:
        pattern = r"(?mi)^#{2,6}\s+" + re.escape(label) + r"\s*$\n(?:\s*\n)*([^\n]+)"
        m = re.search(pattern, body)
        if not m or m.group(1).strip().upper() in ("NOT_ENOUGH_INFO", "TBD", "N/A", ""):
            errors.append("NATIVE_FEATURE_REQUIRED_FIELD_MISSING: "+label)
        elif label in spec["dropdown_choices"] and m.group(1).strip() not in spec["dropdown_choices"][label]:
            errors.append("NATIVE_FEATURE_DROPDOWN_INVALID: "+label)
    for claim in spec["required_checkboxes"]:
        pat = r"(?m)^\s*[-*]\s+\[[xX]\]\s+" + re.escape(claim) + r"\s*$"
        if not re.search(pat, body):
            errors.append("NATIVE_FEATURE_REQUIRED_CHECKBOX_UNVERIFIED: "+claim)
    return errors


def gh_api(path):
    result = subprocess.run(["gh", "api", path], text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"FIRST_PARTY_READ_FAILED {path}: {result.stderr.strip()[:250]}")
    return json.loads(result.stdout)


def get_optional_file(repo, path, ref):
    try:
        data = gh_api(f"repos/{repo}/contents/{path}?ref={ref}")
        if data.get("encoding") != "base64":
            raise RuntimeError("UNSUPPORTED_GITHUB_CONTENT_ENCODING")
        return base64.b64decode(data["content"]).decode("utf-8")
    except RuntimeError as error:
        # Missing configuration cannot prove the requested feature channel.
        if "404" in str(error) or "Not Found" in str(error):
            return None
        raise


def get_optional_templates(repo, ref):
    try:
        data = gh_api(f"repos/{repo}/contents/.github/ISSUE_TEMPLATE?ref={ref}")
        if not isinstance(data, list):
            raise RuntimeError("ISSUE_TEMPLATES_NOT_A_DIRECTORY")
        return data
    except RuntimeError as error:
        if "404" in str(error) or "Not Found" in str(error):
            return None
        raise


def get_categories(repo):
    owner, name = repo.split("/", 1)
    query = ("query($owner:String!,$name:String!){repository(owner:$owner,name:$name)"
             "{discussionCategories(first:100){nodes{id slug name}}}}")
    call = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}",
         "-f", f"owner={owner}", "-f", f"name={name}"],
        text=True, capture_output=True, check=False)
    if call.returncode:
        raise RuntimeError("DISCUSSION_CATEGORY_READ_FAILED: " + call.stderr.strip()[:250])
    result = json.loads(call.stdout)
    if result.get("errors") or not result.get("data", {}).get("repository"):
        raise RuntimeError("DISCUSSION_CATEGORY_GRAPHQL_UNVERIFIED")
    return result["data"]["repository"]["discussionCategories"]["nodes"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="actual destination owner/repo")
    parser.add_argument("--original", required=True, help="original non-fork owner/repo")
    parser.add_argument("--kind", choices=KINDS, required=True)
    parser.add_argument("--purpose", choices=["feature_request"], default="feature_request")
    parser.add_argument("--title-file")
    parser.add_argument("--body-file")
    args = parser.parse_args()
    errors = []
    proof = {"source": "GitHub first-party gh api", "observed_at": datetime.now(timezone.utc)
             .isoformat(timespec="seconds"), "target": args.target, "original": args.original,
             "kind": args.kind, "purpose": args.purpose}
    try:
        if not REPO.fullmatch(args.target) or not REPO.fullmatch(args.original):
            errors = ["INVALID_REPOSITORY_IDENTITY"]
        else:
            repo = gh_api("repos/" + args.target)
            templates = config = categories = None
            if args.kind == "original_issue":
                ref = repo.get("default_branch")
                if not ref:
                    raise RuntimeError("DEFAULT_BRANCH_UNVERIFIED")
                templates = get_optional_templates(args.target, ref)
                config = get_optional_file(args.target, ".github/ISSUE_TEMPLATE/config.yml", ref)
            elif args.kind == "original_discussion":
                categories = get_categories(args.target)
            errors = route_errors(args.target, args.original, args.kind, args.purpose,
                                  repo, templates, config, categories)
            if args.kind == "original_issue" and not errors:
                form_names = [x.get("name") for x in templates or []
                              if re.fullmatch(r"(?i)feature[_-]request\.ya?ml", x.get("name", ""))]
                if len(form_names) != 1:
                    errors.append("FEATURE_REQUEST_FORM_NOT_UNIQUE")
                else:
                    path = ".github/ISSUE_TEMPLATE/" + form_names[0]
                    spec = feature_form_requirements(get_optional_file(args.target, path, ref))
                    proof["native_feature_form"] = {"path": path, **spec}
                    proof["human_signoff_requires_real_review"] = any(
                        re.search(r"(?i)human", v) for v in spec["required_checkboxes"])
                    if args.title_file and args.body_file:
                        from pathlib import Path
                        errors.extend(feature_form_payload_errors(
                            spec, Path(args.title_file).read_text(),
                            Path(args.body_file).read_text()))
                    elif args.title_file or args.body_file:
                        errors.append("TITLE_AND_BODY_REQUIRED_TOGETHER")
            proof["repository"] = {"full_name": repo.get("full_name"), "fork": repo.get("fork"),
                                    "parent": repo.get("parent", {}).get("full_name"),
                                    "has_issues": repo.get("has_issues"),
                                    "has_discussions": repo.get("has_discussions"),
                                    "default_branch": repo.get("default_branch")}
            if categories is not None:
                proof["category"] = next(
                    ({"id": c["id"], "name": c["name"], "slug": c["slug"]}
                     for c in categories if c.get("slug") == "feature-requests"), None)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors = ["FIRST_PARTY_DESTINATION_EVIDENCE_UNVERIFIED: " + str(exc)[:300]]
    proof["status"] = ("ROUTE_PREFLIGHT_PASS_NOT_PUBLICATION_APPROVAL" if not errors
                       else "PUBLICATION_BLOCKED_DESTINATION")
    proof["errors"] = errors
    proof["approval"] = "REQUIRES_EXACT_CURRENT_CONVERSATION_OWNER_CONSENT"
    proof["other_gates"] = ("Original Issue forms need --title-file and --body-file before posting. "
                            "Checked human signoffs are not proof of real human reading. "
                            "Still verify human intent, "
                            "current source, license, duplicate search, body template, "
                            "policy, legal rights, freshness and publisher identity.")
    print(json.dumps(proof, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
