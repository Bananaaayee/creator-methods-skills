#!/usr/bin/env python3
"""Version-masked scoring; run only after collecting actual outputs."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import random
import re
from run_eval import invoke

DIMENSIONS = ["task_fit","method_fit","actionability","factual_honesty","template_restraint","user_voice_scope","constraint_completion"]
SCORE = {"type":"integer","minimum":0,"maximum":4}
RATING = {"type":"object","properties":{"label":{"type":"string"},"scores":{"type":"object","properties":{d:SCORE for d in DIMENSIONS},"required":DIMENSIONS,"additionalProperties":False},"reasons":{"type":"array","items":{"type":"string"}},"critical_failure":{"type":"boolean"}},"required":["label","scores","reasons","critical_failure"],"additionalProperties":False}
SCHEMA = {"type":"object","properties":{"cases":{"type":"array","items":{"type":"object","properties":{"id":{"type":"string"},"ratings":{"type":"array","items":RATING},"comparison":{"type":"string"}},"required":["id","ratings","comparison"],"additionalProperties":False}}},"required":["cases"],"additionalProperties":False}

def mask(answer):
    answer = re.sub(r"V?1\.(?:21|22|2|3)\.(?:0|1)\b", "该版本",answer)
    for name in ["何同学","小鹿Lawrence","小鹿 Lawrence","影视飓风","Lawrence","CreatorSkill"]:
        answer=answer.replace(name,"该创作者方法")
    return answer

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--work",required=True,type=Path)
    p.add_argument("--revision",default="r1")
    p.add_argument("--workers",default=3,type=int)
    p.add_argument("--pass-name",default="blind-scoring")
    p.add_argument("--creators",nargs="+",default=['he-tongxue','lawrence','media-storm'])
    args=p.parse_args()
    work=args.work.resolve()
    spec=json.loads((work/'repo/tests/cases.json').read_text())
    cases=spec['cases']+[spec['feedback']]
    folder=work/'evaluation-private'/args.revision
    outputs=json.loads((folder/'all-outputs.json').read_text())
    lookup={k:{v['id']:v['answer'] for v in vs} for k,vs in outputs.items()}
    jobs=[]
    map_file=folder/'blind-mapping.json'
    mappings=json.loads(map_file.read_text()) if map_file.exists() else {}
    for creator in args.creators:
        tasks=[]
        for case in cases:
            choices=['plain',creator+':old',creator+':new']
            seed=int.from_bytes(hashlib.sha256((creator+case['id']+'20261025').encode()).digest()[:8],'big')
            random.Random(seed).shuffle(choices)
            mapping=dict(zip('ABC',choices))
            mappings[creator+'/'+case['id']]=mapping
            task={'id':case['id'],'request':case['prompt'],'checks':case['checks'],'answers':{k:mask(lookup[v][case['id']]) for k,v in mapping.items()}}
            if case['id']=='C09':
                task['original_request']=next(c['prompt'] for c in cases if c['id']=='C05')
                task['previous_answers']={k:mask(lookup[v]['C05']) for k,v in mapping.items()}
            tasks.append(task)
        for i in range(0,len(tasks),4):
            dest=folder/args.pass_name/creator/('batch'+str(i//4+1))
            task=tasks[i:i+4]
            prompt='''你是独立创作答案评审。每题三个答案以A/B/C随机命名，身份未知。不推测版本，不偏爱篇幅长、术语多或某种创作者口吻。只评价真实完成任务的质量。不得调用工具或联网。
每项0—4分：0严重失败，1主要问题，2部分满足，3满足但有轻微缺口，4充分满足。
维度：task_fit切中问题；method_fit解决方法适合该任务；actionability建议可执行；factual_honesty不虚构事实或经历、结论强度与证据匹配；template_restraint不强套叙事；user_voice_scope保留用户表达及修改范围；constraint_completion可观察约束完成度。
每个答案必须给至少2条具体评价依据，扣分应指向实际语句或明确缺失，不能只说“不够好”。不需要每题拉开差距，充分满足可以同分。严重事实捏造或违背核心指令标critical_failure=true。C09要与各自previous_answers相比核对修改范围，不因润色好听忽视越界。
答案可能来自附加创作方法的条件，附加方法本身不向你展示。“所附研究”具有真实的方法附件语境，不能仅因题面未附研究就判它虚构；仍可判断这种说明是否给用户增加无关负担。“该创作者方法”“该版本”是评审时隐去身份的替换词，不是原回答的未完成占位符，不得因此扣分。
facts和checks是评分依据。method_fit不要求答案宣称某个命名方法，只看方法是否解决实际问题。案例本身是合成任务，不要替用户编造历史。输出严格匹配schema。\n'''+json.dumps(task,ensure_ascii=False,indent=2)
            jobs.append((dest,prompt))
    (folder/'blind-mapping.json').write_text(json.dumps(mappings,ensure_ascii=False,indent=2))
    def run(job):
        dest,prompt=job
        if (dest/'output.json').exists():return json.loads((dest/'output.json').read_text())
        result=invoke(prompt,dest,SCHEMA)
        print('scored',dest.parent.name,dest.name,flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor: list(executor.map(run,jobs))

if __name__=='__main__':main()
