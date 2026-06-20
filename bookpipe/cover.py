"""生成简易封面：纯色底 + 书名 + 作者。

依赖 Pillow 与系统 CJK 字体；任一缺失则优雅返回 None（不影响转换）。
"""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

# macOS 自带的中文字体候选（按优先级）
_FONT_CANDIDATES = (
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Songti.ttc",
)

_W, _H = 600, 800


def make_cover(title: str, author: str) -> bytes | None:
    """返回 PNG 字节；环境不支持则返回 None。"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    font_path = next((p for p in _FONT_CANDIDATES if Path(p).exists()), None)
    if not font_path:
        return None

    # 由书名派生一个稳定的深色背景，保证可读性
    h = hashlib.md5(title.encode("utf-8")).digest()
    bg = (40 + h[0] % 110, 40 + h[1] % 110, 40 + h[2] % 110)

    img = Image.new("RGB", (_W, _H), bg)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(font_path, 66, index=0)
        author_font = ImageFont.truetype(font_path, 32, index=0)
    except OSError:
        return None

    # 书名按每行 6 字折行
    lines = _wrap(title, 6)
    line_h = 84
    total_h = line_h * len(lines)
    y = (_H - total_h) // 2 - 60
    for line in lines:
        w = draw.textlength(line, font=title_font)
        draw.text(((_W - w) / 2, y), line, fill=(255, 255, 255), font=title_font)
        y += line_h

    # 作者居下
    if author:
        label = f"作者：{author}"
        w = draw.textlength(label, font=author_font)
        draw.text(((_W - w) / 2, _H - 120), label, fill=(225, 225, 225), font=author_font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _wrap(text: str, per_line: int) -> list[str]:
    text = text.strip()
    return [text[i : i + per_line] for i in range(0, len(text), per_line)] or [text]
