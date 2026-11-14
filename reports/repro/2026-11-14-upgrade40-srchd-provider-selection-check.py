"""Offline Node execution of pinned first-party srchd web.ts with stubbed network dependencies.

No API keys, no changes to upstream, no claims about live provider quality.
"""
from pathlib import Path
import json,os,subprocess,tempfile,hashlib,urllib.request,time
base=Path(os.environ.get('OPENSIRO_BATCH40_ROOT', Path.cwd())).resolve()
sha="4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08"
src=base/"scratch/srchd-pinned-web.ts"
src.parent.mkdir(parents=True,exist_ok=True)
if not src.exists():
  url=f"https://raw.githubusercontent.com/dust-tt/srchd/{sha}/src/tools/web.ts"
  src.write_bytes(urllib.request.urlopen(url,timeout=45).read())
assert "new Firecrawl" in src.read_text() and "createWebServer" in src.read_text()
def write(root,name,text):
  p=root/name
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(text,encoding="utf-8")
with tempfile.TemporaryDirectory(prefix="srchd-b40-native-") as t:
  work=Path(t)
  write(work,"package.json",'{"type":"module"}')
  write(work,"src/tools/web.ts",src.read_text())
  write(work,"src/tools/constants.js", "export const WEB_SERVER_NAME='stub-web';")
  write(work,"resolve-loader.mjs", "export async function resolve(specifier,context,nextResolve){return nextResolve(specifier==='./constants' ? './constants.js' : specifier,context)}")
  packages={
    "zod":({"type":"module","exports":{".":"./index.js"}},{"index.js":"export const z={string:()=>({describe(){return this},default(){return this}}),number:()=>({describe(){return this},default(){return this}})};"}),
    "@modelcontextprotocol/sdk":({"type":"module","exports":{"./server/mcp.js":"./server/mcp.js"}},{"server/mcp.js":"export class McpServer {constructor(settings){this.settings=settings;this.tools=new Map()}tool(name,description,schema,fn){this.tools.set(name,fn)}}"}),
    "@mendable/firecrawl":({"type":"module","exports":{".":"./index.js"}},{"index.js":"export default class Firecrawl {constructor(options){globalThis.__firecrawl.push(options)}async scrape(url){return {markdown:'fetched:'+url}}async search(query,{limit}){return {web:[{url:'https://test.invalid/1',title:'F',description:query+'@'+limit}]}}}"}),
    "@app/lib":({"type":"module","exports":{"./mcp":"./mcp.js","./error":"./error.js"}},{"mcp.js":"export const errorToCallToolResult=(err)=>({isError:true,error:err});","error.js":"export const err=(code,message,error)=>({code,message,error})"}),
    "@app/tools":({"type":"module","exports":{"./constants":"./constants.js"}},{"constants.js":"export const WEB_SERVER_NAME='stub-web';"}),
  }
  for pkg,(meta,parts) in packages.items():
    write(work/f"node_modules/{pkg}","package.json",json.dumps(meta))
    for name,body in parts.items():write(work/f"node_modules/{pkg}",name,body)
  write(work,"scenario.mjs",'''import assert from 'node:assert/strict';
globalThis.__firecrawl=[];
const {createWebServer}=await import('./src/tools/web.ts');
const results=[];
for(const provider of ['', 'linkup']){
  if(provider){process.env.WEB_PROVIDER=provider;process.env.SRCHD_WEB_PROVIDER=provider;}
  else {delete process.env.WEB_PROVIDER;delete process.env.SRCHD_WEB_PROVIDER;}
  process.env.FIRECRAWL_API_KEY='offline-test-placeholder';
  const before=globalThis.__firecrawl.length;
  const s=await createWebServer();
  assert.equal(s.tools.has('search'),true);
  assert.equal(s.tools.has('fetch'),true);
  assert.equal(globalThis.__firecrawl.length,before+1,'Firecrawl is instantiated');
  const searched=await s.tools.get('search')({query:'pubmed',count:2});
  const fetched=await s.tools.get('fetch')({url:'https://example.invalid',offset:0,length:8192});
  assert.equal(searched.isError,false);
  assert.equal(fetched.isError,false);
  assert.match(searched.content[0].text,/pubmed@2/);
  assert.match(fetched.content[0].text,/fetched:/);
  results.push({provider:provider||'default',firecrawl_instantiated:globalThis.__firecrawl.length-before,search_works:true,fetch_works:true});
}
console.log(JSON.stringify(results));
''')
  node=Path(os.environ.get("OPENSIRO_BATCH40_NODE",str(base/".toolchains/node-v22.23.5-linux-x64/bin/node")))
  start=time.monotonic()
  p=subprocess.run([str(node),"--experimental-loader",str(work/"resolve-loader.mjs"),"--experimental-strip-types",str(work/"scenario.mjs")],cwd=work,env=os.environ.copy(),capture_output=True,text=True,timeout=30)
  results=json.loads(p.stdout) if p.returncode==0 else []
  record={"name":"srchd-original-web-provider-selection-falsifier","source":"dust-tt/srchd","pin":sha,"pinned_source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"technique":"Execute exact pinned TypeScript src/tools/web.ts under Node 22 with mocks only for network/client imports and McpServer; no modification to target source","command":"node --experimental-loader resolve-loader.mjs --experimental-strip-types scenario.mjs (generated offline stubs)","exit_code":p.returncode,"seconds":round(time.monotonic()-start,2),"results":results,"stderr":p.stderr[-1100:],"limitation":"External provider HTTP not exercised; no comparative benefit or target maintainer acceptance inferred from this probe."}
  (base/"receipts/srchd-native-provider-selection-falsifier.json").write_text(json.dumps(record,indent=2)+"\n")
  print(json.dumps(record,indent=2))
