#!/usr/bin/env python3
"""Batch-40 source-native type compatibility probe; read-only to upstream repositories.

Compare the EXACT existing contributor implementation against official SHA512-verified
Firecrawl SDK 1.21.1 and 4.35.0 type contracts; report diagnostics without modifying
the contributor's source. This is not a product quality benchmark.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

PIN = "9f183fde801a21ca925b13c7a5e2149d86093654"
AUTHOR_SHA256 = "825db8374276f561c1f5f361dc907770c2ae6cbba011e581cc720f14678f2fda"
PACKAGES = ("1.21.1", "4.35.0")
TSC_VERSION = "5.9.3"
ROOT = Path(os.environ.get("OPENSIRO_BATCH40_ROOT", "batch40-20261114")).resolve()
OUT = ROOT / "receipts"
OUT.mkdir(parents=True, exist_ok=True)
CACHE = ROOT / ".research-downloads"
CACHE.mkdir(parents=True, exist_ok=True)
NODE = Path(os.environ.get(
    "OPENSIRO_BATCH40_NODE", str(ROOT / ".toolchains/node-v22.23.5-linux-x64/bin/node")
))
if not NODE.is_file():
    system_node = shutil.which("node")
    if not system_node:
        raise SystemExit("BLOCKED: node executable missing (pass OPENSIRO_BATCH40_NODE)")
    NODE = Path(system_node)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "opensiro-batch40-repro/0.8.0"})
    with urllib.request.urlopen(request, timeout=55) as response:
        return response.read()


def verified_npm(name: str, version: str) -> tuple[bytes, str]:
    metadata = json.loads(fetch(
        f"https://registry.npmjs.org/{name.replace('/', '%2F').replace('@', '%40')}/{version}"
    ))
    integrity = metadata["dist"]["integrity"]
    if not integrity.startswith("sha512-"):
        raise RuntimeError("unsupported npm integrity algorithm")
    expected = base64.b64decode(integrity.removeprefix("sha512-"))
    cache_file = CACHE / (name.replace("/", "-").replace("@", "") + "-" + version + ".tgz")
    if not cache_file.is_file():
        cache_file.write_bytes(fetch(metadata["dist"]["tarball"]))
    data = cache_file.read_bytes()
    if hashlib.sha512(data).digest() != expected:
        raise RuntimeError(f"integrity mismatch for {name}@{version}")
    return data, integrity


author_path = CACHE / "srchd-pr203-web-providers.ts"
if not author_path.is_file():
    author_path.write_bytes(fetch(
        f"https://raw.githubusercontent.com/Tketa/srchd/{PIN}/src/tools/web-providers.ts"
    ))
author = author_path.read_bytes()
assert hashlib.sha256(author).hexdigest() == AUTHOR_SHA256, "author source SHA256 mismatch"

records = {}
with tempfile.TemporaryDirectory(prefix="opensiro-srchd-sdk-matrix-") as tmpdir:
    root = Path(tmpdir)
    src = root / "src/web-providers.ts"
    src.parent.mkdir(parents=True)
    src.write_bytes(author)
    (root / "linkup-stub.d.ts").write_text("""
declare const process: { env: Record<string, string | undefined> };
declare module "linkup-sdk" {
  export class LinkupClient {
    constructor(o: {apiKey: string});
    fetch(o: {url: string, renderJs: boolean, includeRawHtml: boolean,
      extractImages: boolean}): Promise<{content?: string}>;
    search(o: {query: string, depth: string, outputType: string,
      maxResults: number}): Promise<{results: Array<{name:string,url:string,content:string}>}>;
  }
}
""")
    types = {}
    checksums = {}
    for version in PACKAGES:
        blob, integrity = verified_npm("@mendable/firecrawl", version)
        checksums[version] = integrity
        with tarfile.open(fileobj=__import__("io").BytesIO(blob), mode="r:gz") as tf:
            declarations = tf.extractfile("package/dist/index.d.ts")
            assert declarations
            target = root / ("sdk-" + version + ".d.ts")
            target.write_bytes(declarations.read())
            types[version] = target

    tsc_blob, tsc_integrity = verified_npm("typescript", TSC_VERSION)
    compiler_dir = root / "typescript-lib"
    compiler_dir.mkdir()
    with tarfile.open(fileobj=__import__("io").BytesIO(tsc_blob), mode="r:gz") as tf:
        for entry in tf:
            if entry.isfile() and entry.name.startswith("package/lib/") and entry.size <= 12_000_000:
                target = compiler_dir / entry.name.removeprefix("package/lib/")
                target.parent.mkdir(parents=True, exist_ok=True)
                source_file = tf.extractfile(entry)
                assert source_file
                target.write_bytes(source_file.read())

    for version in PACKAGES:
        config = {
            "compilerOptions": {
                "strict": True, "skipLibCheck": True, "noEmit": True,
                "target": "ES2022", "module": "ESNext", "moduleResolution": "bundler",
                "paths": {"@mendable/firecrawl": [str(types[version])]},
            },
            "files": [str(src), str(root / "linkup-stub.d.ts")],
        }
        (root / "tsconfig.json").write_text(json.dumps(config))
        run = subprocess.run(
            [str(NODE), str(compiler_dir / "tsc.js"), "-p", str(root / "tsconfig.json"),
             "--pretty", "false"],
            cwd=root, text=True, capture_output=True, timeout=35
        )
        diagnostics = run.stdout.strip() + run.stderr.strip()
        records[version] = {"exit_code": run.returncode,
                            "error_codes": re.findall(r"error (TS\d+):", diagnostics),
                            "diagnostics": diagnostics}
    assert records["1.21.1"]["error_codes"] == ["TS2322"], records["1.21.1"]
    assert len(records["4.35.0"]["error_codes"]) == 6, records["4.35.0"]
    assert "Property 'success' does not exist on type 'Document'" in records["4.35.0"]["diagnostics"]
    assert "Property 'data' does not exist on type 'SearchData'" in records["4.35.0"]["diagnostics"]
    sdk_v4 = types["4.35.0"].read_text()
    assert "scrapeUrl(url: string, options?: ScrapeOptions): Promise<Document>" in sdk_v4
    assert "search(query: string, req?: Omit<SearchRequest" in sdk_v4
    assert "searchPapers(query: string, options?: SearchPapersOptions)" in sdk_v4
    assert "get research(): ResearchClient" in sdk_v4

result = {
    "schema": "opensiro.upstream.batch40.srchd-sdk-compat.v1",
    "batch": "40", "semver": "0.8.0",
    "frozen_batch39_ref": "8a5ebb36058140e2b84ae4fb1b0751c9b0be7d89",
    "source": "Tketa/srchd original author PR #203 branch",
    "source_ref": PIN,
    "source_file": "src/tools/web-providers.ts",
    "source_sha256": AUTHOR_SHA256,
    "target_source_ref": "dust-tt/srchd@4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08",
    "target_package_lock": "@mendable/firecrawl@4.35.0",
    "compiler": "TypeScript " + TSC_VERSION,
    "typescript_integrity": tsc_integrity,
    "sdk_integrities": checksums,
    "sdk_has_scrapeUrl_compat_alias": True,
    "sdk_has_research_searchPapers": True,
    "compilation": records,
    "scope": ("Source-native TypeScript type check of exact first-party contributor code against verified "
              "published SDK declarations with a separately declared Linkup stub. It does NOT execute "
              "Firecrawl or Linkup HTTP; no deployed effect or independently measured product gain."),
    "disposition": ("Author's existing proposal is not drop-in compatible with target lockfile; "
                    "do not duplicate their PR or claim an admitted intervention."),
}
out = OUT / "srchd-sdk-compat-lockfile-v4.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({
    "source_sha256": result["source_sha256"],
    "verified_integrity_versions": list(checksums),
    "typescript": TSC_VERSION,
    "diagnostic_counts": {v: len(records[v]["error_codes"]) for v in PACKAGES},
    "method_alias": result["sdk_has_scrapeUrl_compat_alias"],
    "research_search": result["sdk_has_research_searchPapers"],
    "receipt": str(out),
}, indent=2))
