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

    best = from_bytes(raw).best()
    if best is not None:
        return str(best), best.encoding

    # charset-normalizer 没给出结果时，按中文优先的顺序硬试。
    for enc in _FALLBACK_ENCODINGS:
        try:
            return raw.decode(enc), enc
        except (UnicodeDecodeError, LookupError):
            continue

    # 最后兜底：永不抛错，无法识别的字节用替换符。
    return raw.decode("utf-8", errors="replace"), "utf-8(replaced)"


def _normalize(text: str) -> str:
    """剥离 BOM、统一换行符。"""
    if text and text[0] == "﻿":
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")
