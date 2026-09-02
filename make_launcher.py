"""Build a Car Thing game launcher plus 10 small offline HTML games."""
from pathlib import Path
import re
import shutil

SRC = Path(r"C:\Users\Gilzh\Documents\Offline-HTML-Games-Pack-master\offline")
OUT = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne\launcher")
GAMES = OUT / "games"
FITTED_2048 = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne\2048_carthing.html")

PAD_INJECT = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne\alpha_pad_inject.html").read_text(encoding="utf-8")

PACK = [
    ("Alpha_1.2.6.html", SRC / "Alpha_1.2.6.html"),
    ("amongus.html", SRC / "amongus.html"),
    ("retrobowl.html", SRC / "retrobowl.html"),
    ("crossyroad.htm", SRC / "crossyroad.htm"),
    ("fruitninja.html", SRC / "fruitninja.html"),
    ("tinyfishing.html", SRC / "tinyfishing.html"),
    ("paperio2.htm", SRC / "paperio2.htm"),
    ("drawclimber.html", SRC / "drawclimber.html"),
    ("helixjump.html", SRC / "helixjump.html"),
    ("stacktris.html", SRC / "stacktris.html"),
    ("noobminer.html", SRC / "noobminer.html"),
    ("wheeliebike.html", SRC / "wheeliebike.html"),
    ("2048.html", FITTED_2048 if FITTED_2048.exists() else SRC / "2048.html"),
    ("googledino.html", SRC / "googledino.html"),
    ("trapthecat.html", SRC / "trapthecat.html"),
    ("sandgame.html", SRC / "sandgame.html"),
    ("wordleunlimited.html", SRC / "wordleunlimited.html"),
    ("doodlejump.html", SRC / "doodlejump.html"),
    ("stack.html", SRC / "stack.html"),
    ("minesweeper.html", SRC / "minesweeper.html"),
    ("spacebarclicker.html", SRC / "spacebarclicker.html"),
    ("oppositeday.html", SRC / "oppositeday.html"),
]


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def inject(data: bytes, name: str) -> bytes:
    text = data.decode("utf-8", errors="surrogateescape")
    if name == "googledino.html":
        text = text.replace(
            '<script src="//www.google.com/jsapi"></script><script>window.parent.maeExportApis_();</script>',
            "",
            1,
        )
    if name == "2048.html":
        text = text.replace("@import url(fonts/clear-sans.css);\n", "")
    if name == "Alpha_1.2.6.html":
        text = re.sub(
            r"<script[^>]*cloudflareinsights\.com[^>]*>.*?</script>",
            "",
            text,
            flags=re.I | re.S,
        )
    if name == "amongus.html":
        text = re.sub(
            r'<script type="module">"use strict";window\.C3_RegisterSW=async function\(\)\{.*?</script>',
            "",
            text,
            flags=re.S,
        )
    snippet = PAD_INJECT
    lower = text.lower()
    idx = lower.rfind("</body>")
    if idx != -1:
        text = text[:idx] + snippet + text[idx:]
    else:
        text = text + snippet
    if "viewport" not in text[:1200].lower():
        text = re.sub(
            r"(<head[^>]*>)",
            r'\1<meta name="viewport" content="width=800, height=480, initial-scale=1, maximum-scale=1, user-scalable=no">',
            text,
            count=1,
            flags=re.I,
        )
    return text.encode("utf-8", errors="surrogateescape")


def main() -> None:
    GAMES.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, src in PACK:
        if not src.exists():
            raise SystemExit(f"missing {src}")
        out = GAMES / name
        raw = read_bytes(src)
        data = inject(raw, name)
        out.write_bytes(data)
        total += out.stat().st_size
        print(f"wrote {out.name:24s} {out.stat().st_size:9d}")
    idx = OUT / "index.html"
    print(f"launcher {idx} {idx.stat().st_size}")
    print(f"games total {total} bytes")


if __name__ == "__main__":
    main()
