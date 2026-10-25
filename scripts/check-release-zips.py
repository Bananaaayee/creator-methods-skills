#!/usr/bin/env python3
import argparse
import collections
import hashlib
import json
import pathlib
import stat
import sys
import tempfile
import zipfile
from datetime import datetime, timezone

parser = argparse.ArgumentParser(description='Inspect three release ZIPs against canonical skills/ without changing the repository.')
parser.add_argument('--repo', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1])
parser.add_argument('--archives', type=pathlib.Path, help='Directory containing the three single-skill ZIPs; default: sibling release-assets/')
args = parser.parse_args()
repo = args.repo.resolve()
archive_dir = args.archives.resolve() if args.archives else repo.parent / 'release-assets'
record_dir = pathlib.Path(tempfile.mkdtemp(prefix='creator-atlas-zip-checks-'))
extract_base = record_dir / 'extracted'
names = ['he-tongxue-creator', 'lawrence-creator', 'media-storm-creator']
results = []

for name in names:
    archive = archive_dir / (name + '.zip')
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        unsafe = []
        duplicate_entries = sorted(k for k, count in collections.Counter(i.filename for i in infos).items() if count > 1)
        actual = {}
        for info in infos:
            p = pathlib.PurePosixPath(info.filename)
            mode = (info.external_attr >> 16) & 0xffff
            if p.is_absolute() or '..' in p.parts or stat.S_ISLNK(mode):
                unsafe.append(info.filename)
            if not info.is_dir():
                actual[info.filename] = hashlib.sha256(z.read(info.filename)).hexdigest()
        expected = {}
        for f in sorted((repo / 'skills' / name).rglob('*')):
            if f.is_file():
                expected[name + '/' + f.relative_to(repo / 'skills' / name).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
        errors = z.testzip()
        passed = not unsafe and not duplicate_entries and errors is None and actual == expected
        if not unsafe:
            target = extract_base / name
            target.mkdir(parents=True, exist_ok=True)
            z.extractall(target)
        results.append({
            'name': name, 'archive': str(archive), 'archiveSha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'files': len(actual), 'expectedFiles': len(expected), 'topLevel': sorted({pathlib.PurePosixPath(k).parts[0] for k in actual}),
            'skillEntry': name + '/SKILL.md', 'hasSkillEntry': name + '/SKILL.md' in actual,
            'unsafeEntries': unsafe, 'duplicateEntries': duplicate_entries, 'zipCrcError': errors, 'exactFileSetAndHashes': actual == expected,
            'missing': sorted(set(expected) - set(actual)), 'unexpected': sorted(set(actual) - set(expected)),
            'extractedDirectory': str(extract_base / name / name), 'passed': passed,
            'expected': expected, 'actual': actual
        })

report = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'scope': '最终35文件发布单ZIP，结构、CRC、安全路径、完整文件集合及SHA256；不调用模型', 'results': results}
(record_dir / 'final-release-zips-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
for r in results:
    print(json.dumps({k: r[k] for k in ['name', 'files', 'topLevel', 'hasSkillEntry', 'exactFileSetAndHashes', 'passed']}, ensure_ascii=False))
print('Results and extracted files:', record_dir)
sys.exit(0 if all(r['passed'] for r in results) else 1)
