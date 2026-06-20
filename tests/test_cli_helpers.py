from bookpipe.cli import _safe_filename


def test_safe_filename_replaces_slash():
    # 书名含斜杠不应把路径带歪
    assert "/" not in _safe_filename("天才/废柴")
    assert "\\" not in _safe_filename("上\\下")


def test_safe_filename_strips_reserved_chars():
    out = _safe_filename('问号?冒号:星号*引号"')
    for ch in '?:*"<>|':
        assert ch not in out


def test_safe_filename_empty_falls_back():
    assert _safe_filename("   ") == "未命名"
    assert _safe_filename("...") == "未命名"


def test_safe_filename_keeps_normal_title():
    assert _safe_filename("某某传") == "某某传"
