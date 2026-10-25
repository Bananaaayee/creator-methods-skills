#!/usr/bin/env python3
"""Blind semantic comparison of the three methods on common requests."""
import argparse
import json
from pathlib import Path
from run_eval import invoke
from score_blind import mask

SCHEMA={"type":"object","properties":{"cases":{"type":"array","items":{"type":"object","properties":{"id":{"type":"string"},"decision_differences":{"type":"array","items":{"type":"string"}},"shared_appropriate_principles":{"type":"array","items":{"type":"string"}},"similarity_risk":{"type":"string","enum":["low","moderate","high"]},"basis":{"type":"string"}},"required":["id","decision_differences","shared_appropriate_principles","similarity_risk","basis"],"additionalProperties":False}},"overall":{"type":"string"}},"required":["cases","overall"],"additionalProperties":False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);a=p.parse_args();w=a.work.resolve()
    outputs=json.loads((w/'evaluation-private/r2/all-outputs.json').read_text())
    spec=json.loads((w/'repo/tests/cases.json').read_text())
    mapping={'P':'lawrence:new','Q':'media-storm:new','R':'he-tongxue:new'}
    tasks=[]
    for c in spec['cases']:
        if c['id'] not in ['C01','C03','C04','H01','L01','M01']:continue
        tasks.append({'id':c['id'],'request':c['prompt'],'answers':{k:mask(next(x['answer'] for x in outputs[v] if x['id']==c['id'])) for k,v in mapping.items()}})
    prompt='''独立比较以下三种未知创作方法对相同任务的真实答案。不要猜身份或版本，不因文风不同就认定方法不同。比较选择的问题、行动、证据责任和结构决策；一般事实诚实、按用户约束或同样的合理答案不算风格混淆。指出哪些相近由任务约束造成，哪些方法层面高度相似、缺少实质区分。答案中的“该创作者方法”等是身份替换，不是未填占位。方法附件不向你显示，提及“所附研究”不因此虚构。每项评价必须有具体决策差异或相似依据；不为迎合项目强造三套差异。不得使用工具或联网。\n'''+json.dumps(tasks,ensure_ascii=False)
    d=w/'evaluation-private/cross-style-r2';d.mkdir(exist_ok=True)
    (d/'mapping.json').write_text(json.dumps(mapping))
    result=invoke(prompt,d,SCHEMA)
    print(result['overall'])

if __name__=='__main__':main()
