#!/usr/bin/env python3
"""Copy one modular skill into a destination directory without overwriting."""
import argparse
from pathlib import Path
import shutil
import re

def main():
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser()
    p.add_argument('creator',choices=['he-tongxue','lawrence','media-storm'])
    p.add_argument('--destination',type=Path,required=True,help='Parent of the installed skill folder, e.g. ~/.codex/skills')
    a=p.parse_args()
    source=root/'creators'/a.creator/'skill'
    frontmatter=(source/'SKILL.md').read_text().split('---',2)[1]
    name=re.search(r'^name:\s*[\"\']?([a-z0-9-]+)',frontmatter,re.M)
    if not name:raise SystemExit('Missing valid skill name')
    target=a.destination.expanduser().resolve()/name.group(1)
    if target.exists():raise SystemExit(f'Refusing to overwrite existing folder: {target}')
    if not (source/'SKILL.md').is_file():raise SystemExit('Missing SKILL.md')
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source,target)
    print(target)

if __name__=='__main__':main()
