#!/usr/bin/env python3
"""Build self-contained portable editions deterministically from runtime files."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CREATORS={'he-tongxue':('何同学','1.3.0'),'lawrence':('小鹿Lawrence','1.3.0'),'media-storm':('影视飓风','1.22.0')}

def main():
    manifest={}
    for slug,(name,version) in CREATORS.items():
        root=ROOT/'creators'/slug
        skill=root/'skill'
        entry=skill/'SKILL.md'
        modules=sorted(skill.glob('[0-9][0-9]_*.md'))
        refs=sorted((skill/'references').rglob('*.md')) if (skill/'references').exists() else []
        files=[entry]+modules+refs
        missing=[str(p) for p in files if not p.is_file()]
        if missing or len(modules)!=6:raise ValueError(f'{slug}: missing core files: {missing}, modules={len(modules)}')
        body=[f'# {name} Creator Skill V{version}｜单文件便携版\n\n由模块化运行文件生成。上传本文件后，按入口路由使用；后附参考区可通过本文件内标题和作品ID检索。文件名链接在单文件环境中表示同名嵌入章节，无需另行下载。原始字幕不随包分发。\n']
        anchors={p.resolve():'embedded-'+hashlib.sha256(p.relative_to(skill).as_posix().encode()).hexdigest()[:12] for p in files}
        for file in files:
            relative=file.relative_to(skill).as_posix()
            text=file.read_text()
            if file==entry and text.startswith('---\n'):
                text=text.split('---\n',2)[-1]
            def link(match):
                label,target=match.group(1),match.group(2)
                path=target.strip('<>').split('#')[0]
                if not path or '://' in path:return match.group(0)
                absolute=(file.parent/path).resolve()
                if absolute in anchors:return '['+label+'](#'+anchors[absolute]+')'
                return match.group(0)
            text=re.sub(r'\[([^\]]*)\]\(([^)]+)\)',link,text)
            body.append('\n\n---\n\n<a id="'+anchors[file.resolve()]+'"></a>\n\n## 嵌入文件：'+relative+'\n\n'+text.rstrip()+'\n')
        dist=root/'dist'
        dist.mkdir(exist_ok=True)
        output=dist/f'{slug}-creator-skill-v{version}-portable.md'
        output.write_text(''.join(body))
        manifest[slug]={'version':version,'portable':str(output.relative_to(ROOT)),'portable_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (ROOT/'release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:{'version':v['version'],'runtime_files':len(v['inputs']),'portable_sha256':v['portable_sha256']} for k,v in manifest.items()},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
