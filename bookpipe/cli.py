"""命令行入口：编排整条 TXT → EPUB 流水线。"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from bookpipe import config
from bookpipe.clean import strip_ad_lines
from bookpipe.cover import make_cover
from bookpipe.encoding import question_mark_ratio, read_text
from bookpipe.epub_builder import build_epub
from bookpipe.meta import parse_title_author
from bookpipe.segment import split_chapters


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bookpipe",
        description="把 01_Inbox_TXT 里的中文 TXT 转成带目录的 EPUB，放到 02_EPUB_Books。",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="要转换的 txt（缺省则处理整个 Inbox）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只探测编码与章节数，不写文件、不归档",
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="转换成功后不把原 txt 移到归档目录",
    )
    args = parser.parse_args(argv)

    if args.files:
        targets = args.files
        from_inbox = False
    else:
        config.INBOX_DIR.mkdir(parents=True, exist_ok=True)
        targets = sorted(config.INBOX_DIR.glob("*.txt"))
        from_inbox = True

    if not targets:
        print("没有要处理的 txt。")
        return 0

    ok, failed = 0, 0
    for txt in targets:
        try:
            converted = _process(
                txt,
                dry_run=args.dry_run,
                archive=from_inbox and not args.no_archive,
            )
            if converted:
                ok += 1
        except Exception as exc:  # 单本失败隔离，不拖垮整批
            failed += 1
            print(f"✗ 失败：{txt.name} —— {exc}", file=sys.stderr)

    print(f"\n完成：成功 {ok}，失败 {failed}。")
    return 1 if failed else 0


def _process(txt: Path, *, dry_run: bool, archive: bool) -> bool:
    """处理单本 txt。返回 True 表示生成了 epub。"""
    _materialize(txt)
    text, encoding = read_text(txt)

    # 优化1：损坏文件预警 —— 字面 '?' 占比过高直接拒绝，原件留在原处。
    qm = question_mark_ratio(text)
    if qm > config.CORRUPTION_QUESTION_MARK_RATIO:
        raise ValueError(
            f"疑似已损坏（{qm:.0%} 是 '?'），多半在转码/另存时被毁；"
            f"请改用原始下载件。已跳过，未归档。"
        )

    # 优化2：从文件名解析干净书名 + 作者。
    title, author = parse_title_author(txt.stem)
    out_path = config.EPUB_DIR / f"{title}.epub"

    if out_path.exists() and not dry_run:
        print(f"• 跳过（已存在）：{out_path.name}")
        return False

    # 优化3：去广告/装饰行。
    text = strip_ad_lines(text)
    chapters = split_chapters(text, default_title=title)

    if dry_run:
        print(
            f"[dry-run] {txt.name} | 编码={encoding} | 书名={title} | "
            f"作者={author} | 章节={len(chapters)}"
        )
        return False

    # 优化4：生成简易封面（环境不支持则为 None，不影响转换）。
    cover = make_cover(title, author)
    build_epub(title, chapters, out_path, author=author, cover=cover)
    cover_tag = "，含封面" if cover else ""
    print(f"✓ {txt.name} → {out_path.name}（编码 {encoding}，{len(chapters)} 章{cover_tag}）")

    if archive:
        config.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(txt), str(config.ARCHIVE_DIR / txt.name))

    return True


def _materialize(path: Path) -> None:
    """若是 iCloud 占位文件，先强制下载到本地。失败不致命。"""
    try:
        subprocess.run(
            ["brctl", "download", str(path)],
            check=False,
            capture_output=True,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


if __name__ == "__main__":
    raise SystemExit(main())
