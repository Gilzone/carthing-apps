# 🚀 Spotify Discontinued the Car Thing... So We Turned It Into an Offline Retro Gaming & Edge AI Beast!

> **📺 Full Video Walkthrough Coming Soon on [GIL STUDIO (@gilstudio2763)](https://www.youtube.com/@gilstudio2763)**

---

## 💡 The Story
Spotify officially killed the Car Thing and told everyone to throw them away. Instead of letting this gorgeous 800×480 touchscreen, rotary knob, and 4-button hardware become e-waste, we resurrected it.

We didn't just flash a generic Linux build — we engineered a **complete, standalone handheld console and edge computing device** that runs **100% offline with zero cloud and zero companion PC**.

---

## 🕹️ 1. Dedicated Game Boy Handheld with Physical Knob Controls
We built a custom Game Boy engine mapped directly to the Car Thing’s unique physical controls:
- **🔘 Rotary Dial Push (Click the Knob):** Triggers **Button A** (Jump, Attack, Confirm).
- **🔴 Dedicated Thumb Button & Physical Back Button:** Triggers **Button B** (Run, Cancel, Inhale).
- **Tactile D-Pad & Top Preset Buttons:** Flawless directional control and hardware `SELECT` / `START`.
- **Pixel-Perfect Scaling:** Native $160 \times 144$ Game Boy resolution scaled to a crisp $400 \times 360$ bezel at locked **60 FPS**.

<p align="center">
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/gb_zelda_user_live.png" width="48%" alt="Zelda Link's Awakening on Car Thing" />
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/gb_pokemon_red_user_live.png" width="48%" alt="Pokemon Red on Car Thing" />
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/gb_kirby_user_live.png" width="48%" alt="Kirby's Dream Land 2 on Car Thing" />
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/retro_knob_b_ui.png" width="48%" alt="Handheld Controls Layout" />
</p>

---

## 🌐 2. On-Device Edge Neural Translation (No Internet Needed!)
Edge AI on an automotive gadget:
- Powered by **quantized Marian NMT neural networks** compiled to WebAssembly.
- Translates full sentences between English and Spanish on-device with zero internet connection.
- Custom touch keyboard with hardware debounce guard and instant `[ ⇄ Swap ]` bidirectional translation.

<p align="center">
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/tool_translator_direct_disk_live.png" width="48%" alt="Offline Neural Translation" />
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/tool_translator_bidirectional_success.png" width="48%" alt="Bidirectional Swap" />
</p>

---

## 🖥️ 3. Full 32-bit x86 PC Emulation & Everyday Tools
- **KolibriOS:** Boots a real 32-bit x86 desktop operating system in a 32MB virtual machine (`libv86`) with a smooth virtual touch trackpad.
- **Dial-Controlled E-Reader:** Turn the physical wheel to flip book pages naturally.
- **Microphone Voice Recorder:** Uses the Car Thing’s onboard microphone array to record audio notes straight to internal flash.

<p align="center">
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/kolibri_os.png" width="48%" alt="KolibriOS on Car Thing" />
  <img src="https://raw.githubusercontent.com/Gilzone/carthing-apps/main/docs/screenshots/tool_reader.png" width="48%" alt="E-Reader" />
</p>

---

## 🎬 VIDEO COMING SOON ON GIL STUDIO!

We are putting together a full, in-depth YouTube video breakdown covering:
1. **How we bypassed the bootloader and flashed custom Linux.**
2. **Wiring the rotary dial and physical buttons into custom browser apps.**
3. **Running Edge AI and Game Boy emulation with zero lag.**
4. **Complete open-source release & setup tutorial for your own Car Thing.**

👉 **Subscribe so you don't miss the video:**  
🔗 **[youtube.com/@gilstudio2763](https://www.youtube.com/@gilstudio2763?sub_confirmation=1)**

---

### 📋 Ready-to-Post Snippets:

#### 🔴 YouTube Community Post / Video Description:
```text
Spotify said the Car Thing was dead... so we turned it into a retro console and offline Edge AI device! 🚗🕹️

✅ Dedicated Game Boy & GBA Player (2048, Celeste, Anguna + BYO ROMs) using the rotary dial click as Button A!
✅ 100% Offline Neural Machine Translation (no internet needed)
✅ x86 PC Emulation & Dial E-Reader

Full build video and tutorial coming soon! Subscribe to GIL STUDIO so you don't miss it:
👉 https://www.youtube.com/@gilstudio2763?sub_confirmation=1
```

#### 🌐 Reddit Post (`r/CarThingHax`, `r/cyberDeck`, `r/emulation`):
```text
Title: Don't throw away your Spotify Car Thing — we turned it into a standalone Game Boy console & Offline Edge AI device!

Spotify officially deprecated the Car Thing, but the hardware is too good to scrap. We converted it into a dedicated handheld running:
1. Cycle-accurate Game Boy & GBA (2048, Celeste, Anguna, plus Bring Your Own ROMs) where clicking the physical rotary dial acts as Button A, with a dedicated tactile B button and top preset buttons for Select/Start.

2. 100% on-device Neural Translation running quantized Marian NMT models over WebAssembly (zero cloud/WiFi).
3. KolibriOS 32-bit x86 PC emulation with touch trackpad.
4. Dial-controlled e-reader.

Everything is 100% open source on GitHub: https://github.com/Gilzone/carthing-apps
Full build breakdown video coming soon on GIL STUDIO: https://www.youtube.com/@gilstudio2763
```
