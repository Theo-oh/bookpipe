"""launchd 定时扫描代理的装/卸。

把 `bookpipe`（默认扫 Inbox → 转 → 归档）注册成 macOS launchd Agent，
每 `config.SCAN_INTERVAL_SECONDS` 秒冷启动跑一次：无常驻进程、跑完即退，
同名任务 launchd 天然互斥（长转换不会堆叠）。成败日志由 launchd 把进程
stdout/stderr 追加重定向到 `config.LOG_FILE`，无需 logging 框架。
"""

from __future__ import annotations

import subprocess
import sys
from xml.sax.saxutils import escape

from bookpipe import config


def _render_plist() -> str:
    """生成 launchd plist。python 路径用安装时的 sys.executable，避免硬编码 venv。"""
    program_args = [sys.executable, "-m", "bookpipe"]
    args_xml = "\n".join(f"\t\t<string>{escape(a)}</string>" for a in program_args)
    log_path = escape(str(config.LOG_FILE))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
\t<key>Label</key>
\t<string>{escape(config.LAUNCH_AGENT_LABEL)}</string>
\t<key>ProgramArguments</key>
\t<array>
{args_xml}
\t</array>
\t<key>StartInterval</key>
\t<integer>{config.SCAN_INTERVAL_SECONDS}</integer>
\t<key>RunAtLoad</key>
\t<true/>
\t<key>StandardOutPath</key>
\t<string>{log_path}</string>
\t<key>StandardErrorPath</key>
\t<string>{log_path}</string>
</dict>
</plist>
"""


def install_agent() -> int:
    """写 plist 并（重）加载 launchd 代理。"""
    plist = config.LAUNCH_AGENT_PLIST
    plist.parent.mkdir(parents=True, exist_ok=True)
    plist.write_text(_render_plist(), encoding="utf-8")

    # 已加载则先卸再装，保证改了间隔/路径后重载生效；首次卸载失败无所谓。
    subprocess.run(
        ["launchctl", "unload", "-w", str(plist)],
        check=False,
        capture_output=True,
    )
    result = subprocess.run(
        ["launchctl", "load", "-w", str(plist)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"✗ 加载 launchd 代理失败：{result.stderr.strip()}", file=sys.stderr)
        return 1

    interval_min = config.SCAN_INTERVAL_SECONDS // 60
    print(
        f"✓ 已开启自动转换：每 {interval_min} 分钟扫一次 Inbox。\n"
        f"  日志：{config.LOG_FILE}\n"
        f"  立即跑一次：launchctl kickstart -k gui/$UID/{config.LAUNCH_AGENT_LABEL}\n"
        f"  关闭：bookpipe --uninstall-agent"
    )
    return 0


def uninstall_agent() -> int:
    """卸载 launchd 代理并删除 plist。"""
    plist = config.LAUNCH_AGENT_PLIST
    subprocess.run(
        ["launchctl", "unload", "-w", str(plist)],
        check=False,
        capture_output=True,
    )
    if plist.exists():
        plist.unlink()
    print("✓ 已关闭自动转换。")
    return 0
