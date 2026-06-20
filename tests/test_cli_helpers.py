import io
import sys
from datetime import date

from bookpipe import config
from bookpipe.cli import _find_existing_epub, _process, _safe_filename, main


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


def test_find_existing_epub_across_subfolders(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EPUB_DIR", tmp_path)
    assert _find_existing_epub("书.epub") is None  # 目录空
    sub = tmp_path / "2026-06-20"
    sub.mkdir()
    (sub / "书.epub").write_bytes(b"x")
    found = _find_existing_epub("书.epub")
    assert found == sub / "书.epub"
    # 历史平铺在根目录的也能查到
    (tmp_path / "旧书.epub").write_bytes(b"x")
    assert _find_existing_epub("旧书.epub") == tmp_path / "旧书.epub"


def test_process_writes_into_dated_subfolder(tmp_path, monkeypatch):
    epub_dir = tmp_path / "02"
    monkeypatch.setattr(config, "EPUB_DIR", epub_dir)
    txt = tmp_path / "《测试书》作者：佚名.txt"
    txt.write_text("第一章 起\n" + "正文内容。\n" * 20, encoding="utf-8")

    assert _process(txt, dry_run=False, archive=False) is True
    out_dir = epub_dir / date.today().isoformat()
    epubs = list(out_dir.glob("*.epub"))
    assert len(epubs) == 1
    # 再转一次应跨子文件夹查重跳过，不重复生成。
    assert _process(txt, dry_run=False, archive=False) is False
    assert len(list(out_dir.glob("*.epub"))) == 1
