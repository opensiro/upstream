from pathlib import Path
import subprocess,os,json,time,hashlib
root=Path(os.environ.get('OPENSIRO_BATCH40_ROOT', 'batch40-20261114')).resolve();out=root/'receipts';out.mkdir(parents=True, exist_ok=True)
checks={
'open-sdk-existing-mailbox':('codeany-ai__open-agent-sdk-python',r'''import asyncio
from open_agent_sdk.tools.send_message import SendMessageTool
from open_agent_sdk.tools import read_mailbox, clear_mailboxes
async def main():
    clear_mailboxes()
    tool=SendMessageTool()
    got=await tool.call({'to':'researcher','content':'handoff','type':'text'}, None)
    assert not got.is_error,got
    assert read_mailbox('researcher') == [{'type':'text','content':'handoff','from':'agent'}]
    assert read_mailbox('researcher') == [], 'mailbox drains on read'
    print('PASS: current first-party tool sends and receives; no added mailbox needed')
asyncio.run(main())'''),
'slack-partial-diff-boundary':('sakomws__slack-agent-runtime',r'''import asyncio,json
from unittest.mock import AsyncMock
from slack_agent_runtime.coding.reviewer import PullRequestReviewer
from slack_agent_runtime.inference.client import InferenceResult, InferenceUsage
async def main():
    c=AsyncMock();c.complete.return_value=InferenceResult('{"summary":"No issue in supplied diff","findings":[]}', 'model','request',3,InferenceUsage())
    review=await PullRequestReviewer(c).review(diff='diff --git a/a.py b/a.py\n+pass',title='2 file PR',body='',model='offline-test')
    assert review.event=='APPROVE'
    print('PASS: API accepts supplied partial diff and yields APPROVE when fake model has no findings; real workflow fetches actual GitHub diff and checks SHA; NOT a reproduced incomplete upstream review')
asyncio.run(main())'''),
'ai-scientist-existing-audit-schema':('SakanaAI__AI-Scientist-v3',r'''from pathlib import Path
from src.orchestrator.paper_evidence_audit import AuditFinding
from src.orchestrator import paper_feedback
from src.pipeline import revision_publication
fields=AuditFinding.model_fields
assert 'claim' in fields or any('claim' in name for name in fields),fields
source=Path('src/pipeline/revision_publication.py').read_text()
assert 'paper_evidence_audit.json' in source
print('PASS: machine-readable per-claim schema is defined; named audit JSON staged and consumed; need for separate export not demonstrated')''')
}
for name,(repo,script) in checks.items():
 cwd=root/'sources'/repo;env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(root/'.deps8'),str(root/'.deps'),str(cwd),str(cwd/'src')]);start=time.monotonic()
 try:
  p=subprocess.run(['python3','-c',script],cwd=cwd,env=env,text=True,capture_output=True,timeout=35)
  data={'name':name,'repo':repo,'pin':subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip(),'command':'python3 -c <receipt source native_falsifiers.py:'+name+'>','sha256_code':hashlib.sha256(script.encode()).hexdigest(),'exit_code':p.returncode,'seconds':round(time.monotonic()-start,2),'stdout':p.stdout,'stderr':p.stderr[-4000:]}
 except Exception as e:data={'name':name,'repo':repo,'exception':str(e)}
 (out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 print(name, data.get('exit_code'),(data.get('stdout','')+' '+data.get('stderr',''))[-250:].replace('\n',' '),flush=True)