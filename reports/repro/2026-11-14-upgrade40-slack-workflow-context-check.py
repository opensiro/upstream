"""Execute verbatim Python payload from pinned native GitHub workflow offline."""
from pathlib import Path
import tempfile,re,os,json,subprocess,hashlib
base=Path(os.environ.get('OPENSIRO_BATCH40_ROOT', Path.cwd())).resolve()
orig=base/'sources/sakomws__slack-agent-runtime/.github/workflows/pr-review-reusable.yml'
source=orig.read_text()
needle="          python - <<'PY'\n"
blocks=source.split(needle)
assert len(blocks)>=4,len(blocks)
script=blocks[2].split("          PY\n",1)[0]
script='\n'.join(line[10:] if line.startswith('          ') else line for line in script.splitlines())+'\n'
assert 'head_sha != os.environ["EXPECTED_HEAD_SHA"]' in script
assert 'changed_files' not in script and 'files' not in script
scenarios=[
    ("complete",2,"diff --git a/a.py b/a.py\n+change1\ndiff --git a/b.py b/b.py\n+change2\n","f"*40,True),
    ("incomplete",2,"diff --git a/a.py b/a.py\n+change1\n","f"*40,True),
    ("head_changed",2,"diff --git a/a.py b/a.py\n+change1\ndiff --git a/b.py b/b.py\n+change2\n","e"*40,False),
]
out=[]
with tempfile.TemporaryDirectory(prefix='batch40-slack-context-') as d:
 for key,changed,diff,actual_head,should_accept in scenarios:
    p=Path(d)/key;p.mkdir()
    (p/'pr.json').write_text(json.dumps({"title":"Two-file review","body":"Review both files","changed_files":changed,"head":{"sha":actual_head}}))
    (p/'pr.diff').write_text(diff)
    env=os.environ.copy();env.update({"RUNNER_TEMP":str(p),"CONTEXT_FILE":str(p/'context.json'),"EXPECTED_HEAD_SHA":"f"*40})
    x=subprocess.run(["python3","-c",script],env=env,text=True,capture_output=True,timeout=8)
    context_path=p/'context.json'
    actual_accept=x.returncode==0 and context_path.is_file()
    context=json.loads(context_path.read_text()) if actual_accept else None
    assert actual_accept==should_accept,(key,x.returncode,x.stderr)
    if key=="incomplete":assert context['diff'].count('diff --git')==1
    if key=="complete":assert context['diff'].count('diff --git')==2
    out.append({"scenario":key,"metadata_changed_files":changed,"diff_files":diff.count('diff --git'),"expected_head_valid":actual_head=="f"*40,"exit_code":x.returncode,"context_written":actual_accept,"stderr":x.stderr.strip()[:200]})
result={"name":"slack-pinned-native-workflow-fetch-payload","source":"sakomws/slack-agent-runtime","pin":"16bb262715b7bacb64c7466cf106063c2fdf6c93","workflow_path":".github/workflows/pr-review-reusable.yml","script_sha256":hashlib.sha256(script.encode()).hexdigest(),"assumption":"GitHub returns synthetic partial diff; NOT proof GitHub API truncates in live use.","results":out,"finding":"Pinned workflow accepts incomplete diff whose two-file PR metadata says changed_files=2 and validates HEAD; it has no changed-file inventory comparison. Complete control passes, stale SHA fails."}
path=base/'receipts/slack-workflow-metadata-counterfactual.json';path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))