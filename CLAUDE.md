# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目本质

BookPipe 把粗糙中文 TXT 小说转成带目录的 EPUB。**纯本地、纯 Python、离线、无第三方 App 依赖**——这是刻意的架构红线：不要引入在线 API、Calibre、pandoc 等重型/联网方案（编码与断章都是确定性文本处理，不需要 AI 或外部工具）。

> 这条红线针对**运行时**。开发期用 uv 管依赖（建 venv、装包、`uv.lock` 锁版本）——uv 只是开发工具链，不进运行时、不进 epub 流水线，不违背离线/纯本地红线。构建后端仍是 setuptools，没换。

## 运行与测试

依赖装在项目本地 venv，**不要用系统 python**：

```bash
.venv/bin/pytest                 # 跑测试
.venv/bin/ruff check . && .venv/bin/ruff format .   # 改完代码自检 + 格式化
.venv/bin/bookpipe --dry-run <文件>   # 只看编码/书名/作者/章节数，不写文件
.venv/bin/bookpipe               # 转换 iCloud Inbox 全部 txt
.venv/bin/bookpipe --install-agent     # 装 launchd 定时扫描（每 10 分钟无感转换）
.venv/bin/bookpipe --uninstall-agent   # 卸载
```

依赖用 uv 管理。重建环境 / 重装依赖：

```bash
uv venv                    # 建 .venv（路径不变）
uv pip install -e ".[dev]" # 装运行时 + dev（pytest/ruff）依赖
uv lock                    # 改了依赖后刷新 uv.lock（提交进 git）
```

uv 带全局缓存，装包近乎离线瞬时——不再需要旧的 `pip install --no-build-isolation` workaround。

## 架构（单本处理流水线，编排在 `cli.py:_process`）

`read_text`(encoding.py) → 损坏预警(question_mark_ratio) → `parse_title_author`(meta.py) → `strip_ad_lines`(clean.py) → `split_chapters`(segment.py) → `count_words`(stats.py，字数进文件名+EPUB 元数据+dry-run) → `build_epub`(epub_builder.py)。新增处理步骤时插进这条链，别绕过 cli.py。

**产物按日期分子文件夹**：epub 写到 `EPUB_DIR/<转换日期>/书名（字数）.epub`（cli.py `_process` 用 `date.today()`），避免新书淹没在一堆旧书里。**查重要跨子文件夹**：`_find_existing_epub` 扫 02 根目录 + 各日期子目录，保证「已有同名 epub 自动跳过」跨天仍成立——改输出位置时别退回只查单层。

## 改动时务必注意

- **编码探测顺序是刻意的**（encoding.py `_decode`）：先严格 UTF-8 → 再 charset-normalizer → 最后 GB18030 兜底链。严格 UTF-8 优先是为了防止纯 UTF-8 文件被误判成 Shift-JIS，**不要为了"简化"删掉这个快速路径**。
- **iCloud 路径与断章正则集中在 `config.py`**（`ICLOUD_READING`、`CHAPTER_PATTERN`、`CORRUPTION_QUESTION_MARK_RATIO`）。改规则改这里，不要散落到各模块。
- **优雅降级**：封面在 Pillow 或系统中文字体缺失时返回 None 而非报错（cover.py）；损坏文件只跳过当前本、不中断整批（cli.py 失败隔离）。保持这种"绝不因单点失败中断转换"的风格。
- **EPUB 章节 HTML 不要加 `<?xml?>` 声明**（epub_builder.py `_chapter_html`）：ebooklib 写盘时自行补全，带声明会让 body 提取失效、nav 生成报 "Document is empty"。
- **分段坚持逐行**（epub_builder.py `_to_paragraphs`）：每个非空行 = 一段、空行忽略。曾试过"按空行分块、块内多行合并"的智能模式，会把"一行一段+偶有空行"的常见排版误并成一大段（极端时一章一段），已废弃。**不要再加这种跨行合并。**
- **launchd 代理装卸在 `agent.py`**，CLI 入口是 `--install-agent` / `--uninstall-agent`（cli.py 在文件处理前拦截）。配置（`LOG_FILE`、`LAUNCH_AGENT_LABEL`、`LAUNCH_AGENT_PLIST`、`SCAN_INTERVAL_SECONDS`）集中在 config.py。红线：plist 用 `sys.executable` 安装时解析、**不要硬编码 venv 路径**；是 `StartInterval` 冷启动（无常驻进程、跑完即退），同名任务 launchd 天然互斥、长转换不会堆叠；**日志靠 launchd 把 stdout/stderr 重定向到 `LOG_FILE`，别引 logging 框架**。

## 提交约定

提交信息用中文（见 git log）。不要加 `Co-Authored-By` 等 AI 署名 trailer。

**勤提交**：一组改动累积到一定量（多文件改动、一个完整的功能/修复单元）就提交一次，别攒成一个大杂烩。提交前先过 `pytest` + `ruff check`，绿了再提。

## 文档同步

做完「比较重要的更新」后，顺手把对应文档一起改了、和代码同一个提交，别让文档和代码漂移：

- `README.md`：面向使用者——安装、命令行用法、参数、技术栈、产物形态。
- `CLAUDE.md`：面向 AI 协作者——架构流水线、红线、易踩的坑。
- `ROADMAP.md`：计划落地或新增延后项时增减。

判据：**只有"用户能感知的行为"或"后人接手要知道的约定"变了才同步**——新增/删命令行参数、新增处理步骤、改默认行为、调整架构红线、加依赖、改产物（文件名/元数据）。纯内部重构、修 bug、改测试不必动文档。

## 未来计划

延后的功能（launchd 自动转换等）记在 `ROADMAP.md`，需要时再读。
