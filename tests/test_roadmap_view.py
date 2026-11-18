"""Offline tests of read-only roadmap case discovery; no real GitHub calls."""
import base64
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError
from roadmap_view import roadmap_view, markdown, extract_status

META = "b" * 40
NOW = "2026-11-18T17:00:00Z"
FORK = "opensiro-contributions/example-harness"
ORIGINAL = "upstream/example-harness"
ROOT = f"/repos/{FORK}"
CASES = f"{ROOT}/contents/.opensiro/issues?ref={META}"


def file_blob(text, sha="a" * 40):
    return {"type": "file", "sha": sha, "encoding": "base64",
            "content": base64.b64encode(text.encode("utf-8")).decode("ascii")}


def state_blob(original=ORIGINAL, control="ALLOW", attention="ACTIVE"):
    record = {"schema_version": 1, "original_repository": original,
              "working_fork": FORK, "attention": attention,
              "owner_control": control, "last_event_id": None}
    return file_blob(json.dumps(record))


class Fake:
    def __init__(self):
        self.routes = {}
        self.seen = []

    def get(self, path):
        self.seen.append(path)
        item = self.routes.get(path)
        if item is None:
            raise APIError(404, "missing " + path)
        if isinstance(item, Exception):
            raise item
        return item

    def fork(self, control="ALLOW", attention="ACTIVE"):
        self.routes[ROOT] = {"fork": True, "parent": {"full_name": ORIGINAL}}
        self.routes[ROOT + "/git/ref/heads/opensiro/meta"] = {"object": {"sha": META}}
        self.routes[ROOT + "/contents/.opensiro/state.json?ref=" + META] = state_blob(
            control=control, attention=attention)
        self.routes[CASES] = []
        self.routes["/orgs/opensiro-contributions/repos?per_page=100&page=1&type=all"] = [
            {"full_name": FORK}]
        return self

    def case(self, name, files):
        self.routes[CASES].append({"type": "dir", "name": name,
                                   "path": ".opensiro/issues/" + name})
        folder = f".opensiro/issues/{name}"
        self.routes[f"{ROOT}/contents/{folder}?ref={META}"] = [
            {"type": "file", "name": fn, "path": folder + "/" + fn} for fn in files]
        for fn, text in files.items():
            self.routes[f"{ROOT}/contents/{folder}/{fn}?ref={META}"] = file_blob(text)
        return self


RECEIPT = """# Shared browser S3 roadmap

## Identity and pins
- Original repository: upstream/example-harness
## Delivery and publication
- Result: NEEDS_EVIDENCE
- External issue: DRAFT — NOT PUBLISHED
See https://github.com/upstream/example-harness/issues/582 and
https://github.com/upstream/example-harness/pull/1034
"""
HUMAN = "# Human decision\n[AI](constructor-sufficiency.md)\n"
AI = "# Technical contract\n[Human](issue.md)\n"


class RoadmapViewTests(unittest.TestCase):
    def test_canonical_case_and_original_links_unchecked_by_default(self):
        client = Fake().fork().case("resource-control-20261118", {
            "README.md": "# Roadmap",
            "issue.md": HUMAN,
            "constructor-sufficiency.md": AI,
            "roadmap.md": RECEIPT})
        report = roadmap_view(client, requested=[FORK], observed_at=NOW)
        self.assertTrue(report["coverage"]["scan_complete"])
        self.assertEqual(report["coverage"]["cases"], 1)
        case = report["cases"][0]
        self.assertEqual(case["status"], "NEEDS_EVIDENCE")
        self.assertEqual(case["structure"], "CANONICAL")
        self.assertEqual(len(case["original_links"]), 2)
        self.assertEqual({x["status"] for x in case["original_links"]}, {"NOT_CHECKED"})
        self.assertEqual(case["meta_head_sha"], META)
        self.assertIn("/blob/" + META + "/.opensiro/issues/", case["files"]["roadmap.md"])
        self.assertIn("NEEDS_EVIDENCE", markdown(report))
        self.assertTrue(all("/pulls/" not in route and "/issues/582" not in route
                            for route in client.seen))
        self.assertFalse(report["historical_inventory_complete"])

    def test_historical_pilot_is_not_duplicate_implementation(self):
        client = Fake().fork().case("capability-roadmap-issue-pilots-20261118", {
            "README.md": "# Pilot\n**Status:** PLAN_ONLY / NEEDS_EVIDENCE · DRAFT\n",
            "comparison.md": "Old vs new template",
            "issue-v2.md": "# Legacy issue"})
        report = roadmap_view(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["coverage"]["cases"], 1)
        case = report["cases"][0]
        self.assertEqual(case["kind"], "HISTORICAL_TEMPLATE_PILOT")
        self.assertEqual(case["structure"], "HISTORICAL_PILOT")
        self.assertEqual(case["status"], "NEEDS_EVIDENCE")

    def test_disposition_takes_priority_over_plan_only_route(self):
        client = Fake().fork().case("audit", {
            "README.md": "# Audit",
            "roadmap.md": RECEIPT.replace("- Result: NEEDS_EVIDENCE",
                                         "- Result: PLAN_ONLY\n- Disposition: NEEDS_EVIDENCE. Case complete")})
        case = roadmap_view(client, requested=[FORK], observed_at=NOW)["cases"][0]
        self.assertEqual(case["status"], "NEEDS_EVIDENCE")

    def test_old_roadmap_lacks_human_ai_and_stays_visible(self):
        client = Fake().fork().case("model-adaptation", {
            "README.md": "# Legacy Paperclip case\n",
            "roadmap.md": RECEIPT.replace("NEEDS_EVIDENCE", "PLAN_ONLY")})
        case = roadmap_view(client, requested=[FORK], observed_at=NOW)["cases"][0]
        self.assertEqual(case["structure"], "LEGACY_PARTIAL")
        self.assertEqual(case["status"], "PLAN_ONLY")

    def test_empty_case_directory_and_missing_meta_are_not_false_cases(self):
        client = Fake().fork()
        report = roadmap_view(client, observed_at=NOW)
        self.assertEqual(report["coverage"]["no_issues_directory"], 0)
        self.assertEqual(report["coverage"]["cases"], 0)
        del client.routes[CASES]
        report = roadmap_view(client, observed_at=NOW)
        self.assertEqual(report["coverage"]["no_issues_directory"], 1)
        self.assertTrue(report["coverage"]["scan_complete"])
        del client.routes[ROOT + "/git/ref/heads/opensiro/meta"]
        report = roadmap_view(client, observed_at=NOW)
        self.assertEqual(report["coverage"]["missing_meta"], 1)
        self.assertEqual(report["coverage"]["cases"], 0)

    def test_paused_fork_stays_visible_unless_filtered(self):
        client = Fake().fork(control="PAUSE", attention="DORMANT").case(
            "paused-case", {"README.md": "# Pause", "roadmap.md": RECEIPT})
        result = roadmap_view(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(result["cases"][0]["owner_control"], "PAUSE")
        active = roadmap_view(client, requested=[FORK], only_active=True, observed_at=NOW)
        self.assertEqual(active["coverage"]["filtered_by_attention"], 1)
        self.assertEqual(active["coverage"]["cases"], 0)

    def test_invalid_parent_or_structure_causes_partial_scan(self):
        client = Fake().fork().case("resource-control", {
            "README.md": "# Roadmap", "roadmap.md": RECEIPT})
        client.routes[ROOT]["parent"]["full_name"] = "another/source"
        report = roadmap_view(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["coverage"]["errors"], 1)
        self.assertEqual(report["coverage"]["cases"], 0)
        self.assertFalse(report["coverage"]["scan_complete"])

    def test_malformed_case_does_not_look_like_success(self):
        client = Fake().fork()
        client.routes[CASES] = [{"name": "bad/child", "type": "dir",
                                "path": ".opensiro/issues/bad/child"}]
        report = roadmap_view(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["coverage"]["errors"], 1)
        self.assertFalse(report["coverage"]["scan_complete"])

    def test_live_original_states_and_unavailable_are_distinct(self):
        client = Fake().fork().case("resource-control", {
            "README.md": "# Roadmap", "roadmap.md": RECEIPT})
        client.routes["/repos/upstream/example-harness/issues/582"] = {
            "state": "open", "updated_at": NOW}
        client.routes["/repos/upstream/example-harness/pulls/1034"] = {
            "state": "closed", "merged_at": "2026-11-18T12:00:00Z", "updated_at": NOW}
        result = roadmap_view(client, requested=[FORK], observed_at=NOW, live_original=True)
        statuses = {v["status"] for v in result["cases"][0]["original_links"]}
        self.assertEqual(statuses, {"OPEN", "MERGED"})
        client.routes["/repos/upstream/example-harness/issues/582"] = APIError(403, "rate limit")
        result = roadmap_view(client, requested=[FORK], observed_at=NOW, live_original=True)
        statuses = {v["status"] for v in result["cases"][0]["original_links"]}
        self.assertEqual(statuses, {"UNKNOWN", "MERGED"})
        self.assertFalse(result["coverage"]["scan_complete"])
        self.assertEqual(result["coverage"]["original_readback"], "PARTIAL")

    def test_reject_arbitrary_repo_and_unknown_status(self):
        with self.assertRaises(ValueError):
            roadmap_view(Fake(), requested=["foreign/repo"], observed_at=NOW)
        self.assertEqual(extract_status({"README.md": "# Only draft"}), (
            "UNKNOWN", "not explicitly recorded"))


if __name__ == "__main__":
    unittest.main()
