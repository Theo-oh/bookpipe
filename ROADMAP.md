# ROADMAP / 未来计划

记录已讨论但刻意延后的功能。当前版本是**手动命令式**（跑 `bookpipe` 即转，跑完即退、零后台常驻）。

## 1. launchd 自动转换（无感模式）

把"丢进 `01_Inbox_TXT` 就自动转"做成后台服务。两种触发机制：

| 方案 | 说明 | 取舍 |
|---|---|---|
| **定时扫描**（倾向） | launchd 每 N 分钟（如 5 分钟）跑一次 `bookpipe` | 对 iCloud 占位符友好、最稳；代价是最多延迟几分钟 |
| WatchPaths 实时 | 文件落地立即触发 | 更即时，但 iCloud 同步下来的文件可能还是占位符、触发时没下载完，需额外处理 |

- 实现：一个 `~/Library/LaunchAgents/com.bookpipe.plist`（约 10 行）+ `launchctl load`。
- **失败通知**（已定）：成败写日志到 `Reading/bookpipe.log`，按需查看，不打扰。
- 决策背景：当前选手动是为先把核心跑通；随时可升级，也随时可 `launchctl unload` 关掉。

## 2. 其他可选增强（未承诺）

- 批量书库一次性处理 / 转换报告
- 更多断章规则（可做成 `config.py` 可配的正则列表，或外部规则文件）
- 把"转换并验收一本书"做成 `/convert` 这类一键技能（可用 skill-creator 生成）
