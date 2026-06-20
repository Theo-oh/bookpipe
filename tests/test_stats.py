from bookpipe.segment import Chapter
from bookpipe.stats import count_words, format_word_count


def test_count_words_counts_title_and_body_ignoring_whitespace():
    chapters = [
        Chapter("第一章 开始", "你好 世界。\n这是正文"),
        Chapter("第二章", "结尾"),
    ]
    # 标题: 第一章开始(5) + 第二章(3); 正文: 你好世界。这是正文(9) + 结尾(2)
    assert count_words(chapters) == 5 + 3 + 9 + 2


def test_count_words_empty():
    assert count_words([]) == 0


def test_format_word_count_below_ten_thousand():
    assert format_word_count(0) == "0字"
    assert format_word_count(9999) == "9999字"


def test_format_word_count_wan():
    assert format_word_count(10000) == "1.0万字"
    assert format_word_count(123456) == "12.3万字"
