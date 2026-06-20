# BookPipe

把网上下载的粗糙中文 `.txt` 小说，自动转成排版精美、带完整章节目录的 `.epub`，
放进 iCloud `Reading/02_EPUB_Books/`，在任意 Apple 设备的「图书」里打开。

纯本地、纯 Python、离线、无第三方 App 依赖。技术栈三件套：
`charset-normalizer`（修编码）+ 正则断章 + `EbookLib`（标准 NCX/nav 目录）。

## 安装（Mac mini）

```bash
cd ~/Workspace/bookpipe
python3 -m venv .venv
.venv/bin/pip install -e .
```

可选：加个 alias 方便用
```bash
echo 'alias bookpipe="$HOME/Workspace/bookpipe/.venv/bin/bookpipe"' >> ~/.zshrc
```

## 使用

```bash
bookpipe                 # 处理 01_Inbox_TXT 里所有 txt，转好放 02，原 txt 归档到 03
bookpipe 某本.txt         # 只转指定文件（输出到 02，不归档）
bookpipe --dry-run       # 只看探测到的编码与章节数，不写文件
bookpipe --no-archive    # 转换后不移动原 txt
```

## 工作流

1. 任意设备把下载的 txt 丢进 iCloud `Reading/01_Inbox_TXT/`。
2. 在 Mac 上跑 `bookpipe`。
3. epub 出现在 `02_EPUB_Books/`，原 txt 移到 `03_Archive_TXT/`，Inbox 清空。
4. iCloud 同步后，在 iPhone/iPad/Mac 的「图书」打开 epub，左上角章节目录可用。

## 设计要点

- **编码**：`charset-normalizer` 主探测 + GB18030 兜底链，剥 BOM、统一换行，杜绝乱码。
- **断章**：正则匹配「第N章/节/回/卷」「序章/楔子/番外」等整行；无标题时整本作单章，永不失败。
- **幂等**：02 已有同名 epub 自动跳过。**失败隔离**：单本出错不影响其余。
- **iCloud 占位符**：读取前先 `brctl download` 强制下载。

## 测试

```bash
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```
