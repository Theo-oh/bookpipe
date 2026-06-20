"""集中配置：iCloud 路径、子目录、断章正则。"""

from __future__ import annotations

import re
from pathlib import Path

# iCloud Drive 中的 Reading 根目录
ICLOUD_READING = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Reading"

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

# launchd 定时扫描代理（`bookpipe --install-agent` 装/卸）。
# 成败日志由 launchd 把进程 stdout/stderr 追加重定向到此文件，不引 logging 框架。
LOG_FILE = ICLOUD_READING / "bookpipe.log"
LAUNCH_AGENT_LABEL = "com.bookpipe"
LAUNCH_AGENT_PLIST = Path.home() / "Library" / "LaunchAgents" / "com.bookpipe.plist"
# 扫描间隔（秒）。10 分钟在「及时」与「省」之间取平衡；改这里即可调。
SCAN_INTERVAL_SECONDS = 600

# 损坏判定：字面 '?' 与替换符占比超过此阈值即视为已损坏文件，拒绝转换。
CORRUPTION_QUESTION_MARK_RATIO = 0.25

# 内容下限：去空白后不足此字符数即视为空文件 / 未下载完成的占位文件，拒绝转换。
MIN_CONTENT_CHARS = 10
