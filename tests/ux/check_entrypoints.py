#!/usr/bin/env python3
"""Read-only UX regression checks; no install, rebuild, network, or config writes.

Run from a full Git checkout with the V3 baseline commit available:
    python3 tests/ux/check_entrypoints.py
Output is JSON on stdout. This does not rerun online/download/installer tests.
"""
from __future__ import annotations
import hashlib
import json
import re
import runpy
import subprocess
from pathlib import Path

BASELINE = "f571b8288e8b26bdfeb1802f850784e0a5130f75"
ROOT = Path(__file__).resolve().parents[2]
SLUGS = ("he-tongxue-creator", "lawrence-creator", "media-storm-creator")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.PIPE)


def immutable(path: str) -> bool:
    return (path.startswith(("skills/", "portable/", "creators/"))
            or (path.startswith("copy/") and path != "copy/README.md")
            or path == "distribution-manifest.json")


def main() -> int:
    report = {"baseline_commit": BASELINE, "network_requests": 0,
              "model_calls": 0, "writes": 0}
    try:
        baseline_paths = git("ls-tree", "-r", "--name-only", "-z", BASELINE).decode().rstrip("\0").split("\0")
        protected = [p for p in baseline_paths if immutable(p)]
        mismatches = []
        for name in protected:
            path = ROOT / name
            if not path.is_file() or digest(path.read_bytes()) != digest(git("show", f"{BASELINE}:{name}")):
                mismatches.append(name)
        current = {p.relative_to(ROOT).as_posix() for directory in ("skills", "portable", "copy", "creators")
                   for p in (ROOT / directory).rglob("*") if p.is_file()
                   and "__pycache__" not in p.parts and immutable(p.relative_to(ROOT).as_posix())}
        extras = sorted(current - set(protected))
        report["preservation"] = {"files_checked": len(protected), "mismatches": mismatches,
                                  "new_files_in_protected_directories": extras,
                                  "passed": not mismatches and not extras}
    except (subprocess.CalledProcessError, OSError) as error:
        report["preservation"] = {"passed": False, "error": type(error).__name__,
                                  "note": "The full Git baseline must be present; no missing evidence is treated as pass."}
    checker = runpy.run_path(str(ROOT / "scripts/check_distribution.py"), run_name="ux_link_checker")
    markdown = sorted(p.resolve() for p in ROOT.rglob("*.md") if p.is_file()
                      and not any(x in {".git", "__pycache__", "node_modules"} for x in p.parts))
    decoded = {p: p.read_text(encoding="utf-8", errors="strict") for p in markdown}
    report["local_links"] = checker["local_links"](ROOT, markdown, decoded)
    prompt_path = ROOT / "docs/交给AI安装.md"
    prompt = prompt_path.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    def prompt_block(text: str) -> str:
        match = re.search(r"```text\n(请帮我获取并使用 Creator Methods Atlas[\s\S]+?)\n```", text)
        return match.group(1) if match else ""
    source_prompt, readme_prompt = prompt_block(prompt), prompt_block(readme)
    required = ["README.md", "docs/交给AI安装.md", "docs/安装Skill.md", "DISCLAIMER.md"]
    source_files = []
    for slug in SLUGS:
        path = ROOT / "skills" / slug
        files = sorted(p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file())
        entry = (path / "SKILL.md").read_text(encoding="utf-8")
        source_files.append({"name": slug, "files": len(files), "entry_exists": (path / "SKILL.md").is_file(),
                             "frontmatter_name_matches": f"name: {slug}\n" in entry,
                             "listed_in_install_guide": slug in prompt,
                             "references_directory_exists": (path / "references").is_dir()})
    path_ok = all((ROOT / name).is_file() for name in required)
    skills_ok = all(all(row[key] for key in ("entry_exists", "frontmatter_name_matches",
                                             "listed_in_install_guide", "references_directory_exists"))
                    for row in source_files)
    report["agent_prompt_paths"] = {"required_reading_exists": path_ok, "skills": source_files,
                                      "readme_and_guide_prompt_identical": bool(source_prompt) and source_prompt == readme_prompt,
                                      "passed": path_ok and skills_ok and bool(source_prompt) and source_prompt == readme_prompt}
    retained_anchors, legacy_targets = [], []
    edited_docs = ("README.md", "docs/安装Skill.md", "downloads/README.md", "downloads/Hetongxue.md",
                   "downloads/Lawrence.md", "downloads/MediaStorm.md", "copy/README.md", "CHANGELOG.md")
    # Preserve every historical file path plus old heading anchors on navigation pages.
    old_paths = git("ls-tree", "-r", "--name-only", "-z", BASELINE).decode().rstrip("\0").split("\0")
    missing_old_paths = [name for name in old_paths if not (ROOT / name).is_file()]
    for name in edited_docs:
        old_text = git("show", f"{BASELINE}:{name}").decode("utf-8")
        new_text = (ROOT / name).read_text(encoding="utf-8")
        missing = sorted(checker["anchors"](old_text) - checker["anchors"](new_text))
        retained_anchors.append({"path": name, "missing_old_anchors": missing})
        for match in checker["INLINE_LINK"].finditer(old_text):
            target = match.group(2).strip("<>")
            if target.startswith("https://github.com/Bananaaayee/creator-methods-skills/releases/"):
                legacy_targets.append(target)
    current_docs = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in edited_docs)
    missing_release_links = sorted({target for target in legacy_targets if target not in current_docs})
    report["legacy_links"] = {"baseline_paths_checked": len(old_paths), "missing_old_paths": missing_old_paths,
                               "navigation_anchors": retained_anchors,
                               "release_links_checked": len(set(legacy_targets)),
                               "missing_old_release_links": missing_release_links,
                               "passed": not missing_old_paths and not missing_release_links
                                         and not any(row["missing_old_anchors"] for row in retained_anchors)}
    report["agent_prompt_paths"]["repository_url_correct"] = "https://github.com/Bananaaayee/creator-methods-skills" in source_prompt
    report["agent_prompt_paths"]["passed"] &= report["agent_prompt_paths"]["repository_url_correct"]
    report["passed"] = (report["preservation"]["passed"] and report["local_links"]["result"] == "pass"
                        and report["agent_prompt_paths"]["passed"] and report["legacy_links"]["passed"])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
