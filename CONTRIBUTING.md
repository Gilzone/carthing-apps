# Contributing to Car Thing Apps

Thank you for your interest in contributing to **Car Thing Apps**! We welcome contributions ranging from new HTML5 games and tools to documentation improvements and bug fixes.

---

## 🎯 Ground Rules & Attribution
1. **Respect Upstream Licenses:** All borrowed tools, libraries, and firmware must retain their original licenses and explicitly attribute their original authors.
2. **Be Kind & Constructive:** All participants are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 🕹️ Adding a New Game or Tool
We love expanding the Car Thing library! Keep in mind the physical hardware constraints:
* **Resolution:** 800×480 landscape display.
* **Architecture:** Quad-core Amlogic S905D2 (ARM Cortex-A53) with 512MB RAM and Mali-G31 GPU.
* **Storage:** Flash memory is limited. Apps should be self-contained and lightweight (HTML, CSS, JS).
* **Controls:** Design touch controls or integrate the physical rotary dial (`wheel` events, key codes `1` to `4`, and `M`).

### Adding to the Launcher Catalog
1. Place your self-contained app in `launcher/games/` or `launcher/tools/`.
2. Register your entry in `launcher/catalog.json` and `launcher/catalog.js`:
   ```json
   {
     "tab": "games",
     "file": "games/mygame.html",
     "name": "My Game",
     "hint": "Short description",
     "mark": "GM",
     "color": "#3b82f6"
   }
   ```
3. Test on device via `python add_project.py "path/to/mygame.html" --deploy`.

---

## 🚀 Submitting a Pull Request
1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/awesome-new-game
   ```
2. Commit your changes with a clear message:
   ```bash
   git commit -m "feat(game): add awesome new retro puzzle game"
   ```
3. Push to your branch and open a Pull Request.
4. Fill out the Pull Request template checklist.
