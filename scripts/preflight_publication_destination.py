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


def is_feature_template(entry):
    if not isinstance(entry, dict):
        return False
    if "feature_request" in entry:
        return entry["feature_request"] is True
    name = entry.get("name", "").lower()
    return "feature" in name and "request" in name


def route_errors(target, original, kind, purpose, repo, templates=None, config=None, categories=None, verified_blank_issue=False):
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
            if verified_blank_issue is True and not templates and config is None:
                pass  # Verified effective absence, not an unknown response.
            elif templates is None:
                errors.append("ISSUE_CHANNEL_EVIDENCE_UNVERIFIED")
            else:
                feature_template = any(is_feature_template(x) for x in templates)
                if config is None and not feature_template:
                    errors.append("ISSUE_CHANNEL_EVIDENCE_UNVERIFIED")
                discussion_route = bool(re.search(
                    r"(?is)https?://github\.com/[^/\s\"']+/[^/\s\"']+/discussions/"
                    r"(?:categories/[^ \n\"']*feature|[^ \n\"']*feature)", config or ""))
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
    if not title.strip():
        errors.append("NATIVE_FEATURE_TITLE_MISSING")
    # GitHub Issue Form's title: field is a suggested default, not an
    # immutable prefix constraint. Preserve it in evidence, not as a veto.
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


def expected_source_head_errors(expected, actual):
    """Require same observed original default-branch SHA for publication attempts."""
    if not expected or not re.fullmatch(r"[0-9a-f]{40}", expected):
        return ["ORIGINAL_SOURCE_HEAD_NOT_PINNED"]
    if not actual or not re.fullmatch(r"[0-9a-f]{40}", actual):
        return ["ORIGINAL_SOURCE_HEAD_NOT_VERIFIED"]
    if expected != actual:
        return ["ORIGINAL_SOURCE_HEAD_DRIFTED"]
    return []


def markdown_feature_template_requirements(text):
    """Fail closed on unrecognized legacy Markdown Issue Template frontmatter."""
    if not text or not re.match(r"(?s)^---\n.+?\n---\n", text):
        raise ValueError("MARKDOWN_FEATURE_FRONTMATTER_MISSING")
    head = text.split("---", 2)[1]
    if not re.search(r"(?mi)^name:\s*feature request\s*$", head):
        raise ValueError("MARKDOWN_FEATURE_TEMPLATE_IDENTITY_UNVERIFIED")
    headings = re.findall(r"(?m)^## (.+?)\s*$", text)
    if not headings:
        raise ValueError("MARKDOWN_FEATURE_SECTIONS_UNVERIFIED")
    return {"required_sections": headings}


def markdown_feature_payload_errors(spec, body):
    errors = []
    for label in spec["required_sections"]:
        match = re.search(r"(?ms)^##\s+" + re.escape(label)
                          + r"\s*$\n(.*?)(?=^## |\Z)", body)
        if not match:
            errors.append("NATIVE_MARKDOWN_FEATURE_SECTION_MISSING: "+label)
            continue
        content = re.sub(r"(?s)<!--.*?-->", "", match.group(1)).strip()
        if not content or content.upper() in ("NOT_ENOUGH_INFO", "TBD", "N/A"):
            errors.append("NATIVE_MARKDOWN_FEATURE_SECTION_UNFILLED: "+label)
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


def pinned_head(repo, branch):
    if not branch:
        raise RuntimeError("DEFAULT_BRANCH_UNVERIFIED")
    sha = gh_api(f"repos/{repo}/branches/{branch}")["commit"]["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise RuntimeError("DEFAULT_BRANCH_HEAD_UNVERIFIED")
    return sha


def resolve_issue_templates(target, source_head):
    """Local directory takes precedence; never mix local and inherited forms."""
    templates = get_optional_templates(target, source_head)
    config = get_optional_file(target, ".github/ISSUE_TEMPLATE/config.yml", source_head)
    source, ref = target, source_head
    if templates is None and config is None:
        for path in (".github/ISSUE_TEMPLATE.md", "ISSUE_TEMPLATE.md", "docs/ISSUE_TEMPLATE.md"):
            if get_optional_file(target, path, source_head) is not None:
                raise RuntimeError("LOCAL_LEGACY_ISSUE_TEMPLATE_REQUIRES_REVIEW")
        defaults = target.split("/", 1)[0] + "/.github"
        if defaults != target:
            try:
                default_repo = gh_api("repos/" + defaults)
            except RuntimeError as error:
                if "404" in str(error) or "Not Found" in str(error):
                    return templates, config, source, ref
                raise
            if (default_repo.get("full_name") != defaults or
                    default_repo.get("private") is not False or
                    default_repo.get("disabled") is not False):
                raise RuntimeError("PUBLIC_DEFAULT_COMMUNITY_REPOSITORY_UNVERIFIED")
            source, ref = defaults, pinned_head(defaults, default_repo.get("default_branch"))
            templates = get_optional_templates(source, ref)
            config = get_optional_file(source, ".github/ISSUE_TEMPLATE/config.yml", ref)
    return templates, config, source, ref


def classify_issue_templates(templates, source, ref):
    if templates is None:
        return None, {}
    classified, contents = [], {}
    for entry in templates:
        name = entry.get("name", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+\.(?:ya?ml|md)", name, re.I):
            continue
        if name.lower() in ("config.yml", "config.yaml"):
            continue
        if entry.get("type") != "file":
            raise RuntimeError("ISSUE_TEMPLATE_FILE_UNVERIFIED")
        template = get_optional_file(source, ".github/ISSUE_TEMPLATE/" + name, ref)
        if template is None:
            raise RuntimeError("ISSUE_TEMPLATE_CONTENT_UNVERIFIED")
        if name.lower().endswith(".md"):
            match = re.match(r"(?s)^---\n(.+?)\n---\n", template)
            header = match.group(1) if match else ""
        else:
            header = template
        feature = bool(re.search(r"(?mi)^name:[ \t]*[\"']?feature[ \t]+request[\"']?[ \t]*$", header))
        # Some maintainers call the canonical feature-request form "Idea".
        # Require both the verified native form name and conventional filename;
        # an arbitrary Idea form or a misleading filename alone is insufficient.
        if not feature and re.fullmatch(r"feature[_-]request\.ya?ml", name, re.I):
            feature = bool(re.search(r"(?mi)^name:[ \t]*[\"']?idea[\"']?[ \t]*$", header))
        classified.append({**entry, "feature_request": feature})
        contents[name] = template
    return classified, contents


def verify_blank_issue_route(target, original_pin, templates, config, source, ref):
    """Require no local/inherited form or config and provider-confirmed effective absence."""
    if templates or config is not None:
        return False
    for repo, pin in sorted({(target, original_pin), (source, ref)}):
        for path in (".github/ISSUE_TEMPLATE/config.yaml", ".github/ISSUE_TEMPLATE.md",
                     "ISSUE_TEMPLATE.md", "docs/ISSUE_TEMPLATE.md"):
            if get_optional_file(repo, path, pin) is not None:
                return False
    owner, name = target.split("/", 1)
    query = ("query($owner:String!,$name:String!){repository(owner:$owner,name:$name)"
             "{nameWithOwner hasIssuesEnabled issueTemplates{name filename} "
             "defaultBranchRef{target{oid}}}}")
    call = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}",
         "-f", f"owner={owner}", "-f", f"name={name}"],
        text=True, capture_output=True, check=False)
    if call.returncode:
        raise RuntimeError("EFFECTIVE_ISSUE_TEMPLATES_READ_FAILED")
    result = json.loads(call.stdout)
    repo = (result.get("data") or {}).get("repository") or {}
    if result.get("errors") or repo.get("nameWithOwner") != target:
        raise RuntimeError("EFFECTIVE_ISSUE_TEMPLATES_UNVERIFIED")
    return (repo.get("hasIssuesEnabled") is True
            and repo.get("issueTemplates") == []
            and ((repo.get("defaultBranchRef") or {}).get("target") or {}).get("oid") == original_pin)


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
    parser.add_argument("--source-head", help="original default-branch HEAD used in the draft")
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
            verified_blank_issue = False
            if args.kind == "original_issue":
                original_pin = pinned_head(args.target, repo.get("default_branch"))
                templates, config, template_repo, ref = resolve_issue_templates(
                    args.target, original_pin)
                verified_blank_issue = verify_blank_issue_route(
                    args.target, original_pin, templates, config, template_repo, ref)
                templates, template_contents = classify_issue_templates(templates, template_repo, ref)
                proof["issue_template_source"] = {
                    "repository": template_repo, "commit": ref,
                    "inherited": template_repo != args.target,
                    "blank_issues_explicitly_enabled": bool(re.search(
                        r"(?mi)^blank_issues_enabled:[ \t]*true[ \t]*$", config or "")),
                    "config_url": (f"https://github.com/{template_repo}/blob/{ref}/.github/ISSUE_TEMPLATE/config.yml"
                                   if config is not None else None)}
            elif args.kind == "original_discussion":
                categories = get_categories(args.target)
            errors = route_errors(args.target, args.original, args.kind, args.purpose,
                                  repo, templates, config, categories, verified_blank_issue)
            if args.kind == "original_issue" and not errors and verified_blank_issue:
                proof["native_blank_issue"] = {
                    "url": f"https://github.com/{args.target}/issues/new",
                    "effective_templates": [], "required_fields": [],
                    "required_checkboxes": [], "source_head": original_pin,
                    "provider_rule": "https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue"}
                if bool(args.title_file) != bool(args.body_file):
                    errors.append("TITLE_AND_BODY_REQUIRED_TOGETHER")
                elif args.title_file and args.body_file:
                    from pathlib import Path
                    if not Path(args.title_file).read_text().strip() or not Path(args.body_file).read_text().strip():
                        errors.append("BLANK_ISSUE_TITLE_OR_BODY_MISSING")
            if args.kind == "original_issue" and not errors and not verified_blank_issue:
                form_names = [x.get("name") for x in templates or []
                              if is_feature_template(x)]
                if len(form_names) != 1:
                    errors.append("FEATURE_REQUEST_FORM_NOT_UNIQUE")
                else:
                    from pathlib import Path
                    path = ".github/ISSUE_TEMPLATE/" + form_names[0]
                    template = template_contents[form_names[0]]
                    proof["issue_template_source"]["template_url"] = (
                        f"https://github.com/{template_repo}/blob/{ref}/{path}")
                    if path.lower().endswith(".md"):
                        spec = markdown_feature_template_requirements(template)
                        proof["native_markdown_feature_template"] = {"path": path, **spec}
                        if args.title_file and args.body_file:
                            errors.extend(markdown_feature_payload_errors(
                                spec, Path(args.body_file).read_text()))
                    else:
                        spec = feature_form_requirements(template)
                        proof["native_feature_form"] = {"path": path, **spec}
                        proof["human_signoff_requires_real_review"] = any(
                            re.search(r"(?i)human", v) for v in spec["required_checkboxes"])
                        if args.title_file and args.body_file:
                            errors.extend(feature_form_payload_errors(
                                spec, Path(args.title_file).read_text(),
                                Path(args.body_file).read_text()))
                    if bool(args.title_file) != bool(args.body_file):
                        errors.append("TITLE_AND_BODY_REQUIRED_TOGETHER")
            if args.title_file or args.body_file or args.source_head:
                current_original = (gh_api("repos/" + args.original) if args.original != args.target
                                    else repo)
                original_branch = current_original.get("default_branch")
                if not original_branch:
                    errors.append("ORIGINAL_DEFAULT_BRANCH_NOT_VERIFIED")
                else:
                    current_head = gh_api("repos/" + args.original + "/branches/" +
                                          original_branch)["commit"]["sha"]
                    proof["current_original_head"] = current_head
                    errors.extend(expected_source_head_errors(args.source_head, current_head))
                    if args.kind == "original_issue" and current_head != original_pin:
                        errors.append("ORIGINAL_SOURCE_HEAD_DRIFTED_DURING_PREFLIGHT")
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
    proof["other_gates"] = ("When checking an actual publication body supply exact --source-head "
                            "to fail on original default-branch drift. "
                            "Original Issue forms need --title-file and --body-file before posting. "
                            "Checked human signoffs are not proof of real human reading. "
                            "Still verify human intent, "
                            "current source, license, duplicate search, body template, "
                            "policy, legal rights, freshness and publisher identity.")
    print(json.dumps(proof, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
