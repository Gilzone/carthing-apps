"""Copy the Reader and bundled book onto a connected Car Thing."""
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
LAUNCHER = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne\launcher")


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
    reader = LAUNCHER / "tools" / "reader.html"
    book = LAUNCHER / "tools" / "books" / "contented.js"
    if not reader.exists() or not book.exists():
        raise SystemExit("missing reader or book file")
    run(["ssh"] + SSH_BASE + [REMOTE, "echo SSH_OK"])
    run(["ssh"] + SSH_BASE + [REMOTE, f"mkdir -p {REMOTE_ROOT}/tools/books"])
    run(["scp"] + SSH_BASE + [str(reader), f"{REMOTE}:{REMOTE_ROOT}/tools/reader.html"])
    run(["scp"] + SSH_BASE + [str(book), f"{REMOTE}:{REMOTE_ROOT}/tools/books/contented.js"])
    run(
        ["ssh"]
        + SSH_BASE
        + [
            REMOTE,
            f"ls -l {REMOTE_ROOT}/tools/reader.html {REMOTE_ROOT}/tools/books/contented.js; "
            "systemctl restart chromium-kiosk; sleep 3; systemctl is-active chromium-kiosk",
        ]
    )
    print("DEPLOY_OK")


if __name__ == "__main__":
    main()
