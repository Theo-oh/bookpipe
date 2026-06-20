from bookpipe.segment import split_chapters


def test_basic_chapters():
    text = "第一章 开始\n正文甲\n第二章 继续\n正文乙"
    chs = split_chapters(text)
    assert [c.title for c in chs] == ["第一章 开始", "第二章 继续"]
    assert chs[0].body == "正文甲"
    assert chs[1].body == "正文乙"


def test_varied_titles():
    text = "楔子\n引子内容\n第 10 回 大战\n打斗\n番外一 后日谈\n番外内容"
    titles = [c.title for c in split_chapters(text)]
    assert titles == ["楔子", "第 10 回 大战", "番外一 后日谈"]


def test_preface_before_first_title():
    text = "这是没有标题的开篇。\n第一章 正式开始\n内容"
    chs = split_chapters(text)
    assert chs[0].title == "卷首"
    assert "开篇" in chs[0].body
    assert chs[1].title == "第一章 正式开始"


def test_no_titles_single_chapter():
    text = "这本书\n完全没有章节标题\n就是一坨文字"
    chs = split_chapters(text, default_title="我的书")
    assert len(chs) == 1
    assert chs[0].title == "我的书"


def test_does_not_eat_long_body_line():
    # 「第一」开头但其实是正文长句，不应被当作章节标题
    text = "第一章 真标题\n第一次见面他就说了一大段非常非常长的废话还在继续说个不停没完没了"
    chs = split_chapters(text)
    assert len(chs) == 1
    assert chs[0].title == "第一章 真标题"
