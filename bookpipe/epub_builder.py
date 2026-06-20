"""用 ebooklib 组装带标准 NCX/nav 目录的 EPUB。"""

from __future__ import annotations

import html
import uuid
from pathlib import Path

from ebooklib import epub

from bookpipe.config import BOOK_LANGUAGE
from bookpipe.segment import Chapter
from bookpipe.stats import format_word_count

_CSS_PATH = Path(__file__).parent / "assets" / "style.css"


def build_epub(
    title: str,
    chapters: list[Chapter],
    out_path: Path,
    author: str = "未知",
    cover: bytes | None = None,
    word_count: int | None = None,
) -> Path:
    """根据章节列表生成 EPUB 并写到 out_path。"""
    book = epub.EpubBook()
    book.set_identifier(f"bookpipe:{uuid.uuid4()}")
    book.set_title(title)
    book.set_language(BOOK_LANGUAGE)
    book.add_author(author)
    if word_count is not None:
        book.add_metadata("DC", "description", f"全书约 {format_word_count(word_count)}")

    if cover:
        book.set_cover("cover.png", cover)

    css = epub.EpubItem(
        uid="style",
        file_name="style/main.css",
        media_type="text/css",
        content=_CSS_PATH.read_bytes(),
    )
    book.add_item(css)

    spine: list = ["cover", "nav"] if cover else ["nav"]
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
    book.add_item(epub.EpubNcx())  # 旧版 Books 用 NCX
    book.add_item(epub.EpubNav())  # EPUB3 nav
    book.spine = spine

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(out_path), book)
    return out_path


def _chapter_html(title: str, body: str) -> str:
    """把纯文本正文转成 XHTML：智能识别分段，每段一个 <p>。"""
    paragraphs = [f"<p>{html.escape(p)}</p>" for p in _to_paragraphs(body)]
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


def _to_paragraphs(body: str) -> list[str]:
    """每个非空行就是一段，空行直接忽略。

    中文网文绝大多数是「一行一段」排版，逐行成段最稳。曾尝试过「按空行分块、
    块内多行合并」的智能模式，但它会把"一行一段 + 偶有空行"的常见排版误并成
    一大段（极端时一章一段），故退回这种确定性的逐行分段。
    """
    return [ln.strip() for ln in body.split("\n") if ln.strip()]
