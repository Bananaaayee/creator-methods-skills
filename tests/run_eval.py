#!/usr/bin/env python3
"""Reproducible local Codex evaluation. Private inputs stay outside the repo."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

MODEL = "gpt-6.1-sol"
EFFORT = "high"
SCHEMA = {"type":"object","properties":{"responses":{"type":"array","items":{"type":"object","properties":{"id":{"type":"string"},"answer":{"type":"string"}},"required":["id","answer"],"additionalProperties":False}}},"required":["responses"],"additionalProperties":False}

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def invoke(prompt, destination, schema=SCHEMA):
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "prompt.txt").write_text(prompt)
    (destination / "schema.json").write_text(json.dumps(schema, ensure_ascii=False))
    with tempfile.TemporaryDirectory(prefix="creator-eval-") as scratch:
        command = ["codex", "exec", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config", "-C", scratch, "-m", MODEL, "-c", f'model_reasoning_effort="{EFFORT}"', "-s", "read-only", "--json", "--output-schema", str((destination / "schema.json").resolve()), "-o", str((destination / "output.json").resolve()), "-"]
        started = time.time()
        with (destination / "events.jsonl").open("w") as output, (destination / "stderr.txt").open("w") as error:
            process = subprocess.run(command, input=prompt, text=True, stdout=output, stderr=error, timeout=1800)
        events = []
        for line in (destination / "events.jsonl").read_text().splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: pass
        usage = [e.get("usage") for e in events if e.get("type") == "turn.completed"]
        tools = [e for e in events if e.get("item",{}).get("type") not in (None,"agent_message","reasoning")]
        meta = {"model":MODEL,"reasoning_effort":EFFORT,"started_at":datetime.datetime.fromtimestamp(started, datetime.timezone.utc).isoformat(),"duration_seconds":round(time.time()-started,2),"exit_code":process.returncode,"command":command,"prompt_sha256":digest(prompt),"usage":usage,"non_message_items":tools}
        (destination / "run.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2))
        if process.returncode: raise RuntimeError(f"Evaluation failed: {destination}")
        result = json.loads((destination / "output.json").read_text())
        if tools: raise RuntimeError(f"Unexpected tool execution: {destination}")
        return result

def make_prompt(cases, method):
    prefix = "你在完成一组创作委托。下面各题相互独立，不能互相借用经历、素材或事实。只按输出schema返回每题答案，不报告评测过程。不得使用任何工具、访问文件或联网。每题通常不超过800个汉字；若题目要求更短，按题目要求。\n"
    if method:
        prefix += "使用下面完整附加方法处理委托；附加方法与题目冲突时，题目的具体要求优先。\n<method>\n" + method + "\n</method>\n"
    else:
        prefix += "未附加专门创作者方法，按你的通常专业判断完成。\n"
    return prefix + "\n<cases>\n" + json.dumps([{"id":c["id"],"prompt":c["prompt"]} for c in cases],ensure_ascii=False,indent=2) + "\n</cases>"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True, type=Path, help="Private research/output root; outside the publishable repository")
    parser.add_argument("--conditions", nargs="+", required=True, help="plain or creator:old or creator:new")
    parser.add_argument("--revision", default="r1")
    parser.add_argument("--workers", default=3, type=int)
    parser.add_argument("--spec", type=Path, help="Alternative case specification")
    parser.add_argument("--respect-targets", action="store_true", help="Use targeted regression cases only for their named creator")
    args = parser.parse_args()
    work = args.work.resolve()
    repository = work / "repo"
    spec = json.loads((args.spec or repository / "tests/cases.json").read_text())
    cases = spec["cases"]
    jobs = []
    methods = {}
    for condition in args.conditions:
        if condition == "plain": method = ""
        else:
            creator, variant = condition.split(":")
            if variant == "old":
                index = {"he-tongxue":"09A", "lawrence":"09B", "media-storm":"09C"}[creator]
                old = next((work / "private-baselines").glob(index+"*"))
                method = next((old / "dist").glob("*.md")).read_text()
            else:
                method = next((repository / "creators" / creator / "dist").glob("*.md")).read_text()
        methods[condition] = method
        selected=[c for c in cases if not args.respect_targets or condition=='plain' or c.get('creator')==condition.split(':')[0]]
        batches=[selected[i:i+4] for i in range(0,len(selected),4)]
        for i,batch in enumerate(batches):
            destination = work / "evaluation-private" / args.revision / condition.replace(":","-") / ("batch"+str(i+1))
            jobs.append((condition, i, batch, destination))
    def run(job):
        condition, i, batch, destination = job
        if (destination / "run.json").exists() and json.loads((destination / "run.json").read_text())["exit_code"] == 0 and (destination / "output.json").exists():
            return condition, json.loads((destination / "output.json").read_text())
        output = invoke(make_prompt(batch,methods[condition]), destination)
        expected = [c["id"] for c in batch]
        actual = [x["id"] for x in output["responses"]]
        if actual != expected: raise RuntimeError(f"Case mismatch: {expected} != {actual}")
        print("completed", condition, "batch",i+1,flush=True)
        return condition, output
    results = {c:[] for c in args.conditions}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        for condition, output in executor.map(run,jobs): results[condition].extend(output["responses"])
    def feedback(condition):
        parent = next(x["answer"] for x in results[condition] if x["id"] == spec["feedback"]["parent"])
        destination = work / "evaluation-private" / args.revision / condition.replace(":","-") / "feedback"
        current = next(c for c in cases if c["id"] == spec["feedback"]["parent"])
        conversation = "下面是本次委托前一轮的真实对话。请接着用户反馈完成同一委托。\n用户："+current["prompt"]+"\n助手："+parent+"\n用户反馈："+spec["feedback"]["prompt"]
        case = {"id":"C09","prompt":conversation}
        output = invoke(make_prompt([case],methods[condition]), destination)
        print("completed",condition,"feedback",flush=True)
        return condition,output
    if spec.get('feedback'):
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            for condition, output in executor.map(feedback,args.conditions): results[condition].extend(output["responses"])
    folder = work / "evaluation-private" / args.revision
    all_file=folder / "all-outputs.json"
    existing=json.loads(all_file.read_text()) if all_file.exists() else {}
    existing.update(results)
    all_file.write_text(json.dumps(existing,ensure_ascii=False,indent=2))
    hash_file=folder / "method-hashes.json"
    hashes=json.loads(hash_file.read_text()) if hash_file.exists() else {}
    hashes.update({k:digest(v) for k,v in methods.items()})
    hash_file.write_text(json.dumps(hashes,indent=2))
    print("saved",folder / "all-outputs.json",flush=True)

if __name__ == "__main__": main()
