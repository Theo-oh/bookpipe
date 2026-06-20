"""从文件名解析干净书名与作者。

网文文件名常见形如：
    《示例书名》（1_续10章）作者：佚名
    某某传 作者:某作者
    某某录[完结].txt
解析目标：title=示例书名 / author=佚名。
"""

from __future__ import annotations

import re

DEFAULT_AUTHOR = "未知"

# 作者：xxx / 作者:xxx / 作者 xxx —— 取到下一个括号或结尾
_AUTHOR_RE = re.compile(r"作者[：:\s]*([^\s（）()\[\]【】《》]+)")
# 书名号《...》
_TITLE_BRACKET_RE = re.compile(r"《(.+?)》")
# 各类括号噪音：（1_续10章）【完结】[全本] 等
_NOISE_BRACKET_RE = re.compile(r"[（(【\[\{].*?[）)】\]\}]")


def parse_title_author(stem: str) -> tuple[str, str]:
    """返回 (title, author)。author 缺省为「未知」。"""
    author = DEFAULT_AUTHOR
    m = _AUTHOR_RE.search(stem)
    if m:
        author = m.group(1).strip()

    bracket = _TITLE_BRACKET_RE.search(stem)
    if bracket:
        title = bracket.group(1).strip()
    else:
        # 去掉「作者：xxx」整段与各种括号噪音，剩下的当书名
        t = _AUTHOR_RE.sub("", stem)
        t = _NOISE_BRACKET_RE.sub("", t)
        title = t.strip(" -_—–·.　") or stem

    return title, author
