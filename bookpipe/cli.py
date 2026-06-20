"""命令行入口：编排整条 TXT → EPUB 流水线。"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from bookpipe import config
from bookpipe.encoding import read_text
from bookpipe.epub_builder import build_epub
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
    title = txt.stem
    out_path = config.EPUB_DIR / f"{title}.epub"

    if out_path.exists() and not dry_run:
        print(f"• 跳过（已存在）：{out_path.name}")
        return False

    _materialize(txt)
    text, encoding = read_text(txt)
    chapters = split_chapters(text, default_title=title)

    if dry_run:
        print(f"[dry-run] {txt.name} | 编码={encoding} | 章节={len(chapters)}")
        return False

    build_epub(title, chapters, out_path)
    print(f"✓ {txt.name} → {out_path.name}（编码 {encoding}，{len(chapters)} 章）")

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
