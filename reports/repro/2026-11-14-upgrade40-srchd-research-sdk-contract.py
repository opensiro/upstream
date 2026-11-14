#!/usr/bin/env python3
"""Batch 40: invoke verbatim Firecrawl 4.35.0 ResearchClient JS through an offline fake HTTP transport.

The published SDK source is SHA512-verified first. This is an API-contract falsifier,
not a real provider invocation, product benchmark, or code intended for srchd.
"""
import base64, hashlib, io, json, os, pathlib, subprocess, tarfile, tempfile, urllib.request
from pathlib import Path

ROOT=Path(os.environ.get("OPENSIRO_BATCH40_ROOT","batch40-20261114")).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
NODE=Path(os.environ.get("OPENSIRO_BATCH40_NODE",str(ROOT/'.toolchains/node-v22.23.5-linux-x64/bin/node')))
assert NODE.exists(),f"Node executable missing: {NODE}"
version="4.35.0"
url=f"https://registry.npmjs.org/%40mendable%2Ffirecrawl/{version}"
with urllib.request.urlopen(url,timeout=30) as stream:
    meta=json.load(stream)
cache=ROOT/'.research-downloads/firecrawl-4.35.0.tgz'
cache.parent.mkdir(parents=True,exist_ok=True)
if not cache.exists():
    with urllib.request.urlopen(meta['dist']['tarball'],timeout=45) as stream:
        cache.write_bytes(stream.read())
blob=cache.read_bytes()
assert hashlib.sha512(blob).digest()==base64.b64decode(meta['dist']['integrity'].removeprefix('sha512-'))
tar=tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz')
sdk=tar.extractfile("package/dist/index.cjs").read().decode()
start=sdk.index('// src/v2/methods/research.ts')
end=sdk.index('// src/v2/methods/monitor.ts',start)
segment=sdk[start:end]
assert 'var ResearchClient = class' in segment and 'async searchPapers(' in segment
assert 'async getPaper(' in segment and 'async similarPapers(' in segment
sdk_hash=hashlib.sha256(segment.encode()).hexdigest()
script=r"""
'use strict';
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const source=fs.readFileSync(process.argv[2],'utf8');
const registry=[];
const fakeHTTP={
  async get(url) {
    registry.push(url);
    if(url.includes('/papers/') && url.includes('/similar')) return {status:200,data:{success:true,results:[]}};
    if(url.includes('/papers/')) return {status:200,data:{success:true,paper:{paperId:'88',title:'Genome',abstract:'Synthetic citation for test'}}};
    return {status:200,data:{success:true,results:[{
      paperId:'88',primaryId:'pmid:12345678',
      ids:{pmid:['12345678'],doi:['10.0000/example']},
      title:'Genome',abstract:'Synthetic abstract',score:0.87
    }]}};
  }
};
const sandbox={URLSearchParams, getVersion:()=> '4.35.0',
  SdkError: class SdkError extends Error{},
  throwForBadResponse(){throw new Error('HTTP fail closed')}};
const ResearchClient=vm.runInNewContext(source+'\nResearchClient',sandbox,{timeout:2000});
const client=new ResearchClient(fakeHTTP);
(async()=>{
 const input='tau aggregation in Parkinson disease';
 const result=await client.searchPapers(input,{k:5,authors:['A. Smith','B. Doe'],from:'2020-01-01'});
 assert.equal(result.success,true);
 assert.equal(result.results[0].primaryId,'pmid:12345678');
 assert.equal(result.results[0].url,undefined,'paper result has no web href');
 const target=registry[0];
 const parsed=new URL(target,'https://offline.invalid');
 assert.equal(parsed.pathname,'/v2/search/research/papers');
 assert.equal(parsed.searchParams.get('query'),input);
 assert.equal(parsed.searchParams.get('k'),'5');
 assert.deepEqual(parsed.searchParams.getAll('authors'),['A. Smith','B. Doe']);
 assert.equal(parsed.searchParams.get('from'),'2020-01-01');
 assert.equal(parsed.searchParams.get('origin'),'js-sdk@4.35.0');
 await assert.rejects(()=>client.searchPapers(''),/query cannot be empty/);
 await assert.rejects(()=>client.searchPapers('paper',{k:0}),/k must be positive/);
 assert.equal(registry.length,1,'invalid inputs fail before HTTP');
 const detail=await client.getPaper('pmid:12345678',{query:'treatment passage',k:2});
 assert.equal(detail.paper.paperId,'88');
 assert.match(registry[1],/pmid%3A12345678/);
 const similar=await client.similarPapers('pmid:12345678',{intent:'related biomarkers',k:3});
 assert.equal(similar.success,true);
 assert.match(registry[2],/similar/);
 const rows=[{case:'paper search',status:'PASS',path:target,primaryId:result.results[0].primaryId,hasDirectUrl:'url' in result.results[0]},
 {case:'invalid query/k fail before HTTP',status:'PASS'},
 {case:'paper detail',status:'PASS',path:registry[1]},
 {case:'related citation search',status:'PASS',path:registry[2]}];
 console.log(JSON.stringify({status:'PASS',controls:rows,transport:'offline stub only'}))
})().catch(err=>{console.error(err);process.exitCode=1});
"""
with tempfile.TemporaryDirectory(prefix="batch40-sdk-research-") as td:
    path=Path(td)
    (path/"sdk-research-slice.js").write_text(segment)
    (path/"test.cjs").write_text(script)
    proc=subprocess.run([str(NODE),str(path/"test.cjs"),str(path/"sdk-research-slice.js")],
                        text=True,capture_output=True,timeout=18)
if proc.returncode:
    raise SystemExit(f"SDK native extracted contract FAIL {proc.returncode}: {proc.stderr[:2000]}")
data=json.loads(proc.stdout)
assert data['status']=='PASS'
assert len(data['controls'])==4
assert data['controls'][0]['hasDirectUrl'] is False
receipt={
 "schema":"opensiro.upstream.batch40.srchd-research-sdk-native.v1",
 "pin":"dust-tt/srchd@4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08",
 "sdk":"@mendable/firecrawl@4.35.0",
 "npm_integrity":meta['dist']['integrity'],
 "npm_sha512_verified":True,
 "sdk_source_segment_sha256":sdk_hash,
 "runner":"Node (vm executing verbatim SDK ResearchClient class) with fake isolated HTTP transport",
 "test_status":proc.returncode,
 "control_cases":data['controls'],
 "web_contract_mismatch":"PaperResult has primaryId (e.g. pmid:), does not require a URL; cannot pass directly to srchd WebClient search output which requires a link.",
 "scope":"No live Firecrawl API call, provider keys, latency, coverage or quality. Synthetic server response verifies route encoding and input validation only. Research papers != patents.",
 "need":"PENDING",
 "mechanism":"PASS",
 "counterfactual":"PENDING",
 "scope_gate":"PENDING",
 "external_patch_admitted":False
}
out=ROOT/"receipts/srchd-research-sdk-native-contract.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
