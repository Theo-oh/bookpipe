import sys

from bookpipe import agent, config


def test_render_plist_has_essentials():
    xml = agent._render_plist()
    assert config.LAUNCH_AGENT_LABEL in xml
    assert f"<integer>{config.SCAN_INTERVAL_SECONDS}</integer>" in xml
    assert "<string>-m</string>" in xml
    assert "<string>bookpipe</string>" in xml
    assert sys.executable in xml
    assert str(config.LOG_FILE) in xml


def test_render_plist_is_well_formed_xml():
    # plist 损坏会让 launchd 直接拒绝加载，确保能被解析。
    from xml.dom.minidom import parseString

    parseString(agent._render_plist())


def test_install_agent_writes_plist_and_loads(tmp_path, monkeypatch):
    plist = tmp_path / "LaunchAgents" / "com.bookpipe.plist"
    monkeypatch.setattr(config, "LAUNCH_AGENT_PLIST", plist)

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(agent.subprocess, "run", fake_run)

    rc = agent.install_agent()
    assert rc == 0
    assert plist.exists()
    # 先 unload 再 load，保证改了配置后能重载生效。
    assert calls[0][:2] == ["launchctl", "unload"]
    assert calls[1][:2] == ["launchctl", "load"]


def test_install_agent_reports_load_failure(tmp_path, monkeypatch):
    plist = tmp_path / "LaunchAgents" / "com.bookpipe.plist"
    monkeypatch.setattr(config, "LAUNCH_AGENT_PLIST", plist)

    def fake_run(cmd, **kwargs):
        class R:
            returncode = 0 if cmd[1] == "unload" else 1
            stderr = "boom"

        return R()

    monkeypatch.setattr(agent.subprocess, "run", fake_run)
    assert agent.install_agent() == 1


def test_uninstall_agent_unloads_and_removes(tmp_path, monkeypatch):
    plist = tmp_path / "LaunchAgents" / "com.bookpipe.plist"
    plist.parent.mkdir(parents=True)
    plist.write_text("x", encoding="utf-8")
    monkeypatch.setattr(config, "LAUNCH_AGENT_PLIST", plist)

    calls = []
    monkeypatch.setattr(agent.subprocess, "run", lambda cmd, **kw: calls.append(cmd) or None)

    rc = agent.uninstall_agent()
    assert rc == 0
    assert not plist.exists()
    assert calls[0][:2] == ["launchctl", "unload"]
