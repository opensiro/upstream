"""Research-only native call-path check: qualification with two contradictory mocked baseline receipts.

No actual evaluator run, no fix, no claim of a reproduced stochastic model.
"""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch
import json,os,sys,tempfile,time,subprocess,hashlib

work=Path(os.environ.get('OPENSIRO_BATCH40_ROOT', Path.cwd())).resolve()
source=work/"sources/SakanaAI__AI-Scientist-v3"
sys.path[:0]=[str(work/".deps8"),str(work/".deps"),str(source)]
from src.task_drafting.qualification import qualify_task_for_publication,load_task_qualification_receipt
from src.investigation.task_runtime import TaskRuntimePreparationReport,TaskRuntimePreparationResult
from tests.final_evaluation.test_final_evaluation import _write_contract_task
results=[]
with tempfile.TemporaryDirectory(prefix="batch40-qualification-") as temp:
 root=Path(temp)
 task_dir=_write_contract_task(root)
 (root/"cache").mkdir()
 calls=[]
 def prepare(task:Path,_timeout:int,**kwargs):
  score=next(scores)
  calls.append({"score":score,"draft_smoke":kwargs["draft_smoke"],"evaluator_tree_sha256":kwargs["evaluator_tree_sha256"]})
  manifest={"schema_version":1,"image_id":"sha256:"+"2"*64,"baseline_combined_score":score,
   "baseline_correct":False,"baseline_feasible":True,"evaluator_sha256":"7"*64,
   "evaluator_tree_sha256":kwargs["evaluator_tree_sha256"],"gpu_evaluation":False,
   "cuda_visible_devices":"","sandbox_gpus":None,"requirements_sha256":"4"*64,
   "tooling_sha256":"5"*64}
  (task/".agentic_runtime.json").write_text(json.dumps(manifest),encoding="utf8")
  return TaskRuntimePreparationReport(TaskRuntimePreparationResult.READY,None,None,"","8"*64,1.25)
 scores=iter([0.41,0.62])
 with patch("src.task_drafting.publication.task_publication_plan_sha256",return_value="1"*64):
  for i in range(2):
   out=root/f"qualification-{i}";out.mkdir()
   attempt=qualify_task_for_publication(task_dir=task_dir,publication_task_dir=task_dir,output_dir=out,
    receipt_path=out/"receipt.json",timeout_seconds=100,container_image="image",container_network="none",
    install_cache_dir=root/"cache",max_runtime_bytes=1024,prepare=prepare)
   assert attempt.status=="pass",(i,attempt.status,attempt.diagnostic)
   receipt=load_task_qualification_receipt(out/"receipt.json",expected_publication_plan_sha256="1"*64)
   results.append({"status":attempt.status,"receipt_score":receipt.baseline_combined_score,
      "evaluator_tree_sha256":receipt.evaluator_tree_sha256})
 assert len(calls)==2 and calls[0]["evaluator_tree_sha256"]==calls[1]["evaluator_tree_sha256"]
 assert results[0]["receipt_score"]!=results[1]["receipt_score"]
record={"name":"ai-scientist-qualification-mock-nondeterministic-scores","source":"SakanaAI/AI-Scientist-v3",
 "source_pin":"df8313889a004f8a44a472e19a833cd547bb828a",
 "program_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 "result":"PASS (negative control: same evaluator-tree digest, two mocked score manifests, both accepted by original qualification)",
 "calls":calls,"receipts":results,
 "limitation":"Two separate qualification invocations and explicitly injected mock scores; not a native real-model or real container baseline reproducibility test. Does not establish four PASS or authorize fix."}
(work/"receipts/ai-scientist-qualification-mock-nondeterministic-scores.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps(record,indent=2))