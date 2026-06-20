from ebooklib import epub

from bookpipe.epub_builder import _to_paragraphs, build_epub
from bookpipe.segment import Chapter


def test_build_epub_roundtrip(tmp_path):
    chapters = [
        Chapter("第一章 开始", "正文甲第一段\n正文甲第二段"),
        Chapter("第二章 继续", "正文乙"),
    ]
    out = tmp_path / "测试书.epub"
    build_epub("测试书", chapters, out, author="某作者")

    assert out.exists()

    book = epub.read_epub(str(out))
    assert book.get_metadata("DC", "title")[0][0] == "测试书"
    assert book.get_metadata("DC", "creator")[0][0] == "某作者"

    docs = [it for it in book.get_items() if isinstance(it, epub.EpubHtml)]
    chapter_docs = [d for d in docs if d.file_name.startswith("chap_")]
    assert len(chapter_docs) == 2
    first = chapter_docs[0].get_content().decode("utf-8")
    assert "第一章 开始" in first
    assert "正文甲第一段" in first


def test_build_epub_with_cover(tmp_path):
    # 1x1 PNG
    png = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
        "890000000a49444154789c6360000002000154a24f5f0000000049454e44ae426082"
    )
    out = tmp_path / "封面书.epub"
    build_epub("封面书", [Chapter("正文", "内容")], out, cover=png)
    book = epub.read_epub(str(out))
    assert any(it.file_name == "cover.png" for it in book.get_items())


def test_paragraphs_one_line_each():
    # 一行一段、无空行：每行就是一段，不应合并
    body = "第一段。\n第二段。\n第三段。"
    assert _to_paragraphs(body) == ["第一段。", "第二段。", "第三段。"]


def test_paragraphs_blank_separated_merges_wrapped_lines():
    # 段间空行、段内硬换行：块内多行合并成一段
    body = "第一段上半\n第一段下半\n\n第二段独立"
    assert _to_paragraphs(body) == ["第一段上半第一段下半", "第二段独立"]


def test_paragraphs_blank_separated_single_lines():
    # 段间空行、段内单行：仍是逐行成段
    body = "第一段\n\n第二段\n\n第三段"
    assert _to_paragraphs(body) == ["第一段", "第二段", "第三段"]


def test_paragraphs_empty():
    assert _to_paragraphs("\n\n  \n") == []
