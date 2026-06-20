from pathlib import Path

import pytest

from bookpipe.encoding import read_text

FIXTURES = Path(__file__).parent / "fixtures"

SAMPLE = "第一章 测试\n这是一段中文——含破折号。\n第二章 继续\n再来一段：你好，世界！\n"


@pytest.fixture
def gbk_file(tmp_path):
    p = tmp_path / "sample_gbk.txt"
    p.write_bytes(SAMPLE.encode("gb18030"))
    return p


def test_gbk_decoded_without_mojibake(gbk_file):
    text, enc = read_text(gbk_file)
    assert "测试" in text
    assert "——" in text
    assert "你好，世界！" in text
    assert enc.lower() in {"gb18030", "gbk", "gb2312"}


def test_crlf_and_bom_normalized(tmp_path):
    p = tmp_path / "bom.txt"
    p.write_bytes("﻿第一章\r\n正文\r\n".encode("utf-8"))
    text, _ = read_text(p)
    assert not text.startswith("﻿")
    assert "\r" not in text
    assert text.startswith("第一章")


def test_empty_file(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_bytes(b"")
    text, enc = read_text(p)
    assert text == ""
    assert enc == "empty"
