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
bookpipe --dry-run       # 只看探测到的编码/书名/作者/章节数/字数，不写文件
bookpipe --no-archive    # 转换后不移动原 txt
bookpipe --install-agent    # 开启后台自动转换（launchd 每 10 分钟扫一次 Inbox）
bookpipe --uninstall-agent  # 关闭后台自动转换
```

## 自动转换（无感后台）

不想每次手动跑？开一个 launchd 定时任务，Mac 常开时每 10 分钟自动扫一次 Inbox：

```bash
bookpipe --install-agent     # 装上即生效，登录时也会先跑一次
bookpipe --uninstall-agent   # 随时关掉
```

- **无常驻进程**：每次冷启动跑完即退，开销可忽略；同名任务由 launchd 天然互斥，长转换不会堆叠。
- **日志**：每次成败追加写到 `Reading/bookpipe.log`，按需查看、不打扰。
- **立即触发一次**（测试用）：`launchctl kickstart -k gui/$UID/com.bookpipe`
- 配合 iCloud，从任意设备把 txt 丢进 `01_Inbox_TXT`，几分钟内自动转好，无需碰 Mac。

## 工作流

1. 任意设备把下载的 txt 丢进 iCloud `Reading/01_Inbox_TXT/`。
2. 在 Mac 上跑 `bookpipe`。
3. epub 出现在 `02_EPUB_Books/<转换日期>/`（按日期分子文件夹，新书不被旧书淹没），原 txt 移到 `03_Archive_TXT/`，Inbox 清空。
4. iCloud 同步后，在 iPhone/iPad/Mac 的「图书」打开 epub，左上角章节目录可用。

## 设计要点

- **编码**：`charset-normalizer` 主探测 + 严格 UTF-8 优先 + GB18030 兜底链，剥 BOM、统一换行，杜绝乱码。
- **断章**：正则匹配「第N章/节/回/卷」「序章/楔子/番外」等整行；无标题时整本作单章，永不失败。
- **按日期归档**：epub 落进 `02_EPUB_Books/<转换日期>/`（如 `2026-06-21/`），刚转好的当天一组、一眼可见，旧书不动。
- **幂等**：跨所有日期子文件夹查重，02 里已有同名 epub 自动跳过。**失败隔离**：单本出错不影响其余。
- **iCloud 占位符**：读取前先 `brctl download` 强制下载。

## 自动优化（无需配置）

1. **损坏文件预警**：若文件里字面 `?` 占比超 25%（多为转码/另存毁掉的文件），直接拒绝并提示，绝不生成乱码 epub。
2. **书名/作者提取**：从文件名解析干净书名与作者，如 `《示例书名》（完结）作者：佚名` → 书名「示例书名」、作者「佚名」。
3. **去广告行**：自动清除含网址、「更多好书请访问」等推广行和纯符号装饰行。
4. **自动封面**：纯色底 + 书名 + 作者，Books 书架上不再是默认灰白图（需 Pillow + 系统中文字体，缺失则自动跳过）。
5. **重复标题合并**：源文件把章节标题写两遍时自动合并，避免空章节。
6. **字数统计**：按去空白字符数统计全书字数，写进产物文件名（如 `书名（12.3万字）.epub`）与 EPUB 元数据，「图书」里可见、文件浏览时一眼知篇幅。

## 测试

```bash
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```
