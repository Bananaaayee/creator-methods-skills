#!/usr/bin/env python3
"""Deterministic, standard-library-only Creator Methods Atlas V3 builder.

Runtime sources under skills/ are read only. Portable Markdown and text files
contain identical UTF-8 bytes. Every copy segment carries a removable delivery
envelope; payload offsets/lengths in the manifest reconstruct the exact text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import stat
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

EXPECTED_SOURCE_HASHES = {'he-tongxue-creator': {'01_portable_instruction.md': '9d978acc3d8acc8502594808a325137b6ba572381746ebc162f9a5c651015daa', '02_domain_kernel.md': '5b98456d77222be035ee4a0eebfb34096f83d8ada73fa0417c69a2d2c420248f', '03_product_policy.md': '16aca488b2936379e4e150d73d54701c1227d23dfbc0f77827d052a464dc7d01', '04_runtime_state.md': 'f3e2c9da399657d41f4165f34af6c99c3d2582dcfd92c5216180ead6069db49f', '05_decision_logic.md': '3c8c5399e5c27792b5d28f105105a473222fcae61e5bd033529d6899376b8f8b', '06_research_boundary.md': 'c75c0a614bb2f21ea543b42c50e3790bc9114ef9263d707b293785b1e25ec829', 'SKILL.md': '9773c8a9f7858a12ad33f88b8847e552d5770ed09103bda929e522c0637c3200', 'references/decision-tools.md': 'a51ce78ed7ed849e5a970fd4ebad2addfb99a9e1d002755b60fe94358417cb94', 'references/evidence-index.md': '4e1afecac5317543ba338680e0bb6bd8fdd0078e7c728472ca95e14610cc8617', 'references/work-registry.md': '38f0ce2f3e820e140e4f7ec41bac9a900a52abe400a9f4d86c7f21fb2fdc608d'}, 'lawrence-creator': {'01_portable_instruction.md': '55a96b96e2845a38b415af039dc6925af3901ac28869ba5e4190e6d8f8950f32', '02_domain_kernel.md': '58a3c214edd43b3d8620e26afa278257f7d119bc5c5344272e50a3e5d83c6977', '03_product_policy.md': 'd9e6dc54721a79ed82d09b71bdb62edc7b0e73708ca8754d485bee8812a88c36', '04_runtime_state.md': 'fbcb8dc401bba0e94ae84fe9aea999ef4ecce1c9ce6b6badd745974ba681f9a5', '05_decision_logic.md': 'c62d93069286a426dbc9bfd29256444c0a8f2cfb75bce067b4e8ba9f77109844', '06_research_boundary.md': 'ed1a0e673543e9ca52ea7008aff089d805d8ee4d2582949b5d945999842b7193', 'SKILL.md': '1674dc167a67e6575ab1ecaf9d0bba353a65b0b32603a8217832c653a203fc02', 'references/evidence-index.md': 'fb47c30a3c90cc58dd0438c0bb1703f487b6370f5a634ebbf6febd3989547b8b', 'references/method-bridges.md': 'a12c578cc51b9c1fffbe41205f183509c8ca9e66fd970a79dfab7ab1dfcbe2cf', 'references/work-registry.md': '82d80fa0e8a43979988405e7790c0d62521a5ddaae86e128be22e01df1d6875b'}, 'media-storm-creator': {'01_portable_instruction.md': 'ecade84ceec05c0d5005411c555c417f3c348477cb6e3470901a2cabba3a7aba', '02_domain_kernel.md': '7d9010b059d1297bf7d1acda9622649fd25e165d0d68f07a6b54e7eed5e629aa', '03_product_policy.md': 'ad52d11da56244ff7caa87dcda454b45844fd3fcf96956e52dceb7eda63fcad4', '04_runtime_state.md': '8846153593e0b2fa5f8288cfddf6cf4cf3751adab667d250df5c9df9ba601bc4', '05_decision_logic.md': '87870c99879437fd0cead8461a85a83d04c9d06f6b5d41a280439d8d9c43bdc9', '06_research_boundary.md': 'df6b0bf8ed629c5585bd51ce7aa87c4cec6b03ac27896a73b16ca9229e8bfa0c', 'SKILL.md': '03336a9c4f63faf89024ecbf65543cad459177eb16c12cca7c789893c964b348', 'references/evidence-vnext.md': '47cbed9650b772981024e45f2c002b2c9345cf6a91822fb2fe84ce3d2a1c73fa', 'references/legacy-work-library.md': '16b70c14294f49e5d995d6b91f9955cd42440e9b268ccadd723b416fcb8540a1'}}
RELEASE = "atlas-v3-2026.10.25"
MAINTAINER = "BANANAAAYEE"
REPOSITORY_URL = "https://github.com/Bananaaayee/creator-methods-skills"
ZIP_DATE = (2026, 10, 25, 0, 0, 0)
CHUNK_LIMIT = 8000
PAYLOAD_LIMIT = 7400
BEGIN_MARKER = "=== ATLAS METHOD PAYLOAD BEGIN ===\n"
END_MARKER = "\n=== ATLAS METHOD PAYLOAD END ===\n"
AUTHORS = (
    ("he-tongxue-creator", "Hetongxue", "何同学", "1.3.0"),
    ("lawrence-creator", "Lawrence", "小鹿 Lawrence", "1.3.0"),
    ("media-storm-creator", "MediaStorm", "影视飓风", "1.22.0"),
)
ROOT_ASSETS = (
    ("README.md", "README.md"),
    ("DISCLAIMER.md", "DISCLAIMER.md"),
    ("CHANGELOG.md", "CHANGELOG.md"),
    ("KNOWN_LIMITS.md", "KNOWN_LIMITS.md"),
    ("docs/使用指南.md", "Cross-Platform-Guide.zh-CN.md"),
)
MD_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^\s)]+)\)")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def describe(data: bytes, *, is_text: bool = True) -> dict:
    result = {"sha256": sha(data), "bytes": len(data)}
    if is_text:
        result["characters"] = len(data.decode("utf-8"))
        result["encoding"] = "UTF-8"
    return result


def write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def runtime_order(names: dict) -> list[str]:
    return ["SKILL.md"] + sorted(name for name in names if name != "SKILL.md")


def anchor(path: str) -> str:
    return "source-" + re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")


def inspect_sources(root: Path) -> tuple[dict, dict]:
    blobs, records = {}, {}
    for slug, expected in EXPECTED_SOURCE_HASHES.items():
        blobs[slug], records[slug] = {}, {}
        for name in runtime_order(expected):
            path = root / "skills" / slug / name
            data = path.read_bytes()
            if sha(data) != expected[name]:
                raise ValueError(f"Read-only runtime source differs from baseline: {slug}/{name}")
            data.decode("utf-8", errors="strict")
            blobs[slug][name] = data
            records[slug][name] = describe(data)
        # An installer must find exactly one canonical entry file per author.
        entries = sorted(p.relative_to(root / "skills" / slug).as_posix()
                         for p in (root / "skills" / slug).rglob("SKILL.md"))
        if entries != ["SKILL.md"]:
            raise ValueError(f"Duplicate or missing skill entry in {slug}: {entries}")
    if sum(map(len, records.values())) != 29:
        raise ValueError("The release must include exactly 29 runtime sources")
    return blobs, records


def render_source(name: str, text: str, all_names: set[str]) -> tuple[str, int]:
    converted = 0

    def replace(match: re.Match) -> str:
        nonlocal converted
        label, target = match.groups()
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            return match.group(0)
        if not parsed.path.lower().endswith(".md"):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
        if resolved not in all_names:
            raise ValueError(f"Unresolved relative Markdown dependency: {name} -> {target}")
        # Current runtime sources have no section fragments. Fail visibly if one
        # is introduced, rather than silently dropping its original meaning.
        if parsed.fragment or parsed.query:
            raise ValueError(f"A section-specific source link needs an explicit mapping: {name} -> {target}")
        converted += 1
        return f"[{label}](#{anchor(resolved)})"

    return MD_LINK.sub(replace, text), converted


def make_portable(slug: str, prefix: str, label: str, version: str, blobs: dict) -> tuple[str, list, int]:
    names = runtime_order(blobs)
    title = f"{label}创作方法 · 完整便携版"
    header = (
        f"# {title}\n\n"
        f"方法版本：{version}｜发行标签：{RELEASE}｜维护者：{MAINTAINER}\n\n"
        "第三方独立研究与整理，未经相关创作者或团队官方授权，不代表其立场、代言或合作。"
        "用于理解公开作品中的创作方法，不用于冒充本人；研究解释不等于作者未公开的内心或团队决策。\n\n"
        "**这是完整方法全文，与一句启动短句不同。** 本文件完整嵌入该方法的入口、六个运行模块与全部随包参考载荷。"
        "单独保存并提供本文即可使用，无需另外下载原始语料、其他方法文件或安装 Python。"
        "正文里的相对 Markdown 文件链接已指向本文内部锚点；反引号里的原始文件路径仅为证据定位，"
        "不表示使用前必须另找这些材料。缺少原始材料时，仍须遵守正文对作品覆盖、事实与研究范围的限定。\n\n"
        "本文件采用 UTF-8；同名 .md 和 .txt 的全文字节完全相同。.txt 是可直接复制的 UTF-8 纯文本，"
        "保留 # 标题、列表、反引号与锚点等可读格式标记，这些标记不影响将内容提供给 AI 使用。\n\n"
        "请先加载本文，再发送具体创作任务。提供了完整文件不等于平台已经读完或能持续保留全部内容；"
        "平台若截断、遗漏附件或丢失前文，只能按实际仍可见内容作为“有限上下文版本”使用，"
        "不得宣称已完整加载，也不保证与完整上下文效果等同。\n\n"
        "## 内嵌文件目录\n\n"
    )
    toc = "".join(f"- [{name}](#{anchor(name)})\n" for name in names)
    out = [header, toc, "\n"]
    sections, converted = [], 0
    for name in names:
        original = blobs[name].decode("utf-8")
        rendered, links = render_source(name, original, set(names))
        lead = (f'\n<a id="{anchor(name)}"></a>\n\n'
                f"## 内嵌原文件：{name}\n\n"
                f"原始位置：`skills/{slug}/{name}`；SHA-256：`{sha(blobs[name])}`。\n\n")
        start = sum(map(len, out)) + len(lead)
        out.extend((lead, rendered, "\n"))
        sections.append({
            "source": f"skills/{slug}/{name}", "anchor": anchor(name),
            "source_sha256": sha(blobs[name]), "rendered_sha256": sha(rendered.encode("utf-8")),
            "rendered_characters": len(rendered), "portable_character_start": start,
            "portable_character_end": start + len(rendered), "links_rewritten": links,
        })
        converted += links
    return "".join(out), sections, converted


def split_payload(text: str) -> list[str]:
    """Prefer paragraph ends, then line ends; never add/drop a character."""
    chunks = []
    start = 0
    while start < len(text):
        if len(text) - start <= PAYLOAD_LIMIT:
            end = len(text)
        else:
            limit = start + PAYLOAD_LIMIT
            paragraph = text.rfind("\n\n", start + 1, limit)
            line = text.rfind("\n", start + 1, limit)
            if paragraph >= start + PAYLOAD_LIMIT // 2:
                end = paragraph + 2
            elif line >= start:
                end = line + 1
            else:
                raise ValueError("A source line exceeds the segment budget; manual review required")
        chunks.append(text[start:end])
        start = end
    if "".join(chunks) != text:
        raise AssertionError("Payload splitting did not preserve the original text")
    return chunks


def envelope(label: str, i: int, total: int) -> str:
    return (
        f"资料加载阶段｜{label}完整方法｜第 {i:02d}/{total:02d} 段\n"
        f"请载入以下原文切片，本条只回复“收到第 {i:02d}/{total:02d} 段”。"
        "全部段落发送结束且我另发任务之前，不开始创作，不总结或改写方法。\n"
        "未收齐时不得声称已完整加载；即使段号收齐，若平台无法保留或读取全部前文，"
        "请明确说“有限上下文版本”，只使用仍可见内容。包装中的段号与标记不是方法正文。\n\n"
        + BEGIN_MARKER
    )


def fence_for(text: str) -> str:
    longest = max((len(m.group(0)) for m in re.finditer(r"`+", text)), default=0)
    return "`" * max(8, longest + 1)


def make_copy(root: Path, prefix: str, label: str, version: str, text: str) -> dict:
    directory = root / "copy" / prefix
    parts_dir = directory / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    for stale in parts_dir.glob("*-of-*.txt"):
        stale.unlink()
    payloads = split_payload(text)
    chunks = []
    start_char = start_byte = 0
    for i, payload in enumerate(payloads, 1):
        lead = envelope(label, i, len(payloads))
        whole = lead + payload + END_MARKER
        if len(whole) > CHUNK_LIMIT:
            raise ValueError(f"Copy segment exceeds {CHUNK_LIMIT} characters")
        name = f"{i:02d}-of-{len(payloads):02d}.txt"
        data = whole.encode("utf-8")
        write(parts_dir / name, data)
        payload_bytes = payload.encode("utf-8")
        chunks.append({
            "path": f"copy/{prefix}/parts/{name}", "number": i,
            **describe(data), "payload_sha256": sha(payload_bytes),
            "payload_characters": len(payload), "payload_bytes": len(payload_bytes),
            "payload_start_character_in_part": len(lead),
            "payload_start_byte_in_part": len(lead.encode("utf-8")),
            "payload_start_character_in_full_text": start_char,
            "payload_start_byte_in_full_text": start_byte,
        })
        start_char += len(payload)
        start_byte += len(payload_bytes)
    start = (
        f"请准备使用{label}创作方法 V{version}协作，保留我的事实、表达和当前任务范围。"
        "我将提供或已经提供完整方法全文或各分段；这句启动说明不是完整方法。"
        "先确认方法资料是否实际可读；在我发送完方法资料并另发具体任务之前，只确认资料接收，不开始创作。"
        "缺少内容时明确说明只按“有限上下文版本”使用，不要仅凭这一句声称已加载完整方法。"
        "方法资料发送完毕后，我会另发任务。\n"
    )
    task = (
        "现在进入任务阶段。\n"
        "我的任务：[例如：从已有素材整理一支 3 分钟视频的结构，或只改下面一段旁白。]\n"
        "已有材料：[粘贴真实素材、现有稿件、可核对事实及已知缺口。]\n"
        "需要的交付：[具体成品、长度、受众和格式。]\n"
        "保留或锁定：[必须保留的事实、表达、结构，以及不需要修改的部分。]\n"
        "请按本次已实际加载的方法和我的要求完成；材料不足时标明，不编造经历或结果。\n"
    )
    write(directory / "START.txt", start)
    write(directory / "TASK.txt", task)
    fence = fence_for(text)
    listing = "".join(
        f'- [{c["path"].split("/")[-1]}](parts/{c["path"].split("/")[-1]})：'
        f'{c["characters"]:,} 字符（含加载包装），正文 {c["payload_characters"]:,} 字符\n'
        for c in chunks
    )
    readme = (
        f"# {label}：复制即用\n\n"
        f"方法版本 {version} · {RELEASE} · 维护者 {MAINTAINER}\n\n"
        "第三方独立整理，非创作者官方出品，未经其授权或背书。用于学习公开作品方法，保留你自己的表达。\n\n"
        "## 先选一种加载方式\n\n"
        f"1. 能上传文件：提供 [完整 TXT](../../portable/{prefix}-Portable.txt) 或 "
        f"[完整 Markdown](../../portable/{prefix}-Portable.md)，确认平台实际读取后再发任务。\n"
        "2. 能一次粘贴全文：复制下一节完整代码块的全部正文，不复制最外侧围栏，作为第一条资料消息发送。\n"
        "3. 需要分段：打开[编号分段目录](parts/)，从 01 开始按顺序逐条发送各文件的完整内容，包含加载包装。"
        "每段只让 AI 确认段号；全部发送完毕后，再发送你的任务。不要跳段。\n\n"
        f"短启动指令见 [START.txt](START.txt)：它只启动协作，**不是完整 Skill**，不能代替全文。"
        "完成加载后，可用 [TASK.txt](TASK.txt) 写任务。不同平台使用同一份方法，不另写一套规则。\n\n"
        "每段不超过 8,000 个 Unicode 字符，数字包括加载包装，并非所有平台统一支持的输入或上下文上限。"
        "平台若仍截断单条消息、无法读取附件或无法保留全部段落，只能明确按“有限上下文版本”使用；"
        "收齐段号不等于仍持有全部正文，不得宣称完整加载或承诺效果等同。\n\n"
        "## 一次整体复制：完整方法\n\n"
        "以下代码块与对应完整 TXT 字节相同，包含所有运行模块及参考载荷，不是摘要。"
        "格式标记可保留，无需安装 Python 或另外下载研究语料。\n\n"
        + fence + "text\n" + text + fence + "\n\n"
        "## 任务例\n\n"
        "“我有一段 650 字旁白，只希望减少重复、让两处逻辑衔接更清楚。"
        "保留叙事顺序、事实、立场和我的口吻，请直接给修改稿并简述必要改动。”\n\n"
        "“下面是我实际拍到的素材和缺失镜头。请根据材料组织一支 3 分钟视频的结构，"
        "标明哪些主张已有证据、哪些只能作为待拍计划，不替我编造结果。”\n\n"
        "## 分段目录\n\n"
        f"共 {len(chunks)} 段。每个文件都可以整体直接复制；外层包装负责加载顺序，正文切片逐字保留。"
        "构建清单记录了正文的精确偏移、长度与 SHA-256，可去除包装后逐字重组为完整 TXT。\n\n"
        + listing
    )
    write(directory / "README.md", readme)
    return {
        "readme": {"path": f"copy/{prefix}/README.md", **describe(readme.encode("utf-8"))},
        "start": {"path": f"copy/{prefix}/START.txt", **describe(start.encode("utf-8"))},
        "task": {"path": f"copy/{prefix}/TASK.txt", **describe(task.encode("utf-8"))},
        "full_copy_fence_characters": len(fence), "chunks": chunks,
        "chunk_count": len(chunks), "maximum_part_characters": CHUNK_LIMIT,
        "maximum_payload_characters": PAYLOAD_LIMIT,
        "reconstructed_payload": describe(text.encode("utf-8")),
        "reconstruction": "In listed order, slice each UTF-8-decoded part at payload_start_character_in_part for payload_characters, then concatenate. Byte offsets provide an equivalent exact extraction.",
    }


def skill_entries(root: Path, slug: str) -> dict[str, bytes]:
    base = root / "skills" / slug
    result = {}
    for p in sorted(base.rglob("*")):
        if p.is_file() and not any(x in {".git", "__pycache__", ".DS_Store"} for x in p.parts):
            if p.suffix in {".pyc", ".pyo"}:
                continue
            result[f"{slug}/{p.relative_to(base).as_posix()}"] = p.read_bytes()
    for doc in ("README.md", "DISCLAIMER.md"):
        if f"{slug}/{doc}" not in result:
            raise ValueError(f"Skill archive requires its user-facing {slug}/{doc}")
    return result


def deterministic_zip(path: Path, entries: dict[str, bytes]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for name, data in sorted(entries.items()):
            if name.startswith("/") or ".." in Path(name).parts:
                raise ValueError(f"Unsafe archive entry: {name}")
            info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    return {
        **describe(path.read_bytes(), is_text=False), "entries": sorted(entries),
        "entry_count": len(entries), "compression": "ZIP_STORED",
        "fixed_timestamp": list(ZIP_DATE), "unix_file_mode": "100644",
    }


def adapt_document(root: Path, source: str, data: bytes, *, portable_archive: bool) -> tuple[bytes, int]:
    """Change navigation only; repository files themselves remain untouched."""
    local_portable = {f"portable/{prefix}-Portable.{ext}": f"{prefix}-Portable.{ext}"
                      for _, prefix, _, _ in AUTHORS for ext in ("md", "txt")}
    changed = 0

    def replace(match: re.Match) -> str:
        nonlocal changed
        label, target = match.groups()
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path)))
        if resolved.startswith("../"):
            raise ValueError(f"Document link escapes repository: {source} -> {target}")
        if portable_archive and resolved in local_portable:
            dest = local_portable[resolved]
        else:
            kind = "tree" if (root / resolved).is_dir() or parsed.path.endswith("/") else "blob"
            dest = f"{REPOSITORY_URL}/{kind}/main/{quote(resolved, safe='/')}"
        if parsed.query:
            dest += "?" + parsed.query
        if parsed.fragment:
            dest += "#" + parsed.fragment
        changed += 1
        return f"[{label}]({dest})"

    text = MD_LINK.sub(replace, data.decode("utf-8"))
    return text.encode("utf-8"), changed


def portable_start() -> bytes:
    listing = "".join(f"- {label} V{version}：[完整 TXT]({prefix}-Portable.txt) · "
                      f"[同内容 Markdown]({prefix}-Portable.md)\n"
                      for _, prefix, label, version in AUTHORS)
    return (
        "# 先从这里开始\n\n"
        "本合集根目录的六个完整方法文件可在本地直接打开、复制或作为附件使用，"
        "不需要安装 Python，也不依赖在线仓库、原始语料或其他方法文件。每位创作者的 TXT 与 Markdown 字节相同，任选其一。\n\n"
        + listing + "\n"
        "先让平台读取一份完整方法，再发具体任务。短启动词不能代替全文；"
        "附件被截断或上下文无法保留全部内容时，只能明确按“有限上下文版本”使用。\n\n"
        "跨平台步骤见本地 [Cross-Platform-Guide.zh-CN.md](Cross-Platform-Guide.zh-CN.md)，"
        "独立声明与限制见本地 [DISCLAIMER.md](DISCLAIMER.md)、[KNOWN_LIMITS.md](KNOWN_LIMITS.md)。\n\n"
        f"更多下载页面、分段复制、安装与验证资料链接到[在线仓库]({REPOSITORY_URL})。"
        "仓库当前为 Private，在线页面是否可读受你的访问权限与维护者后续公开状态约束；"
        "本合集内的六个完整文件仍可独立使用。\n\n"
        f"{RELEASE} · 维护者 {MAINTAINER} · 第三方独立整理，非相关创作者官方出品。\n"
    ).encode("utf-8")


def build(root: Path, assets: bool) -> tuple[dict, list[Path]]:
    blobs, records = inspect_sources(root)
    manifest = {
        "schema_version": 1, "release_tag": RELEASE, "maintainer": MAINTAINER,
        "source_policy": "Only skills/<name>/ runtime files are method sources; they are read-only and verified against 29 embedded SHA-256 baselines.",
        "runtime_source_file_count": sum(map(len, records.values())),
        "runtime_sources": records, "authors": {},
        "portable_policy": "The .md and .txt variants contain identical UTF-8 bytes. Source bodies are retained in full; only relative Markdown file links are rewritten to explicit internal anchors.",
        "archive_policy": {"timestamp": list(ZIP_DATE), "compression": "ZIP_STORED", "unix_file_mode": "100644", "sorted_entries": True},
    }
    generated = []
    for slug, prefix, label, version in AUTHORS:
        text, sections, links = make_portable(slug, prefix, label, version, blobs[slug])
        data = text.encode("utf-8")
        full = {}
        for ext in ("md", "txt"):
            path = root / "portable" / f"{prefix}-Portable.{ext}"
            write(path, data)
            full[ext] = {"path": path.relative_to(root).as_posix(), **describe(data)}
            generated.append(path)
        copy = make_copy(root, prefix, label, version, text)
        generated.extend((root / v["path"]) for k, v in copy.items() if k in {"readme", "start", "task"})
        generated.extend(root / c["path"] for c in copy["chunks"])
        manifest["authors"][slug] = {
            "label": label, "method_version": version, "portable": full,
            "source_sections": sections, "relative_links_rewritten": links, "copy": copy,
        }
    if assets:
        asset_dir = root.parent / "release-assets"
        asset_dir.mkdir(parents=True, exist_ok=True)
        asset_records, portable_entries, skill_all, archives, doc_adaptations = {}, {}, {}, {}, {}
        for path in sorted(root.joinpath("portable").glob("*-Portable.*")):
            if path.suffix not in {".md", ".txt"}:
                continue
            data = path.read_bytes()
            write(asset_dir / path.name, data)
            asset_records[path.name] = describe(data)
            portable_entries[path.name] = data
        for source, dest in ROOT_ASSETS:
            data = (root / source).read_bytes()
            standalone, standalone_changes = adapt_document(root, source, data, portable_archive=False)
            bundled, bundled_changes = adapt_document(root, source, data, portable_archive=True)
            write(asset_dir / dest, standalone)
            asset_records[dest] = describe(standalone)
            portable_entries[dest] = bundled
            doc_adaptations[dest] = {
                "source": source, "source_sha256": sha(data),
                "standalone_sha256": sha(standalone), "standalone_links_rewritten": standalone_changes,
                "portable_archive_sha256": sha(bundled), "portable_archive_links_rewritten": bundled_changes,
                "policy": "Only relative navigation targets change. Standalone assets link to explicit GitHub reading pages; in the portable ZIP, links to six full method files stay local and other repository paths point to GitHub reading pages.",
            }
        portable_entries["START-HERE.md"] = portable_start()
        for slug, _, _, _ in AUTHORS:
            entries = skill_entries(root, slug)
            skill_all.update(entries)
            name = f"{slug}.zip"
            archives[name] = deterministic_zip(asset_dir / name, entries)
        archives["Creator-Methods-Atlas-Skills.zip"] = deterministic_zip(asset_dir / "Creator-Methods-Atlas-Skills.zip", skill_all)
        archives["Creator-Methods-Atlas-Portable.zip"] = deterministic_zip(asset_dir / "Creator-Methods-Atlas-Portable.zip", portable_entries)
        manifest["archives"] = archives
        manifest["documentation_adaptations"] = doc_adaptations
        manifest["release_assets"] = asset_records
        manifest["release_assets_self_reference"] = "distribution-manifest.json and SHA256SUMS are omitted from this manifest's asset inventory to avoid cyclic hashes. SHA256SUMS includes the manifest, every named release asset and every archive, and excludes itself."
        generated.extend(asset_dir / name for name in [*asset_records, *archives])
    write(root / "distribution-manifest.json", json_bytes(manifest))
    generated.append(root / "distribution-manifest.json")
    if assets:
        asset_dir = root.parent / "release-assets"
        write(asset_dir / "distribution-manifest.json", json_bytes(manifest))
        listed = sorted([*manifest["release_assets"], *manifest["archives"], "distribution-manifest.json"])
        sums = "".join(f"{sha((asset_dir / name).read_bytes())}  {name}\n" for name in listed)
        write(asset_dir / "SHA256SUMS", sums)
        generated.extend([asset_dir / "distribution-manifest.json", asset_dir / "SHA256SUMS"])
    inspect_sources(root)
    return manifest, generated


def validate(root: Path, manifest: dict, assets: bool) -> dict:
    checks = {
        "source_runtime_file_count": 29, "source_hashes_unchanged": True,
        "utf8_strict_decode": True, "portable_md_txt_identical": True,
        "all_29_source_bodies_fully_embedded": True,
        "relative_markdown_links_resolve_to_internal_anchors": True,
        "copy_readme_contains_exact_full_txt": True,
        "parts_include_loading_envelope": True,
        "parts_at_most_8000_characters_including_envelope": True,
        "parts_payload_reconstructs_exact_txt": True,
        "no_extra_skill_entry_files": True, "authors": {},
    }
    blobs, _ = inspect_sources(root)
    for slug, prefix, _, _ in AUTHORS:
        author = manifest["authors"][slug]
        text_bytes = (root / author["portable"]["txt"]["path"]).read_bytes()
        text = text_bytes.decode("utf-8", errors="strict")
        assert text_bytes == (root / author["portable"]["md"]["path"]).read_bytes()
        assert describe(text_bytes) == {k: v for k, v in author["portable"]["txt"].items() if k != "path"}
        anchors = re.findall(r'<a id="([^"]+)"></a>', text)
        assert len(anchors) == len(set(anchors)) == len(blobs[slug])
        for match in MD_LINK.finditer(text):
            target = match.group(2)
            if target.startswith("#"):
                assert target[1:] in anchors, target
            else:
                parsed = urlsplit(target)
                assert parsed.scheme or parsed.netloc or not parsed.path.lower().endswith(".md"), target
        for section in author["source_sections"]:
            name = section["source"].split(f"skills/{slug}/", 1)[1]
            rendered, _ = render_source(name, blobs[slug][name].decode("utf-8"), set(blobs[slug]))
            assert text[section["portable_character_start"]:section["portable_character_end"]] == rendered
        copy = author["copy"]
        readme = (root / copy["readme"]["path"]).read_text(encoding="utf-8")
        fence = "`" * copy["full_copy_fence_characters"]
        assert fence + "text\n" + text + fence + "\n" in readme
        char_pieces, byte_pieces = [], []
        for c in copy["chunks"]:
            part_bytes = (root / c["path"]).read_bytes()
            part = part_bytes.decode("utf-8", errors="strict")
            assert len(part) <= CHUNK_LIMIT
            assert part.startswith("资料加载阶段｜") and "不开始创作" in part and "有限上下文版本" in part
            offset = c["payload_start_character_in_part"]
            payload = part[offset:offset + c["payload_characters"]]
            byte_start = c["payload_start_byte_in_part"]
            byte_payload = part_bytes[byte_start:byte_start + c["payload_bytes"]]
            assert payload.encode("utf-8") == byte_payload
            assert sha(byte_payload) == c["payload_sha256"]
            assert part[:offset].endswith(BEGIN_MARKER)
            assert part[offset + c["payload_characters"]:] == END_MARKER
            char_pieces.append(payload)
            byte_pieces.append(byte_payload)
        assert "".join(char_pieces) == text
        assert b"".join(byte_pieces) == text_bytes
        checks["authors"][slug] = {
            "runtime_sources": len(blobs[slug]), "portable": describe(text_bytes),
            "parts": copy["chunk_count"], "maximum_part_characters": max(c["characters"] for c in copy["chunks"]),
            "reconstructed_sha256": sha(b"".join(byte_pieces)),
            "links_rewritten": author["relative_links_rewritten"],
        }
    if assets:
        asset_dir = root.parent / "release-assets"
        for name, record in manifest["archives"].items():
            path = asset_dir / name
            assert sha(path.read_bytes()) == record["sha256"]
            with zipfile.ZipFile(path) as z:
                assert z.namelist() == record["entries"] == sorted(z.namelist())
                assert z.testzip() is None
                for info in z.infolist():
                    assert info.date_time == ZIP_DATE
                    assert info.compress_type == zipfile.ZIP_STORED
                    assert info.external_attr >> 16 == stat.S_IFREG | 0o644
                    assert ".git" not in Path(info.filename).parts
                    assert "__pycache__" not in Path(info.filename).parts
                    if info.filename.endswith("/SKILL.md"):
                        assert len(Path(info.filename).parts) == 2
                    parts = Path(info.filename).parts
                    if parts[0] in EXPECTED_SOURCE_HASHES:
                        rel = Path(*parts[1:]).as_posix()
                        if rel in EXPECTED_SOURCE_HASHES[parts[0]]:
                            assert sha(z.read(info)) == EXPECTED_SOURCE_HASHES[parts[0]][rel]
                    if name == "Creator-Methods-Atlas-Portable.zip" and info.filename.endswith(".md"):
                        for link in MD_LINK.finditer(z.read(info).decode("utf-8")):
                            target = urlsplit(link.group(2))
                            if target.scheme or target.netloc or link.group(2).startswith("#"):
                                continue
                            assert unquote(target.path) in z.namelist(), (info.filename, link.group(2))
        for name, adaptation in manifest["documentation_adaptations"].items():
            assert sha((root / adaptation["source"]).read_bytes()) == adaptation["source_sha256"]
            text = (asset_dir / name).read_text(encoding="utf-8")
            for link in MD_LINK.finditer(text):
                target = urlsplit(link.group(2))
                assert target.scheme or target.netloc or link.group(2).startswith("#"), (name, link.group(2))
        checksum_lines = (asset_dir / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        for line in checksum_lines:
            digest, name = line.split("  ", 1)
            assert sha((asset_dir / name).read_bytes()) == digest
        assert (asset_dir / "distribution-manifest.json").read_bytes() == (root / "distribution-manifest.json").read_bytes()
        checks["deterministic_archives_and_runtime_bytes_verified"] = True
        checks["release_checksums_verified"] = True
        checks["portable_archive_local_navigation_resolves"] = True
        checks["standalone_document_navigation_uses_repository_reading_urls"] = True
        checks["repository_document_sources_unchanged"] = True
        checks["release_asset_count_including_checksums"] = len(checksum_lines) + 1
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", action="store_true", help="Also build sibling release-assets/ (requires all root and per-skill user documents).")
    parser.add_argument("--check", action="store_true", help="Validate all content and rebuild to confirm byte-for-byte repeatability.")
    parser.add_argument("--check-report", type=Path, help="Write the verification report to this path; implies --check.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        manifest, paths = build(root, args.assets)
        report = None
        if args.check or args.check_report:
            report = validate(root, manifest, args.assets)
            first = {str(path): sha(path.read_bytes()) for path in paths}
            manifest2, paths2 = build(root, args.assets)
            second = {str(path): sha(path.read_bytes()) for path in paths2}
            assert first == second, "Repeated build changed generated bytes or its output inventory"
            assert manifest == manifest2
            validate(root, manifest2, args.assets)
            report["repeated_build_byte_identical"] = True
            report["generated_file_count"] = len(paths)
            report["result"] = "pass"
            report["release_tag"] = RELEASE
            if args.check_report:
                write(args.check_report.resolve(), json_bytes(report))
        print(json.dumps({"release_tag": RELEASE, "authors": len(AUTHORS), "source_files": 29,
                          "generated_files": len(paths), "assets": args.assets,
                          "checks": report["result"] if report else "not requested"}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, AssertionError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
