"""中文智能断章：把大通铺文本切成 [(title, body), ...]。"""

from __future__ import annotations

from dataclasses import dataclass

from bookpipe.config import CHAPTER_PATTERN


@dataclass
class Chapter:
    title: str
    body: str  # 原始正文（保留换行，未转 HTML）


def split_chapters(text: str, default_title: str = "正文") -> list[Chapter]:
    """按章节标题行切分文本。

    - 命中 ``CHAPTER_PATTERN`` 的整行作为新章节起点。
    - 标题前的「前言性」散文（无标题的开头文本）归入第一个前置章节。
    - 若全文一个标题都没命中，整本作为单章返回（保证永不失败）。
    """
    lines = text.split("\n")
    chapters: list[Chapter] = []
    pre_lines: list[str] = []  # 第一个标题出现前的内容
    cur_title: str | None = None
    cur_lines: list[str] = []

    def flush() -> None:
        if cur_title is not None:
            chapters.append(Chapter(cur_title, _clean("\n".join(cur_lines))))

    for line in lines:
        if CHAPTER_PATTERN.match(line):
            flush()
            cur_title = line.strip()
            cur_lines = []
        elif cur_title is None:
            pre_lines.append(line)
        else:
            cur_lines.append(line)

    flush()

    # 标题前还有正文 → 作为开篇章节放最前面。
    pre_body = _clean("\n".join(pre_lines))
    if pre_body:
        chapters.insert(0, Chapter(default_title if not chapters else "卷首", pre_body))

    # 完全没切出章节 → 整本单章。
    if not chapters:
        chapters = [Chapter(default_title, _clean(text))]

    return chapters


def _clean(body: str) -> str:
    """去掉首尾多余空行，折叠连续 3+ 空行为 1 个空行。"""
    body = body.strip("\n")
    out: list[str] = []
    blank = 0
    for line in body.split("\n"):
        if line.strip():
            blank = 0
            out.append(line)
        else:
            blank += 1
            if blank == 1:
                out.append("")
    return "\n".join(out).strip("\n")
