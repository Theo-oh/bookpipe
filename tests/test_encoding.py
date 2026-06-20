from pathlib import Path

import pytest

from bookpipe.encoding import question_mark_ratio, read_text

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


def test_long_gbk_not_mojibake(tmp_path):
    # 一整篇 GBK 中文：即便 charset-normalizer 误判，CJK 占比兜底也应解出可读文本。
    long_cn = ("这是一段很长的中文小说正文，用来确保编码探测不会把它误判成西文。" * 80) + "\n"
    p = tmp_path / "long_gbk.txt"
    p.write_bytes(long_cn.encode("gb18030"))
    text, _ = read_text(p)
    assert "中文小说正文" in text
    # 乱码会带来大量替换符 / 西文符号，正确解码后应几乎为零
    assert question_mark_ratio(text) < 0.01


def test_question_mark_ratio_counts_replacement_char():
    assert question_mark_ratio("���正常") == pytest.approx(3 / 5)
    assert question_mark_ratio("正常中文文本") == 0.0
