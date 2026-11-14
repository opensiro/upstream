import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
if(!process.env.HAPPYHANDS_ROOT)throw Error('Set HAPPYHANDS_ROOT to a checked-out ShuaiMXu/happyhands source root, pinned to 04e75765fa92e662dd6158d2920fd72e06ff25fe');
const {collectExperienceCase,admitExperienceCase,relatedExperienceCases,experienceCaseBrief,verifyExperienceCaseBrief,listExperienceCases}=await import(pathToFileURL(join(resolve(process.env.HAPPYHANDS_ROOT),'packages/harness-core/experience-cases.js')).href);
const dir=await mkdtemp(join(tmpdir(),'happyhands-native-ranking-'));
try {
 const runs=join(dir,'runs');await mkdir(runs);
 const peers=[];
 for(let i=0;i<21;i++){
   const directory=join(runs,'peer-'+i);await mkdir(directory);
   for(const phase of ['before','after']){await mkdir(join(directory,phase));await writeFile(join(directory,phase,'desktop.png'),'synthetic screenshot');}
   await writeFile(join(directory,'experience.json'),'{}');
   const run={directory,manifest:{id:'peer-'+i,onboarding:{repository:{root:'/fixture/project',commit:'source-pin'}},captures:{before:{viewports:{desktop:{screenshot:'before/desktop.png'}}},after:{viewports:{desktop:{screenshot:'after/desktop.png'}}}},judgment:{decision:'reject',reason:'Synthetic rejected change'}}};
   const {id}=await collectExperienceCase(run);peers.push({run,id});
 }
 const sorted=[...peers].sort((a,b)=>a.id.localeCompare(b.id));
 const matching=sorted.at(-1);
 for(const {run,id} of peers){await admitExperienceCase(run,{id,kind:'regressed',reason:'Synthetic task-specific regression case',tags:id===matching.id?['renewal']:['billing']});await writeFile(join(run.directory,'run.json'),JSON.stringify(run.manifest));}
 const next={directory:join(runs,'current'),manifest:{onboarding:{repository:{root:'/fixture/project',commit:'source-pin'}}},spec:{project:{task:'Improve renewal flow'}}};
 await mkdir(next.directory);
 const old=await relatedExperienceCases(next);
 assert.equal(old.length,20);assert.equal(old.filter(x=>x.tags.includes('renewal')).length,0);
 const brief=await experienceCaseBrief(next);
 await verifyExperienceCaseBrief(next,brief);
 assert.equal(old.filter(x=>x.tags.includes('billing')).length,20);
 next.spec.project.task='Improve billing flow';
 const billing=await relatedExperienceCases(next);assert.deepEqual(billing,old);
 next.manifest.onboarding.repository.root='/fixture/other';assert.equal((await relatedExperienceCases(next)).length,0);
 const accepted=[];
 for(const {run,id} of peers){
   const current=(await listExperienceCases(run,{acceptedOnly:true})).find(x=>x.id===id);
   assert.ok(current?.current);accepted.push({caseId:id,tags:current.admission.tags,kind:current.admission.kind});
 }
 const words=s=>String(s).toLowerCase().match(/[\p{L}\p{N}]+/gu)||[];
 const score=(row,task)=>row.tags.reduce((n,tag)=>{
   const term=words(tag).join(' ');const hay=words(task).join(' ');
   return n+(term&&(' '+hay+' ').includes(' '+term+' ')?1:0);
 },0);
 const choose=task=>[...accepted].sort((a,b)=>score(b,task)-score(a,task)||a.caseId.localeCompare(b.caseId)).slice(0,20);
 assert.equal(choose('Improve renewal flow').filter(x=>x.tags.includes('renewal')).length,1);
 assert.equal(choose('Improve billing flow').filter(x=>x.tags.includes('renewal')).length,0);
 assert.equal(choose('irrelevant-no-matching-task').filter(x=>x.tags.includes('renewal')).length,0);
 const proposed={renewalSelected:choose('Improve renewal flow').filter(x=>x.tags.includes('renewal')).length,billingSelected:choose('Improve billing flow').filter(x=>x.tags.includes('renewal')).length,noMatchBackwardCompatible:choose('irrelevant-no-matching-task').map(x=>x.caseId).join(',')===old.map(x=>x.caseId).join(',')};
 console.log(JSON.stringify({nativeSource:'ShuaiMXu/happyhands@04e75765fa92e662dd6158d2920fd72e06ff25fe',scenario:'21 current explicitly admitted synthetic negative cases, same project',renewalTask:{oldCount:old.length,renewalIncluded:old.filter(x=>x.tags.includes('renewal')).length,billingIncluded:old.filter(x=>x.tags.includes('billing')).length},billingTaskSameSet:JSON.stringify(billing)===JSON.stringify(old),foreignProjectCount:0,digestVerification:'PASS',researchOnlyComparator:proposed,limit:20,result:'BASELINE_REPRODUCED_NOT_PRODUCT_BENEFIT'},null,2));
}finally{await rm(dir,{recursive:true,force:true});}