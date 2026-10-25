#!/usr/bin/env python3
"""Scan release source for common secret/file patterns; this is not legal clearance."""
import argparse
import hashlib
import json
from pathlib import Path
import re

PATTERNS = {
    'github_token': re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})'),
    'api_key': re.compile(r'\bs[k]-[A-Za-z0-9_-]{24,}'),
    'aws_key': re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'user_absolute_path': re.compile('/' + 'Users' + r'/[\w.-]+/'),
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
}
BLOCKED_SUFFIXES = {'.srt', '.vtt', '.mp4', '.mov', '.mkv', '.mp3', '.wav', '.pem', '.key'}
BLOCKED_NAMES = {'.env', 'auth.json', 'hosts.yml', '.DS_Store'}

def scan(root):
    findings, hashes, utf8 = [], {}, []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or any(part in {'.git', '__pycache__', 'node_modules', '.venv'} for part in p.relative_to(root).parts):
            continue
        rel = p.relative_to(root).as_posix()
        data = p.read_bytes()
        hashes[rel] = hashlib.sha256(data).hexdigest()
        if p.suffix.lower() in BLOCKED_SUFFIXES or p.name in BLOCKED_NAMES or p.name.startswith('.env.'):
            findings.append({'path': rel, 'kind': 'blocked_file'})
        try:
            content = data.decode('utf-8')
        except UnicodeDecodeError:
            utf8.append(rel)
            continue
        for kind, pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                findings.append({'path': rel, 'kind': kind, 'line': content[:match.start()].count('\n') + 1})
    return {'schema_version': 1, 'date': '2026-10-25', 'scope': 'current release source files, excluding tool caches and .git', 'file_count': len(hashes), 'findings': findings, 'non_utf8_files': utf8, 'sha256': hashes, 'limits': 'Pattern matching only. No legal clearance, no unreachable Git objects, no proof against all secrets or personal information.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, help='Write outside scanned source to avoid self-hash recursion')
    args = parser.parse_args()
    result = scan(args.repo)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'sha256'}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['findings'] or result['non_utf8_files']))
