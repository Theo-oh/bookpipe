import io
import sys

from bookpipe import config
from bookpipe.cli import _safe_filename, main


class _FakeTTY(io.StringIO):
    def isatty(self):
        return True


class _FakePipe(io.StringIO):
    def isatty(self):
        return False


def test_empty_inbox_silent_when_not_tty(tmp_path, monkeypatch):
    # 定时扫描场景：stdout 非 TTY，空 Inbox 不应往日志写「没有要处理」噪音。
    monkeypatch.setattr(config, "INBOX_DIR", tmp_path)
    out = _FakePipe()
    monkeypatch.setattr(sys, "stdout", out)
    assert main([]) == 0
    assert out.getvalue() == ""


def test_empty_inbox_speaks_when_tty(tmp_path, monkeypatch):
    # 交互式终端仍给反馈。
    monkeypatch.setattr(config, "INBOX_DIR", tmp_path)
    out = _FakeTTY()
    monkeypatch.setattr(sys, "stdout", out)
    assert main([]) == 0
    assert "没有要处理" in out.getvalue()


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
