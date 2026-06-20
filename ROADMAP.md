# ROADMAP / 未来计划

记录已讨论但刻意延后的功能。默认仍是**手动命令式**（跑 `bookpipe` 即转，跑完即退、零后台常驻），另已提供可选的 launchd 定时扫描（见下）。

## 1. launchd 自动转换（无感模式）✅ 已落地

`bookpipe --install-agent` 装一个 launchd 定时扫描代理（每 10 分钟扫一次 Inbox 自动转换），`--uninstall-agent` 关掉。实现见 `agent.py`，间隔在 `config.SCAN_INTERVAL_SECONDS`。

- 选了**定时扫描**而非 WatchPaths 实时：对 iCloud 占位符最稳（落地文件可能还没下完），代价是最多延迟几分钟。
- 冷启动跑完即退、无常驻；成败日志追加写到 `Reading/bookpipe.log`。
- 远程/局域网即时触发（SSH、Tailscale+SSH、Apple 快捷指令）暂不内置——iCloud + 定时扫描已覆盖常见需求，需要时再加。

后续可选增强：日志轮转（当前只追加不轮转）。

## 2. 其他可选增强（未承诺）

- 批量书库一次性处理 / 转换报告
- 更多断章规则（可做成 `config.py` 可配的正则列表，或外部规则文件）
- 把"转换并验收一本书"做成 `/convert` 这类一键技能（可用 skill-creator 生成）
