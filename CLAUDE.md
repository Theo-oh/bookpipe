# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目本质

BookPipe 把粗糙中文 TXT 小说转成带目录的 EPUB。**纯本地、纯 Python、离线、无第三方 App 依赖**——这是刻意的架构红线：不要引入在线 API、Calibre、pandoc 等重型/联网方案（编码与断章都是确定性文本处理，不需要 AI 或外部工具）。

## 运行与测试

依赖装在项目本地 venv，**不要用系统 python**：

```bash
.venv/bin/pytest                 # 跑测试
.venv/bin/ruff check . && .venv/bin/ruff format .   # 改完代码自检 + 格式化
.venv/bin/bookpipe --dry-run <文件>   # 只看编码/书名/作者/章节数，不写文件
.venv/bin/bookpipe               # 转换 iCloud Inbox 全部 txt
```

重装依赖时加 `--no-build-isolation`，否则 pip 会卡在联网重下 setuptools：
`.venv/bin/pip install -e . --no-build-isolation`

## 架构（单本处理流水线，编排在 `cli.py:_process`）

`read_text`(encoding.py) → 损坏预警(question_mark_ratio) → `parse_title_author`(meta.py) → `strip_ad_lines`(clean.py) → `split_chapters`(segment.py) → `build_epub`(epub_builder.py)。新增处理步骤时插进这条链，别绕过 cli.py。

## 改动时务必注意

- **编码探测顺序是刻意的**（encoding.py `_decode`）：先严格 UTF-8 → 再 charset-normalizer → 最后 GB18030 兜底链。严格 UTF-8 优先是为了防止纯 UTF-8 文件被误判成 Shift-JIS，**不要为了"简化"删掉这个快速路径**。
- **iCloud 路径与断章正则集中在 `config.py`**（`ICLOUD_READING`、`CHAPTER_PATTERN`、`CORRUPTION_QUESTION_MARK_RATIO`）。改规则改这里，不要散落到各模块。
- **优雅降级**：封面在 Pillow 或系统中文字体缺失时返回 None 而非报错（cover.py）；损坏文件只跳过当前本、不中断整批（cli.py 失败隔离）。保持这种"绝不因单点失败中断转换"的风格。
- **EPUB 章节 HTML 不要加 `<?xml?>` 声明**（epub_builder.py `_chapter_html`）：ebooklib 写盘时自行补全，带声明会让 body 提取失效、nav 生成报 "Document is empty"。

## 提交约定

提交信息用中文（见 git log）。不要加 `Co-Authored-By` 等 AI 署名 trailer。

## 未来计划

延后的功能（launchd 自动转换等）记在 `ROADMAP.md`，需要时再读。
