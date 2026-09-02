"""Add a self-contained HTML file to the Car Thing Apps tab.

Examples:
  python add_project.py C:\\path\\to\\app.html
  python add_project.py C:\\path\\to\\app.html --name "Weather" --hint "Local page"
  python add_project.py C:\\path\\to\\app.html --deploy
  python add_project.py --list
  python add_project.py --remove weather.html
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne")
LAUNCHER = ROOT / "launcher"
PROJ = LAUNCHER / "projects"
FILES = PROJ / "files"
MANIFEST = PROJ / "projects.json"
CATALOG = PROJ / "catalog.js"
HOME_INJECT = PROJ / "home_inject.html"
PAD_INJECT = ROOT / "alpha_pad_inject.html"
COLORS = ["#34d399", "#60a5fa", "#fbbf24", "#f43f5e", "#c084fc", "#fb923c", "#22d3ee", "#a3e635"]
CATALOG_JSON = LAUNCHER / "catalog.json"
CATALOG_JS = LAUNCHER / "catalog.js"


def load_catalog() -> dict:
    if CATALOG_JSON.exists():
        return json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    return {"tabs": [], "items": []}


def save_catalog(cat: dict) -> None:
    CATALOG_JSON.write_text(json.dumps(cat, indent=2), encoding="utf-8")
    CATALOG_JS.write_text("window.CT_CATALOG = " + json.dumps(cat) + ";\n", encoding="utf-8")
    apps = [it for it in cat.get("items", []) if it.get("tab") == "apps"]
    save_manifest(
        [
            {k: it[k] for k in ("file", "name", "hint", "mark", "color") if k in it}
            for it in apps
        ]
    )


def tab_dir(tab_id: str) -> Path:
    if tab_id == "games":
        return LAUNCHER / "games"
    if tab_id == "tools":
        return LAUNCHER / "tools"
    if tab_id == "apps":
        FILES.mkdir(parents=True, exist_ok=True)
        return FILES
    d = LAUNCHER / "tabs" / tab_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def tab_rel(tab_id: str, filename: str) -> str:
    if tab_id == "games":
        return f"games/{filename}"
    if tab_id == "tools":
        return f"tools/{filename}"
    if tab_id == "apps":
        return f"projects/files/{filename}"
    return f"tabs/{tab_id}/{filename}"


def parse_launcher_catalog() -> dict[str, list[dict]]:
    cat = load_catalog()
    out: dict[str, list[dict]] = {}
    for tab in cat.get("tabs", []):
        tid = tab["id"]
        out[tid] = []
        for it in cat.get("items", []):
            if it.get("tab") == tid:
                row = dict(it)
                row["kind"] = tid
                row["deletable"] = True
                out[tid].append(row)
    return out


def device_file_names() -> dict[str, set[str]] | None:
    """What is actually on the Car Thing, or None if USB is down."""
    if not ssh_ok():
        return None
    script = (
        "echo GAMES; ls /opt/nocturne/webapps/player/games 2>/dev/null; "
        "echo TOOLS; ls /opt/nocturne/webapps/player/tools 2>/dev/null; "
        "echo APPS; find /opt/nocturne/webapps/player/projects/files -type f 2>/dev/null | sed 's|.*/||'; "
        "echo TABS; find /opt/nocturne/webapps/player/tabs -type f 2>/dev/null | sed 's|.*/||'"
    )
    r = subprocess.run(
        ["ssh"] + SSH_BASE + [REMOTE, script],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if r.returncode != 0:
        return None
    out = {"game": set(), "tool": set(), "app": set()}
    bucket = None
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if line == "GAMES":
            bucket = "game"
        elif line == "TOOLS":
            bucket = "tool"
        elif line == "APPS":
            bucket = "app"
        elif line == "TABS":
            bucket = "app"
        elif bucket and line and not line.startswith("ls:"):
            out[bucket].add(line)
    return out


def load_manifest() -> list:
    if not MANIFEST.exists():
        return []
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(items: list) -> None:
    MANIFEST.write_text(json.dumps(items, indent=2), encoding="utf-8")
    lines = ["window.DISK_PROJECTS = " + json.dumps(items, indent=2) + ";\n"]
    CATALOG.write_text(lines[0], encoding="utf-8")
    print("wrote", CATALOG)


def slug_name(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(name).name).strip("-")
    return s or "app.html"


def inject_home(text: str, pad: bool, tab: str = "apps") -> str:
    snippet = PAD_INJECT.read_text(encoding="utf-8") if pad else HOME_INJECT.read_text(encoding="utf-8")
    home = f"file:///opt/nocturne/webapps/player/index.html#{tab}"
    snippet = re.sub(
        r'file:///opt/nocturne/webapps/player/index.html(?:#[^"\']*)?',
        home,
        snippet,
    )
    # Kill CDN links that fail offline (do not break JS strings: keep quoting).
    text = re.sub(
        r"https:\\?/\\?/cdn\.jsdelivr\.net[^\"'\\s>]*",
        "#",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"https://cdn\.jsdelivr\.net[^\"'\\s>]*",
        "#",
        text,
        flags=re.I,
    )
    start = text.lstrip()[:64].lower()
    real_html = start.startswith("<!doctype") or start.startswith("<html")
    lower = text.lower()
    idx = lower.rfind("</body>") if real_html else -1
    if idx != -1:
        text = text[:idx] + snippet + text[idx:]
    else:
        text = text + snippet
    start = text.lstrip()[:32].lower()
    if start.startswith("<!doctype") or start.startswith("<html"):
        if "viewport" not in text[:1200].lower():
            text = re.sub(
                r"(<head[^>]*>)",
                r'\1<meta name="viewport" content="width=800, height=480, initial-scale=1, maximum-scale=1, user-scalable=no">',
                text,
                count=1,
                flags=re.I,
            )
    return text


def add(src: Path, name: str | None, hint: str | None, mark: str | None, color: str | None, pad: bool, tab: str = "apps") -> dict:
    cat = load_catalog()
    tab_ids = [t["id"] for t in cat.get("tabs", [])]
    if tab not in tab_ids:
        raise ValueError("unknown tab: " + tab)
    dest_dir = tab_dir(tab)
    dest_dir.mkdir(parents=True, exist_ok=True)
    raw = src.read_text(encoding="utf-8", errors="surrogateescape")
    html = inject_home(raw, pad, tab)
    dest_name = slug_name(src.name)
    dest = dest_dir / dest_name
    n = 2
    while dest.exists():
        dest = dest_dir / f"{dest.stem}-{n}{dest.suffix}"
        n += 1
    dest.write_text(html, encoding="utf-8", errors="surrogateescape", newline="\n")
    title = name or src.stem.replace("_", " ").replace("-", " ")
    item = {
        "tab": tab,
        "file": tab_rel(tab, dest.name),
        "name": title[:28],
        "hint": (hint or "Custom HTML")[:40],
        "mark": (mark or title[:2].upper() or "APP")[:4],
        "color": color or COLORS[len(cat.get("items", [])) % len(COLORS)],
    }
    cat["items"] = [x for x in cat.get("items", []) if x.get("file") != item["file"]]
    cat["items"].append(item)
    save_catalog(cat)
    print("added", dest, dest.stat().st_size, "bytes")
    return item


def remove(name: str) -> dict | None:
    cat = load_catalog()
    removed = None
    keep = []
    for it in cat.get("items", []):
        hit = (
            it.get("file", "").endswith(name)
            or it.get("name", "").lower() == name.lower()
            or Path(it.get("file", "")).name == name
        )
        if hit and removed is None:
            removed = it
        else:
            keep.append(it)
    if not removed:
        raise ValueError("not found: " + name)
    path = LAUNCHER / removed["file"]
    if path.exists():
        path.unlink()
    cat["items"] = keep
    save_catalog(cat)
    print("removed", removed["file"])
    return removed


def add_tab(name: str) -> dict:
    cat = load_catalog()
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-") or "tab"
    base = slug
    n = 2
    ids = {t["id"] for t in cat.get("tabs", [])}
    while slug in ids:
        slug = f"{base}-{n}"
        n += 1
    tab = {
        "id": slug,
        "name": name.strip().upper()[:12] or "TAB",
        "label": name.strip()[:18] or "Tab",
        "hint": "Custom tab",
    }
    cat.setdefault("tabs", []).append(tab)
    tab_dir(slug)
    save_catalog(cat)
    return tab


def remove_tab(tab_id: str) -> None:
    if tab_id in {"games", "tools"}:
        raise ValueError("Cannot delete the Games or Tools tab")
    cat = load_catalog()
    leftover = [it for it in cat.get("items", []) if it.get("tab") == tab_id]
    for it in leftover:
        p = LAUNCHER / it["file"]
        if p.exists():
            p.unlink()
    cat["items"] = [it for it in cat.get("items", []) if it.get("tab") != tab_id]
    cat["tabs"] = [t for t in cat.get("tabs", []) if t["id"] != tab_id]
    save_catalog(cat)


def move_item(file_or_name: str, tab: str) -> dict:
    cat = load_catalog()
    ids = {t["id"] for t in cat.get("tabs", [])}
    if tab not in ids:
        raise ValueError("unknown tab: " + tab)
    found = None
    for it in cat.get("items", []):
        if it.get("file") == file_or_name or it.get("name") == file_or_name or Path(it.get("file", "")).name == file_or_name:
            found = it
            break
    if not found:
        raise ValueError("not found: " + file_or_name)
    found["tab"] = tab
    save_catalog(cat)
    return found


SSH_BASE = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=8",
]
IP = "10.42.1.242"
REMOTE = "root@10.42.1.242"
REMOTE_ROOT = "/opt/nocturne/webapps/player"


def ssh_ok() -> bool:
    try:
        r = subprocess.run(
            ["ssh"] + SSH_BASE + [REMOTE, "echo SSH_OK"],
            capture_output=True,
            text=True,
            timeout=12,
        )
        return "SSH_OK" in (r.stdout or "")
    except Exception:
        return False


def _run(cmd: list[str], log=print) -> None:
    log(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout:
        log(r.stdout.strip())
    if r.returncode != 0:
        err = (r.stderr or "").strip() or f"exit {r.returncode}"
        raise RuntimeError(err)


def deploy_connected(log=print, extra_files: list[Path] | None = None, delete_remote: list[str] | None = None) -> None:
    """Copy launcher catalog and any new HTML to a Car Thing that is already on USB."""
    _run(
        ["ssh"]
        + SSH_BASE
        + [REMOTE, f"mkdir -p {REMOTE_ROOT}/projects/files {REMOTE_ROOT}/tabs {REMOTE_ROOT}/games {REMOTE_ROOT}/tools"],
        log,
    )
    for rel in delete_remote or []:
        _run(["ssh"] + SSH_BASE + [REMOTE, f"rm -f {REMOTE_ROOT}/{rel}"], log)
    _run(["scp"] + SSH_BASE + [str(LAUNCHER / "index.html"), f"{REMOTE}:{REMOTE_ROOT}/index.html"], log)
    if CATALOG_JS.exists():
        _run(["scp"] + SSH_BASE + [str(CATALOG_JS), f"{REMOTE}:{REMOTE_ROOT}/catalog.js"], log)
    if CATALOG_JSON.exists():
        _run(["scp"] + SSH_BASE + [str(CATALOG_JSON), f"{REMOTE}:{REMOTE_ROOT}/catalog.json"], log)
    for p in sorted(PROJ.glob("*")):
        if p.is_file():
            _run(["scp"] + SSH_BASE + [str(p), f"{REMOTE}:{REMOTE_ROOT}/projects/{p.name}"], log)
    to_copy = list(extra_files or [])
    cat = load_catalog()
    for it in cat.get("items", []):
        local = LAUNCHER / it["file"]
        if local.exists() and it.get("tab") not in {"games", "tools"}:
            to_copy.append(local)
    seen = set()
    for local in to_copy:
        local = Path(local)
        if not local.exists() or local in seen:
            continue
        seen.add(local)
        try:
            rel = local.relative_to(LAUNCHER).as_posix()
        except ValueError:
            continue
        remote_dir = f"{REMOTE_ROOT}/{str(Path(rel).parent).replace(chr(92), '/')}"
        _run(["ssh"] + SSH_BASE + [REMOTE, f"mkdir -p {remote_dir}"], log)
        _run(["scp"] + SSH_BASE + [str(local), f"{REMOTE}:{REMOTE_ROOT}/{rel}"], log)
    _run(
        ["ssh"] + SSH_BASE + [REMOTE, "systemctl restart chromium-kiosk; sleep 3; systemctl is-active chromium-kiosk"],
        log,
    )
    log("DEPLOY_OK")


def deploy() -> None:
    try:
        deploy_connected()
    except Exception:
        ps = ROOT / "deploy_apps.ps1"
        subprocess.check_call(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)])


def main() -> None:
    p = argparse.ArgumentParser(description="Add HTML apps to the Car Thing Apps tab")
    p.add_argument("html", nargs="?", help="Path to a .html / .htm file")
    p.add_argument("--name", help="Display name")
    p.add_argument("--hint", help="Short subtitle")
    p.add_argument("--mark", help="2-4 letter badge")
    p.add_argument("--color", help="Hex color like #34d399")
    p.add_argument("--tab", default="apps", help="Tab id: games, tools, apps, or a custom tab")
    p.add_argument("--pad", action="store_true", help="Also inject the WASD touch pad")
    p.add_argument("--deploy", action="store_true", help="Copy Apps tab to the Car Thing")
    p.add_argument("--list", action="store_true")
    p.add_argument("--remove", metavar="FILE", help="Remove by filename or name")
    args = p.parse_args()
    if args.list:
        for it in load_manifest():
            print(f"{it['name']:24s} {it['file']}")
        return
    if args.remove:
        remove(args.remove)
        if args.deploy:
            deploy()
        return
    if args.html:
        add(Path(args.html), args.name, args.hint, args.mark, args.color, args.pad, args.tab)
        if args.deploy:
            deploy()
        return
    if args.deploy:
        deploy()
        return
    p.print_help()


if __name__ == "__main__":
    main()
