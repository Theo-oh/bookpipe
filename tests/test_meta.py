from bookpipe.meta import parse_title_author


def test_bracket_title_with_author():
    t, a = parse_title_author("《示例书名》（1_续10章）作者：佚名")
    assert t == "示例书名"
    assert a == "佚名"


def test_plain_title_with_author_colon():
    t, a = parse_title_author("某某传 作者:某作者")
    assert t == "某某传"
    assert a == "某作者"


def test_noise_brackets_stripped():
    t, a = parse_title_author("某某录[完结]")
    assert t == "某某录"
    assert a == "未知"


def test_bare_name():
    t, a = parse_title_author("书名")
    assert t == "书名"
    assert a == "未知"
