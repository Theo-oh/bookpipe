from bookpipe.segment import split_chapters


def test_duplicate_title_line_removed():
    text = "第六章 相遇\n第六章 相遇\n那天清晨他到了公司。"
    chs = split_chapters(text)
    assert len(chs) == 1
    assert chs[0].title == "第六章 相遇"
    # 正文里不应再保留重复的标题行
    assert not chs[0].body.startswith("第六章 相遇")
    assert chs[0].body == "那天清晨他到了公司。"


def test_no_dedup_when_body_differs():
    text = "第一章 开始\n正文内容"
    chs = split_chapters(text)
    assert chs[0].body == "正文内容"
