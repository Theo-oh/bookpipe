from bookpipe.clean import strip_ad_lines


def test_removes_url_and_keyword_lines():
    text = (
        "更多好书请访问：http://www.xxshuwu.org\n"
        "第一章\n"
        "这是正文。\n"
        "本书由 abc 论坛整理\n"
        "继续正文。"
    )
    out = strip_ad_lines(text)
    assert "http" not in out
    assert "更多好书" not in out
    assert "论坛" not in out
    assert "这是正文。" in out
    assert "继续正文。" in out


def test_removes_decoration_lines():
    text = "*****************\n第一章\n正文\n======="
    out = strip_ad_lines(text)
    assert "*" not in out
    assert "=" not in out
    assert "第一章" in out


def test_keeps_normal_text():
    text = "他说：你好。\n这是一段普通的中文。"
    assert strip_ad_lines(text) == text
