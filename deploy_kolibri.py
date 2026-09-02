"""Copy KolibriOS (v86 + floppy) and the apps catalog onto a connected Car Thing."""
from __future__ import annotations

import subprocess
from pathlib import Path

SSH_BASE = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=8",
]
REMOTE = "root@10.42.1.242"
REMOTE_ROOT = "/opt/nocturne/webapps/player"
ROOT = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne")
LAUNCHER = ROOT / "launcher"
KOLIBRI = LAUNCHER / "projects" / "files" / "kolibri"


def run(cmd: list[str]) -> str:
    print(">", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if out:
        print(out)
    if r.returncode != 0:
        raise SystemExit(f"failed ({r.returncode}): {out or cmd}")
    return out


def main() -> None:
    needed = ["index.html", "libv86.js", "v86.wasm", "seabios.bin", "vgabios.bin", "kolibri.img"]
    for n in needed:
        p = KOLIBRI / n
        if not p.exists():
            raise SystemExit("missing " + str(p))
        print(n, p.stat().st_size)
    run(["ssh"] + SSH_BASE + [REMOTE, "echo SSH_OK"])
    run(
        ["ssh"]
        + SSH_BASE
        + [REMOTE, "df -h /opt/nocturne; mkdir -p /opt/nocturne/webapps/player/projects/files"]
    )
    run(["ssh"] + SSH_BASE + [REMOTE, f"mkdir -p {REMOTE_ROOT}/projects/files/kolibri"])
    for p in KOLIBRI.glob("*"):
        if p.is_file():
            run(["scp"] + SSH_BASE + [str(p), f"{REMOTE}:{REMOTE_ROOT}/projects/files/kolibri/{p.name}"])
    for name in ("catalog.js", "catalog.json"):
        run(["scp"] + SSH_BASE + [str(LAUNCHER / name), f"{REMOTE}:{REMOTE_ROOT}/{name}"])
    run(
        ["ssh"]
        + SSH_BASE
        + [
            REMOTE,
            "ls -l /opt/nocturne/webapps/player/projects/files/kolibri; "
            "systemctl restart chromium-kiosk; sleep 3; systemctl is-active chromium-kiosk",
        ]
    )
    print("DEPLOY_OK")


if __name__ == "__main__":
    main()
