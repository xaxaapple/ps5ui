"""Проверка без окна: сервер, защита токеном, RPC, парсинг Steam. Запуск: python windows/tests/smoke_test.py"""
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.environ.setdefault("APPDATA", tempfile.mkdtemp())

from pc5win import sources                      # noqa: E402
from pc5win.backend import Backend              # noqa: E402
from pc5win.server import EventBus, Server     # noqa: E402


def main() -> int:
    root = tempfile.mkdtemp()
    os.makedirs(root + "/steamapps/common/Game A")
    with open(root + "/steamapps/libraryfolders.vdf", "w") as f:
        f.write('"libraryfolders"{"0"{"path" "%s"}}' % root.replace("\\", "\\\\"))
    with open(root + "/steamapps/appmanifest_123.acf", "w") as f:
        f.write('"AppState"{"appid" "123" "name" "Game A" "StateFlags" "4" "installdir" "Game A" "LastPlayed" "1700000000"}')
    sources.steam_root = lambda: root
    found = sources.scan_steam()
    assert [g.id for g in found] == ["steam:123"], found

    bus = EventBus()
    backend = Backend(bus.emit, lambda: None, lambda: None)
    server = Server(backend.call, bus, lambda: server.query_string("en"))
    server.start()
    base = "http://127.0.0.1:%d" % server.port

    def rpc(method, params=None, token=True):
        headers = {"X-PC5-Token": server.token} if token else {}
        req = urllib.request.Request(base + "/rpc", json.dumps({"method": method, "params": params or {}}).encode(), headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"http": e.code}

    assert rpc("sys.state", token=False) == {"http": 403}
    assert rpc("sys.state")["ok"]
    got = rpc("lib.list", {"kind": "game", "filter": "recent"})["result"]["entries"]
    assert [e["id"] for e in got] == ["steam:123"] and got[0]["art"]["cover"].startswith("https://"), got
    assert rpc("lib.get", {"id": "steam:123"})["result"]["actions"][0]["id"] == "launch"
    assert rpc("settings.set", {"id": "home.theme", "value": "ocean"})["ok"]
    assert rpc("settings.set", {"id": "home.theme", "value": "bogus"})["error"] == "BadValue"
    assert rpc("nope")["error"] == "UnknownMethod"
    for path, want in (("/", 403), ("/js/main.js", 200), ("/../../etc/passwd", 404)):
        try:
            code = urllib.request.urlopen(base + path, timeout=10).status
        except urllib.error.HTTPError as e:
            code = e.code
        assert code == want, (path, code)
    backend.stop()
    server.stop()
    print("smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
