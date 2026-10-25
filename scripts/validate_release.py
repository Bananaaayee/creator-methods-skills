#!/usr/bin/env python3
"""Structural/distribution checks, distinct from behavioral quality evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path)
    p.add_argument('--official-validator',type=Path)
    a=p.parse_args()
    failures=[]
    checks={}
    manifest=json.loads((ROOT/'release-manifest.json').read_text())
    forbidden=[r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'sk-[A-Za-z0-9_-]{20,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'/Users/[A-Za-z0-9._-]+/',r'[A-Za-z0-9._%+-]+@(?:gmail|outlook|qq|hotmail)\.com']
    for slug,data in manifest.items():
        root=ROOT/'creators'/slug
        skill=root/'skill'
        info={'module_count':len(list(skill.glob('[0-9][0-9]_*.md'))),'markdown_files':len(list(root.rglob('*.md'))),'link_errors':[],'privacy_scan':[],'placeholder_errors':[]}
        for file in root.rglob('*.md'):
            text=file.read_text()
            for pattern in forbidden:
                if re.search(pattern,text):info['privacy_scan'].append(str(file.relative_to(ROOT))+':'+pattern)
            for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',text):
                target=match.group(1).strip('<>').split('#')[0]
                if not target or '://' in target or target.startswith('mailto:'):continue
                # A portable edition embeds every referenced runtime file as a heading.
                if 'dist' in file.relative_to(root).parts:
                    embedded='## 嵌入文件：'+target
                    if embedded not in text and not any(x in text for x in ['## 嵌入文件：references/'+target]):
                        info['link_errors'].append(str(file.relative_to(ROOT))+' -> '+target)
                elif not (file.parent/target).resolve().exists():
                    info['link_errors'].append(str(file.relative_to(ROOT))+' -> '+target)
        for file,expected in data['inputs'].items():
            actual=hashlib.sha256((ROOT/file).read_bytes()).hexdigest()
            if actual!=expected:failures.append('manifest mismatch '+file)
        if hashlib.sha256((ROOT/data['portable']).read_bytes()).hexdigest()!=data['portable_sha256']:failures.append('portable mismatch '+slug)
        with tempfile.TemporaryDirectory(prefix='creator-install-check-') as tmp:
            result=subprocess.run([sys.executable,str(ROOT/'scripts/install.py'),slug,'--destination',tmp],text=True,capture_output=True)
            info['install_exit_code']=result.returncode
            if result.returncode:failures.append(result.stderr)
            else:
                installed=Path(result.stdout.strip())
                info['installed_file_count']=len([f for f in installed.rglob('*') if f.is_file()])
                info['installed_name']=installed.name
                if a.official_validator:
                    check=subprocess.run([sys.executable,str(a.official_validator),str(installed)],text=True,capture_output=True)
                    info['official_validation']={'exit_code':check.returncode,'message':check.stdout+check.stderr}
                    if check.returncode:failures.append('official validator '+slug)
                second=subprocess.run([sys.executable,str(ROOT/'scripts/install.py'),slug,'--destination',tmp],text=True,capture_output=True)
                info['overwrite_refused']=second.returncode!=0
                if not info['overwrite_refused']:failures.append('overwrite protection '+slug)
        if info['module_count']!=6:failures.append('module count '+slug)
        if info['link_errors'] or info['privacy_scan']:failures.append('link/privacy '+slug)
        checks[slug]=info
    package_privacy=[]
    unexpected=[]
    for file in ROOT.rglob('*'):
        if not file.is_file() or any(x in file.relative_to(ROOT).parts for x in ['.git','__pycache__']):continue
        if file.suffix in ['.srt','.mp4','.mov','.wav','.mp3','.pdf','.pem','.key'] or file.name in ['auth.json','hosts.yml','.env']:unexpected.append(str(file.relative_to(ROOT)))
        if file.suffix not in ['.md','.json','.py'] and file.name!='.gitignore':continue
        text=file.read_text()
        for pattern in forbidden:
            if re.search(pattern,text):package_privacy.append(str(file.relative_to(ROOT))+':'+pattern)
    if package_privacy or unexpected:failures.append('whole repository privacy/unexpected asset scan')
    result={'checks':checks,'package_privacy_scan':package_privacy,'unexpected_assets':unexpected,'failures':failures,'scope':'format, file references, manifest integrity, temporary installation and limited pattern scan; not proof of rights or behavioral quality'}
    if a.output:a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(bool(failures))

if __name__=='__main__':main()
