from pathlib import Path

src = Path(r"C:\Users\Gilzh\Documents\Offline-HTML-Games-Pack-master\offline\2048.html")
dst = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne\2048_carthing.html")
text = src.read_text(encoding="utf-8")
text = text.replace("@import url(fonts/clear-sans.css);\n", "")
if "<meta charset" in text and "viewport" not in text[:800]:
    text = text.replace(
        '<meta charset="utf-8">',
        '<meta charset="utf-8">\n  <meta name="viewport" content="width=800, height=480, initial-scale=1, maximum-scale=1, user-scalable=no">',
        1,
    )
css = """
  /* Car Thing: Chromium 800x480, Weston rotate-270 onto 480x800 glass. */
  html, body {
    width: 800px !important;
    height: 480px !important;
    max-width: 800px !important;
    max-height: 480px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    background: #faf8ef !important;
  }
  .container {
    width: 800px !important;
    height: 480px !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 6px 0 0 0 !important;
  }
  h1.title { font-size: 36px !important; line-height: 1 !important; }
  .score-container, .best-container {
    padding: 8px 14px !important;
    font-size: 18px !important;
    height: 18px !important;
    line-height: 32px !important;
    margin-top: 0 !important;
  }
  .above-game { margin: 4px 0 !important; width: 500px; }
  .game-intro { margin: 0 !important; font-size: 14px !important; }
  .game-container {
    margin-top: 6px !important;
    transform: scale(0.72);
    transform-origin: top center;
  }
  .game-explanation { display: none !important; }
"""
if "</style>" not in text:
    raise SystemExit("no style tag")
text = text.replace("</style>", css + "\n</style>", 1)
dst.write_text(text, encoding="utf-8", newline="\n")
print("wrote", dst, dst.stat().st_size)
