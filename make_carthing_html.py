from pathlib import Path

src = Path(r"C:\Users\Gilzh\Downloads\mp3_player_sim.html")
dst = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne\mp3_player_carthing.html")
text = src.read_text(encoding="utf-8")
text = text.replace(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '<meta name="viewport" content="width=800, height=480, initial-scale=1, maximum-scale=1, user-scalable=no">',
)
css = """
  /* Car Thing kiosk: Chromium is 800x480; Weston rotate-270 maps it onto the 480x800 panel. */
  html, body {
    width: 800px !important;
    height: 480px !important;
    max-width: 800px !important;
    max-height: 480px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    display: block !important;
    background: #050506 !important;
  }
  .stage, .device-wrap {
    width: 800px !important;
    height: 480px !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    filter: none !important;
  }
  .device, .screen-frame, .screen {
    width: 800px !important;
    height: 480px !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    background: #050506 !important;
  }
  .speaker-grid, .brand, .side-btn, .hint-caption { display: none !important; }
  .statusbar { padding: 8px 18px 4px !important; font-size: 15px !important; }
  .home-page {
    grid-template-columns: repeat(5, 1fr) !important;
    gap: 18px 12px !important;
    padding: 18px 24px 0 !important;
  }
  .app-icon .circle { width: 72px !important; height: 72px !important; }
  .app-icon span { font-size: 13px !important; }
  .circle svg { width: 34px !important; height: 34px !important; }
  .art { width: 210px !important; height: 210px !important; }
  .ctrl-btn { width: 48px !important; height: 48px !important; }
  .ctrl-btn.big { width: 64px !important; height: 64px !important; }
  .app-title { font-size: 18px !important; }
  .track-title { font-size: 18px !important; }
  .calc-btn { padding: 16px 0 !important; font-size: 18px !important; }
  .fm-freq { font-size: 48px !important; }
  .lock-time { font-size: 64px !important; }
"""
if "</style>" not in text:
    raise SystemExit("no style tag")
text = text.replace("</style>", css + "\n</style>", 1)
dst.write_text(text, encoding="utf-8", newline="\n")
print("wrote", dst, dst.stat().st_size)
