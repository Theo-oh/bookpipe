"""集中配置：iCloud 路径、子目录、断章正则。"""

from __future__ import annotations

import re
from pathlib import Path

# iCloud Drive 中的 Reading 根目录
ICLOUD_READING = (
    Path.home()
    / "Library"
    / "Mobile Documents"
    / "com~apple~CloudDocs"
    / "Reading"
)

INBOX_DIR = ICLOUD_READING / "01_Inbox_TXT"
EPUB_DIR = ICLOUD_READING / "02_EPUB_Books"
ARCHIVE_DIR = ICLOUD_READING / "03_Archive_TXT"

# 章节标题正则：命中这一整行即视为一个章节切点。
# 覆盖：序章/楔子/引子/前言/后记/尾声/番外，以及「第N章/节/回/卷/集/部」。
# 数字支持中文数字与阿拉伯数字；标题后允许跟少量副标题文字（最多 30 字），避免误吞正文长句。
CHAPTER_PATTERN = re.compile(
    r"^[\s　]*"
    r"(?:"
    r"序章|楔子|引子|前言|序言|后记|後記|尾声|尾聲"
    r"|番外(?:[一二三四五六七八九十百\d]+|[\s　:：、.．\-—－·篇]|$)[^\n]{0,20}"
    r"|第[\s　]*[一二三四五六七八九十百千万兩两零〇\d]+"
    r"[\s　]*[章节節回卷集部篇]"
    r"(?:[\s　]|[:：、.．\-—－·]|$)[^\n]{0,30}"
    r")"
    r"[\s　]*$"
)

# EPUB 语言
BOOK_LANGUAGE = "zh-CN"
