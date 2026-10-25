#!/usr/bin/env python3
"""Export actual outputs and scoring evidence, excluding private method prompts."""
import argparse
import json
from pathlib import Path
import re
import statistics

def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);a=p.parse_args();w=a.work.resolve();private=w/'evaluation-private';out=w/'repo/tests/results';out.mkdir(exist_ok=True)
    answer_rounds={'r1':'combined-r1','r2-new':'r2','audit-r1':'audit-r1','audit-r2':'audit-r2','repair-r3':'repair-r3','r4-he':'r4-he'}
    for public,source in answer_rounds.items():
        data=json.loads((private/source/'all-outputs.json').read_text())
        (out/('outputs-'+public+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    scores={};summary={}
    for public,roundname,folder in [('r1-initial-invalid','combined-r1','blind-scoring'),('r1-corrected','combined-r1','blind-scoring-corrected'),('r2-corrected','combined-r2','blind-scoring-corrected'),('final-corrected','combined-final','blind-scoring-corrected')]:
        root=private/roundname
        mapping=json.loads((root/'blind-mapping.json').read_text())
        rows=[]
        for creator in ['he-tongxue','lawrence','media-storm']:
            cs=[]
            for file in sorted((root/folder/creator).glob('*/output.json')):
                for case in json.loads(file.read_text())['cases']:
                    labels=[v['label'] for v in case['ratings']]
                    if set(labels)!=set('ABC') or len(labels)!=3:raise ValueError('Invalid labels '+str(file))
                    decoded={}
                    for rating in case['ratings']:
                        condition=mapping[creator+'/'+case['id']][rating['label']]
                        if len(rating['scores'])!=7 or any(not isinstance(x,int) or not 0<=x<=4 for x in rating['scores'].values()):raise ValueError('Invalid score')
                        decoded[condition]={**rating,'total':sum(rating['scores'].values())}
                    row={'creator':creator,'id':case['id'],'decoded':decoded,'comparison':case['comparison']}
                    rows.append(row);cs.append(row)
            if len(cs)!=12 or len({c['id'] for c in cs})!=12:raise ValueError(f'Incomplete {public} {creator}: {len(cs)}')
            if public not in summary:summary[public]={}
            means={cond:round(statistics.mean(x['decoded'][cond]['total'] for x in cs),3) for cond in ['plain',creator+':old',creator+':new']}
            diffs=[x['decoded'][creator+':new']['total']-x['decoded'][creator+':old']['total'] for x in cs]
            summary[public][creator]={'n':12,'mean_out_of_28':means,'new_vs_old':{'wins':sum(v>0 for v in diffs),'ties':sum(v==0 for v in diffs),'losses':sum(v<0 for v in diffs)},'critical_failures':[{'id':x['id'],'condition':k,'reasons':v['reasons']} for x in cs for k,v in x['decoded'].items() if v['critical_failure']]}
        scores[public]=rows
        (out/('scoring-'+public+'.json')).write_text(json.dumps({'valid_for_comparison':public!='r1-initial-invalid','invalid_reason':'Initial judge penalized identity masking and real method-attachment context; preserved for audit, replaced by corrected scoring.' if public=='r1-initial-invalid' else None,'rows':rows},ensure_ascii=False,indent=2)+'\n')
    (out/'score-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (out/'blind-mapping.json').write_text((private/'combined-final/blind-mapping.json').read_text())
    metadata=[]
    for path in sorted(private.rglob('run.json')):
        item=json.loads(path.read_text())
        metadata.append({'run':str(path.parent.relative_to(private)),**{k:item[k] for k in ['model','reasoning_effort','started_at','duration_seconds','exit_code','prompt_sha256','usage']},'tool_items_count':len(item['non_message_items'])})
    (out/'run-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    checks=[]
    for roundname in ['combined-r1','combined-r2','combined-final','repair-r3']:
        outputs=json.loads((private/roundname/'all-outputs.json').read_text())
        for condition,answers in outputs.items():
            lookup={x['id']:x['answer'] for x in answers}
            row={'round':roundname,'condition':condition}
            if 'C06' in lookup:
                body=lookup['C06'].split('\n\n')[0].strip()
                sentences=re.findall(r'[^。！？]*[。！？]',body)
                row['C06_first_and_third_exact']=len(sentences)==3 and sentences[0]=='我买这台小相机，是因为大相机太重。' and sentences[2]=='现在我更愿意每天带着它出门。'
            if 'C08' in lookup:row['C08_nonspace_characters']=len(re.sub(r'\s','',lookup['C08']))
            if 'C09' in lookup:
                parent=lookup['C05'];sentences=[s for s in re.split(r'(?<=[。！？])',parent) if s]
                row['C09_prior_prefix_preserved']=lookup['C09'].startswith(''.join(sentences[:-2]))
                row['C09_nonspace_characters']=len(re.sub(r'\s','',lookup['C09']))
                row['C09_han_characters']=len(re.findall('[\u4e00-\u9fff]',lookup['C09']))
            checks.append(row)
    (out/'objective-checks.json').write_text(json.dumps({'note':'Length units are reported both with punctuation (non-space characters) and Han characters; these checks alone do not certify all semantic constraints. C06 check covers locked sentences, not truthfulness of replacement.','rows':checks},ensure_ascii=False,indent=2)+'\n')
    (out/'structural-validation.json').write_text((w/'research/structural-validation-final.json').read_text())
    modular=json.loads((w/'research/modular-forward/observations.json').read_text())
    text=json.dumps(modular,ensure_ascii=False,indent=2).replace(str(w),'[local-work]')
    (out/'modular-forward.json').write_text(text+'\n')
    cross=json.loads((private/'cross-style-r2/output.json').read_text())
    cross['mapping']=json.loads((private/'cross-style-r2/mapping.json').read_text())
    (out/'cross-style.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary['final-corrected'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
