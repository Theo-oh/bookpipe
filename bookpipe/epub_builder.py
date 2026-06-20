"""用 ebooklib 组装带标准 NCX/nav 目录的 EPUB。"""

from __future__ import annotations

import html
import uuid
from pathlib import Path

from ebooklib import epub

from bookpipe.config import BOOK_LANGUAGE
from bookpipe.segment import Chapter

_CSS_PATH = Path(__file__).parent / "assets" / "style.css"


def build_epub(
    title: str,
    chapters: list[Chapter],
    out_path: Path,
    author: str = "未知",
) -> Path:
    """根据章节列表生成 EPUB 并写到 out_path。"""
    book = epub.EpubBook()
    book.set_identifier(f"bookpipe:{uuid.uuid4()}")
    book.set_title(title)
    book.set_language(BOOK_LANGUAGE)
    book.add_author(author)

    css = epub.EpubItem(
        uid="style",
        file_name="style/main.css",
        media_type="text/css",
        content=_CSS_PATH.read_bytes(),
    )
    book.add_item(css)

    spine: list = ["nav"]
    toc: list = []

    for i, ch in enumerate(chapters, start=1):
        item = epub.EpubHtml(
            title=ch.title,
            file_name=f"chap_{i:04d}.xhtml",
            lang=BOOK_LANGUAGE,
        )
        item.content = _chapter_html(ch.title, ch.body)
        item.add_item(css)
        book.add_item(item)
        spine.append(item)
        toc.append(item)

    book.toc = tuple(toc)
    book.add_item(epub.EpubNcx())   # 旧版 Books 用 NCX
    book.add_item(epub.EpubNav())   # EPUB3 nav
    book.spine = spine

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(out_path), book)
    return out_path


def _chapter_html(title: str, body: str) -> str:
    """把纯文本正文转成 XHTML：空行分段，每段一个 <p>。"""
    paragraphs = [
        f"<p>{html.escape(block.strip())}</p>"
        for block in body.split("\n")
        if block.strip()
    ]
    body_html = "\n".join(paragraphs) if paragraphs else "<p></p>"
    # 不要写 <?xml?> 声明：ebooklib 写盘时会自行补全 XHTML 头，且其 body
    # 提取在带 XML 声明时会失效（导致 nav 生成报 Document is empty）。
    return (
        '<html xmlns="http://www.w3.org/1999/xhtml">\n'
        f"<head><title>{html.escape(title)}</title>"
        '<link rel="stylesheet" type="text/css" href="style/main.css"/></head>\n'
        "<body>\n"
        f'<h2 class="chapter-title">{html.escape(title)}</h2>\n'
        f"{body_html}\n"
        "</body>\n</html>"
    )
