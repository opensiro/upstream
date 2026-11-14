"""Read-only source-pinned check of Sailry spawn_agent machine-readable schema.

This is NOT a native Rust integration test. Cargo integration requires the
first-party workspace's full dependency graph and its pinned git dependencies.
"""
from pathlib import Path
import json,re,hashlib,os
root=Path(os.environ.get('OPENSIRO_BATCH40_ROOT', Path.cwd())).resolve()
repo=root/'sources/sailry__sailry-harness'
tools=repo/'crates/node-runtime/src/agent/delegation/tools.rs'
modes=repo/'crates/node-runtime/src/agent/prompt/modes.rs'
a=tools.read_text()
b=modes.read_text()
assert 'fn parameters() -> Value' in a
part=a.split('fn parameters() -> Value',1)[1].split('/// Selection metadata',1)[0]
hit=re.search(r'json!\(\s*(\{.*?\})\s*\)',part,re.S)
assert hit,'missing source json! schema'
raw=re.sub(r',\s*(?=[}\]])','',hit.group(1))
uuid_pattern=re.search(r'const UUID: &str = "([^"]+)";',a)
assert uuid_pattern
raw=raw.replace(':UUID',':'+json.dumps(uuid_pattern.group(1)))
schema=json.loads(raw)
assert schema['type']=='object'
assert schema['required']==['task']
assert {'session','role','task','title','background','worktree'}==set(schema['properties'])
assert schema.get('additionalProperties') is False
assert not any('file' in k or 'path' in k for k in schema['properties'])
assert 'disjoint file ownership' in b
assert 'concurrent edits need disjoint files or separate worktrees' in a
r={'name':'sailry-spawn-machine-readable-owned-file-absence','source':'sailry/sailry-harness',
    'pin':'eaad1b7f18e448c8c4e9e9286e19560c8a351ae1',
    'method':'exact pinned Rust source json! macro extraction + JSON schema validation, no Rust execution',
    'source_sha256':{tools.relative_to(repo).as_posix():hashlib.sha256(tools.read_bytes()).hexdigest(),modes.relative_to(repo).as_posix():hashlib.sha256(modes.read_bytes()).hexdigest()},
    'schema_required':schema['required'],'schema_properties':sorted(schema['properties']),
    'has_owned_files_field':False,
    'free_text_disjoint_instruction':True,
    'worktree_selector_present':True,
    'source_finding':'No machine-readable per-child owned-file scope in spawn_agent arguments; prompt explicitly asks disjoint ownership, worktree may isolate. This alone does not prove a runtime collision.',
    'native_status':'BLOCKED: cargo test --locked waited on gpui-fast and wezterm git dependencies and timed out; original failure receipt retained.'}
path=root/'receipts/sailry-spawn-machine-readable-owned-file-absence.json'
path.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
