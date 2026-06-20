"""清除网文 TXT 里的广告/装饰垃圾行。"""

from __future__ import annotations

import re

# 含网址的行
_URL_RE = re.compile(r"https?://|www\.|[\w-]+\.(?:com|org|net|cc|xyz|info|top)\b", re.I)
# 常见推广关键词
_AD_KEYWORDS_RE = re.compile(
    r"更多好书|更多精彩|请访问|本书来自|本书由|本书下载|最新章节|手机阅读|免费阅读"
    r"|电子书下载|txt[下电]载|首发|转载请|仅供.{0,6}(?:学习|交流|参考)"
    r"|书城|书库|书屋|书虫|阅读网|小说网|论坛"
)
# 纯装饰行（整行都是符号/星号/等号等）
_DECORATION_RE = re.compile(r"^[\s*=_\-—–~·#＃★☆※＊·•|]+$")


def strip_ad_lines(text: str) -> str:
    """逐行过滤广告与装饰行，保留正文。"""
    kept: list[str] = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            kept.append(line)
            continue
        if _URL_RE.search(s) or _AD_KEYWORDS_RE.search(s) or _DECORATION_RE.match(s):
            continue
        kept.append(line)
    return "\n".join(kept)
