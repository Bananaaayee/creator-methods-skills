#!/usr/bin/env python3
"""Check local distribution links, UTF-8 text and complete-copy safeguards.

Uses Python's standard library and performs no network requests. The default
mode only reads the distribution and writes tests/distribution-result.json.
--rebuild additionally runs the deterministic builder with --check first;
use it before adding a separately prepared final all-in-one release archive.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import runpy
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit


TEXT_SUFFIXES = {".md", ".txt", ".py", ".json", ".toml", ".yaml", ".yml", ".sh"}
IGNORED_PARTS = {".git", "__pycache__", "node_modules", ".pytest_cache"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_LINK = re.compile(r"!?\[([^\]\n]*)\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[\"'][^\"']*[\"'])?\s*\)")
REFERENCE = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)")
HTML_LINK = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)
EXPLICIT_ANCHOR = re.compile(r"\b(?:id|name)=[\"']([^\"']+)[\"']", re.IGNORECASE)
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0003134f]")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def visible_lines(text: str):
    """Yield non-code lines with their original one-based line numbers."""
    opening = None
    previous_blank, indented = True, False
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if opening:
            if match and match.group(1)[0] == opening[0] and len(match.group(1)) >= opening[1] and not match.group(2).strip():
                opening = None
                previous_blank = True
            continue
        if match:
            opening = (match.group(1)[0], len(match.group(1)))
            continue
        if (line.startswith("    ") or line.startswith("\t")) and (previous_blank or indented):
            indented = True
            continue
        if indented and not line.strip():
            continue
        indented = False
        previous_blank = not line.strip()
        yield number, line


def without_inline_code(line: str) -> str:
    # A backtick span uses matching delimiter lengths; examples inside it do
    # not create navigation targets in rendered Markdown.
    return re.sub(r"(`+)(?!`)(.*?)(?<!`)\1(?!`)", "", line)


def anchors(text: str) -> set[str]:
    found, heading_counts = set(), {}
    for _, line in visible_lines(text):
        found.update(html.unescape(m.group(1)) for m in EXPLICIT_ANCHOR.finditer(line))
        heading = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        title = html.unescape(heading.group(1))
        title = re.sub(r"<[^>]+>", "", title)
        title = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", title)
        title = title.replace("`", "").replace("*", "").lower()
        # GitHub-style heading slugs retain letters (including Chinese),
        # numbers, underscores and hyphens, while dropping punctuation.
        title = "".join(c for c in title if c in "_-" or c.isspace()
                        or unicodedata.category(c)[0] in {"L", "N"})
        slug = re.sub(r"\s", "-", title.strip())
        duplicate = heading_counts.get(slug, 0)
        heading_counts[slug] = duplicate + 1
        found.add(slug if not duplicate else f"{slug}-{duplicate}")
    return found


def local_links(root: Path, markdown: list[Path], decoded: dict[Path, str]) -> dict:
    failures, checked, fragments, skipped_external = [], 0, 0, 0
    anchor_cache = {}
    for source in markdown:
        for line_number, raw_line in visible_lines(decoded[source]):
            line = without_inline_code(raw_line)
            targets = [m.group(2).strip("<>") for m in INLINE_LINK.finditer(line)]
            reference = REFERENCE.match(line)
            if reference:
                targets.append(reference.group(1).strip("<>"))
            targets.extend(m.group(1) for m in HTML_LINK.finditer(line))
            for original in targets:
                target = html.unescape(original)
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or target.startswith("//"):
                    skipped_external += 1
                    continue
                checked += 1
                target_path = unquote(parsed.path)
                if not target_path:
                    destination = source
                elif target_path.startswith("/"):
                    destination = (root / target_path.lstrip("/")).resolve()
                else:
                    destination = (source.parent / target_path).resolve()
                issue = {"source": source.relative_to(root).as_posix(), "line": line_number, "target": original}
                if not destination.is_relative_to(root):
                    failures.append({**issue, "error": "relative target escapes repository"})
                    continue
                if not destination.exists():
                    failures.append({**issue, "error": "missing local target"})
                    continue
                if parsed.fragment:
                    fragments += 1
                    if destination.is_dir():
                        destination = destination / "README.md"
                    if destination.suffix.lower() != ".md":
                        continue
                    if destination not in anchor_cache:
                        anchor_cache[destination] = anchors(decoded.get(destination) or destination.read_text(encoding="utf-8"))
                    if unquote(parsed.fragment) not in anchor_cache[destination]:
                        failures.append({**issue, "error": "missing local Markdown anchor"})
    return {"result": "pass" if not failures else "fail", "markdown_files_checked": len(markdown),
            "relative_links_checked": checked, "local_fragments_checked": fragments,
            "external_links_skipped": skipped_external, "code_examples_skipped": True,
            "failures": failures}


def encoding_check(root: Path, files: list[Path]) -> tuple[dict, dict[Path, str]]:
    decoded, failures, chinese_docs = {}, [], []
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_bytes().decode("utf-8", errors="strict")
            decoded[path] = text
        except UnicodeDecodeError:
            failures.append({"path": relative, "error": "not valid UTF-8"})
            continue
        if "\x00" in text or "\ufffd" in text:
            failures.append({"path": relative, "error": "NUL or Unicode replacement character present"})
        if path.suffix.lower() in {".md", ".txt"} and path.relative_to(root).parts[0] not in {"tests", "scripts"}:
            count = len(HAN.findall(text))
            chinese_docs.append({"path": relative, "han_characters": count})
            if not count:
                failures.append({"path": relative, "error": "user-facing document contains no Chinese characters"})
    return {"result": "pass" if not failures else "fail", "text_files_checked": len(files),
            "chinese_documents_checked": len(chinese_docs), "strict_utf8": True,
            "nul_and_replacement_character_check": True, "chinese_documents": chinese_docs,
            "failures": failures}, decoded


def start_check(root: Path, manifest: dict) -> dict:
    details, failures = {}, []
    for slug, author in manifest["authors"].items():
        start_path = root / author["copy"]["start"]["path"]
        start = start_path.read_text(encoding="utf-8")
        rules = {
            "correct_author_and_version": author["label"] in start and f'V{author["method_version"]}' in start,
            "requires_actual_full_text_or_parts": "完整方法全文或各分段" in start and "实际可读" in start,
            "short_start_is_not_full_method": "启动说明不是完整方法" in start,
            "task_follows_method_loading": "方法资料发送完毕后，我会另发任务" in start,
            "no_creation_during_loading": "只确认资料接收，不开始创作" in start,
            "finite_context_boundary": "有限上下文版本" in start,
            "does_not_claim_full_loading_from_start_alone": "不要仅凭这一句声称已加载完整方法" in start,
        }
        details[slug] = rules
        failures.extend({"path": start_path.relative_to(root).as_posix(), "rule": rule}
                        for rule, passed in rules.items() if not passed)
    return {"result": "pass" if not failures else "fail", "authors": details, "failures": failures}


def standalone_assets_check(root: Path, manifest: dict) -> dict:
    directory = root.parent / "release-assets"
    failures, links_checked, copies = [], 0, []
    for name, adaptation in manifest.get("documentation_adaptations", {}).items():
        file = directory / name
        text = file.read_text(encoding="utf-8")
        source = (root / adaptation["source"]).read_text(encoding="utf-8")
        # Compare every non-target character, including copyright prose.
        normalize = lambda value: INLINE_LINK.sub(lambda m: f"[{m.group(1)}](TARGET)", value)
        unchanged = normalize(text) == normalize(source)
        copies.append({"path": f"../release-assets/{name}", "source": adaptation["source"],
                       "only_link_targets_changed": unchanged})
        if not unchanged:
            failures.append({"path": f"../release-assets/{name}", "error": "document prose changed"})
        for line_number, raw in visible_lines(text):
            for match in INLINE_LINK.finditer(without_inline_code(raw)):
                target = match.group(2).strip("<>")
                parsed = urlsplit(target)
                links_checked += 1
                issue = {"path": f"../release-assets/{name}", "line": line_number, "target": target}
                if not (parsed.scheme or parsed.netloc or target.startswith("#")):
                    failures.append({**issue, "error": "standalone document retains a relative file link"})
                prefix = "https://github.com/Bananaaayee/creator-methods-skills/"
                if target.startswith(prefix):
                    tail = unquote(parsed.path).split("/creator-methods-skills/", 1)[1]
                    for kind in ("blob/main/", "tree/main/"):
                        if tail.startswith(kind) and not (root / tail[len(kind):]).exists():
                            failures.append({**issue, "error": "main-branch reading URL has no corresponding local file"})
    return {"result": "pass" if not failures else "fail", "documents": copies,
            "links_checked": links_checked, "no_release_download_urls_constructed": True,
            "failures": failures}


def clean_error(error: Exception, root: Path) -> str:
    # Public reports never carry machine-specific absolute paths.
    return str(error).replace(str(root), "<repo>").replace(str(root.parent), "<release-root>") or type(error).__name__


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true", help="Run build_release.py --assets --check before read-only checks.")
    parser.add_argument("--report", default="tests/distribution-result.json", help="Repository-relative report output.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    report_path = (root / args.report).resolve()
    if not report_path.is_relative_to(root):
        parser.error("The report must be inside this repository")
    rebuild = {"requested": args.rebuild, "result": "not requested"}
    if args.rebuild:
        process = subprocess.run([sys.executable, "scripts/build_release.py", "--assets", "--check"],
                                 cwd=root, capture_output=True, text=True, encoding="utf-8")
        rebuild = {"requested": True, "result": "pass" if process.returncode == 0 else "fail",
                   "exit_code": process.returncode}
        if process.returncode:
            rebuild["error"] = clean_error(RuntimeError(process.stderr.strip()), root)
    files = sorted(p.resolve() for p in root.rglob("*") if p.is_file()
                   and p.suffix.lower() in TEXT_SUFFIXES and not any(x in IGNORED_PARTS for x in p.parts)
                   and p.resolve() != report_path)
    encoding, decoded = encoding_check(root, files)
    markdown = [p for p in files if p.suffix.lower() == ".md" and p in decoded]
    links = local_links(root, markdown, decoded)
    manifest = json.loads((root / "distribution-manifest.json").read_text(encoding="utf-8"))
    starts = start_check(root, manifest)
    standalone = standalone_assets_check(root, manifest)
    try:
        builder = runpy.run_path(str(root / "scripts" / "build_release.py"), run_name="atlas_distribution_builder")
        existing = builder["validate"](root, manifest, "archives" in manifest)
        content = {"result": "pass", "verification": existing}
    except (OSError, ValueError, AssertionError) as error:
        content = {"result": "fail", "error": clean_error(error, root)}
    result = "pass" if all(r["result"] != "fail" for r in (rebuild, encoding, links, starts, standalone, content)) else "fail"
    report = {
        "schema_version": 1, "release_tag": manifest["release_tag"], "result": result,
        "scope": "Offline local distribution verification; no model quality evaluation, browser, network, or remote installation claims.",
        "path_policy": "All report paths are relative to the repository, including ../release-assets/ for sibling assets; the report excludes itself from text-file counts.",
        "builder_rebuild": rebuild, "encoding_and_chinese": encoding, "relative_links": links,
        "short_start_boundaries": starts, "existing_builder_content_checks": content,
        "standalone_asset_document_navigation": standalone,
        "method_source_policy": "The builder verifies all 29 immutable runtime sources against embedded SHA-256 baselines.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({"result": result, "report": report_path.relative_to(root).as_posix(),
                      "relative_links": links["relative_links_checked"], "broken_links": len(links["failures"]),
                      "text_files": len(files)}, ensure_ascii=False))
    return 0 if result == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
