"""编码探测与转 UTF-8。

网络下载的中文 TXT 多为 GBK/GB18030/ANSI 甚至带 BOM。这里用 charset-normalizer
做主探测，并对中文场景加一条 GB18030 兜底链，确保 100% 能解出可读文本。
"""

from __future__ import annotations

from pathlib import Path

from charset_normalizer import from_bytes

# 兜底尝试顺序：GB18030 是 GBK/GB2312 的超集，几乎能解所有简体中文遗留编码。
_FALLBACK_ENCODINGS = ("utf-8-sig", "gb18030", "big5", "utf-16", "latin-1")


def read_text(path: Path) -> tuple[str, str]:
    """读取文件并返回 (规范化后的 UTF-8 文本, 探测到的源编码名)。

    文本已剥离 BOM、统一换行为 ``\\n``。
    """
    raw = Path(path).read_bytes()
    text, encoding = _decode(raw)
    return _normalize(text), encoding


def _decode(raw: bytes) -> tuple[str, str]:
    """把原始字节解码为 str，返回 (text, encoding_name)。"""
    if not raw:
        return "", "empty"

    # 快速路径：合法 UTF-8 就一定是 UTF-8。charset-normalizer 偶尔会把纯
    # UTF-8 文件误判成 Shift-JIS 等冷门编码，这里先用严格解码拦住。
    try:
        return raw.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        pass

    # 收集候选解码，再按"中文字符占比"挑出真正可读的那个。
    # charset-normalizer 对 GBK 偶尔会判成 latin-1/cp1252 之类——这些编码
    # 几乎不会解码失败，却会产出整篇乱码且不含 '?'，导致损坏检测也抓不到。
    # 强制把中文遗留编码一并纳入候选，用 CJK 占比兜底，避免静默产出乱码。
    candidates: list[tuple[str, str]] = []
    best = from_bytes(raw).best()
    if best is not None:
        candidates.append((str(best), best.encoding))
    for enc in ("gb18030", "big5"):
        try:
            candidates.append((raw.decode(enc), enc))
        except (UnicodeDecodeError, LookupError):
            continue

    if candidates:
        # 平局时 max 取最先出现者，即优先保留 charset-normalizer 的判断。
        text, enc = max(candidates, key=lambda c: _cjk_ratio(c[0]))
        return text, enc

    # 连候选都没有时，按中文优先的顺序硬试。
    for enc in _FALLBACK_ENCODINGS:
        try:
            return raw.decode(enc), enc
        except (UnicodeDecodeError, LookupError):
            continue

    # 最后兜底：永不抛错，无法识别的字节用替换符。
    return raw.decode("utf-8", errors="replace"), "utf-8(replaced)"


def _cjk_ratio(text: str) -> float:
    """返回 CJK 统一表意文字占非空白字符的比例，用于在多个候选解码里挑可读的。"""
    cjk = total = 0
    for c in text:
        if c.isspace():
            continue
        total += 1
        if "一" <= c <= "鿿":
            cjk += 1
    return cjk / total if total else 0.0


def question_mark_ratio(text: str) -> float:
    """返回字面 '?' 与替换符占非空白字符的比例，用于判断文件是否已损坏。

    正常中文文本接近 0；被错误转码毁掉的文件（每个汉字变成 '?' 或替换符
    ``\\ufffd``）会非常高。两类符号都计入，覆盖"另存为 ASCII"和"解码失败兜底"
    两种损坏来源。
    """
    non_ws = [c for c in text if not c.isspace()]
    if not non_ws:
        return 0.0
    damaged = sum(1 for c in non_ws if c == "?" or c == "�")
    return damaged / len(non_ws)


def _normalize(text: str) -> str:
    """剥离 BOM、统一换行符。"""
    if text and text[0] == "﻿":
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")
