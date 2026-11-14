"""Read-only GitHub REST diff status controls for the batch-40 Slack hypothesis.

Public PRs only, no tokens, no cloning; the names identify external
independently visible HTTP status, not an application integration test.
"""
from pathlib import Path
import os,json,time,urllib.request,urllib.error,hashlib
root=Path(os.environ.get('OPENSIRO_BATCH40_ROOT',Path(__file__).resolve().parent)).resolve()
items=[('apache/hbase',7722,'large'),('opensiro/upstream',303,'normal')]
results=[]
for repo,num,category in items:
    url=f'https://api.github.com/repos/{repo}/pulls/{num}'
    headers={'Accept':'application/vnd.github.diff','X-GitHub-Api-Version':'2022-11-28','User-Agent':'opensiro-batch40-native-research'}
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=25) as stream:
            status=stream.status
            snippet=stream.read(400)
            content_type=stream.headers.get('Content-Type','')
    except urllib.error.HTTPError as err:
        status=err.code
        snippet=err.read(600)
        content_type=err.headers.get('Content-Type','')
    results.append({'repo':repo,'pr':num,'category':category,'status':status,'content_type':content_type,
       'sample':snippet.decode('utf8',errors='replace')[:330]})
assert results[0]['status']==406,results
assert results[1]['status']==200,results
rec={'name':'github-public-diff-size-failclosed-boundary','result':'PASS: upstream public big PR gives HTTP 406, ordinary PR HTTP 200',
 'source':'GitHub public REST diff endpoints under official diff media type',
 'observed_utc_date':'2026-11-14','method':'HTTP read-only GET with Accept application/vnd.github.diff; no user credentials',
 'cases':results,'limitation':'Not a production execution of pinned slack-agent-runtime workflow; confirms GitHub oversized diff HTTP error rather than silent success for chosen public control. Does not cover all small/partial successful diffs.'}
(root/'receipts/github-public-diff-size-failclosed-boundary.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps(rec,indent=2))
