"""统计工具：中文字数计数与展示格式化。"""

from __future__ import annotations

import re
from collections.abc import Iterable

from bookpipe.segment import Chapter

# 字数口径：去掉所有空白后的字符数（含标点），贴合网文站的统计习惯。
# 不用空格分词——中文没有词间空格，那样会把整本算成寥寥几"词"。
_WHITESPACE_RE = re.compile(r"\s")


def count_words(chapters: Iterable[Chapter]) -> int:
    """统计全书字数：所有章节标题与正文里的非空白字符数之和。"""
    total = 0
    for ch in chapters:
        total += len(_WHITESPACE_RE.sub("", ch.title))
        total += len(_WHITESPACE_RE.sub("", ch.body))
    return total


def format_word_count(n: int) -> str:
    """格式化成中文习惯的展示串：≥1万显示「X.X万字」，否则「N字」。"""
    if n >= 10000:
        return f"{n / 10000:.1f}万字"
    return f"{n}字"
