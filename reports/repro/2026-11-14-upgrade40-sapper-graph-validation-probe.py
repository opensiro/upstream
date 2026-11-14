"""First-party CLI check: `validate` is graph integrity, not independent truth verification."""
from pathlib import Path
import tempfile,subprocess,hashlib,json,os
root=Path(os.environ.get("OPENSIRO_BATCH40_ROOT", Path.cwd())).resolve()
p=root/'sapper-readonly/sapper.py'
assert p.is_file()
records=[]
with tempfile.TemporaryDirectory(prefix='sapper-b40-') as tmp:
    calls=[['init','--goal','No live network or target systems'],
           ['fact','Claim intentionally untested: X caused Y','--kind','note','--json'],
           ['validate'],['graph','--format','json']]
    for command in calls:
        proc=subprocess.run(['python3',str(p),'--store',tmp,*command],capture_output=True,text=True,timeout=20)
        records.append({'args':command,'exit_code':proc.returncode,'stdout':proc.stdout[-1100:],'stderr':proc.stderr[-400:]})
        assert proc.returncode==0,(command,proc.stderr)
    graph=json.loads(records[-1]['stdout'])
    assert any('Claim intentionally untested:' in x.get('description','') for x in graph['facts'])
record={'name':'sapper-native-graph-validate-vs-truth','pin':'7b75e6f1f5d5b4ae0c55878b0dd0994d9b08f1fb',
        'cli_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'scenario':'store an explicitly untested claim as a note using original CLI, validate native graph schema, inspect JSON result',
        'status':'PASS: validate returns zero although semantic fact truth is unassessed',
        'scope':'expected command contract; NOT a validation defect without product need for automatic source corroboration',
        'commands':records}
(root/'receipts/sapper-native-graph-validate-vs-truth.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'results':[(x['args'][0],x['exit_code']) for x in records]},indent=2))
