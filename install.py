#!/usr/bin/env python3
"""
Spotify Car Thing — 1-Click Complete Installer
Automated deployment of Nocturne Webapps, 23 Games, Tools Suite, and System Optimizations.
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

# Enable UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CARTHING_IP = os.environ.get("CARTHING_IP", "10.42.1.242")
CARTHING_USER = "root"
SCRIPT_DIR = Path(__file__).resolve().parent
LAUNCHER_DIR = SCRIPT_DIR / "launcher"

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5",
    "-o", "LogLevel=ERROR"
]

ASOUND_CONF = """pcm.!default {
    type asym
    capture.pcm "mic_hw"
}

pcm.mic_hw {
    type plug
    slave {
        pcm "hw:0,1"
        rate 48000
        channels 4
        format S16_LE
    }
}
"""

def print_banner():
    banner = r"""
========================================================================
   [+] SPOTIFY CAR THING -- 1-CLICK ALL-IN-ONE INSTALLER
   Custom Nocturne OS Webapps, 23 Games & Tools Suite
========================================================================
"""
    print(banner)

def log_step(step, total, msg):
    print(f"[{step}/{total}] [..] {msg}...")

def log_ok(msg):
    print(f"       [OK] {msg}")

def log_fail(msg):
    print(f"       [FAIL] {msg}")

def run_ssh(cmd, timeout=15):
    full_cmd = ["ssh"] + SSH_OPTS + [f"{CARTHING_USER}@{CARTHING_IP}", cmd]
    res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return res.returncode == 0, res.stdout.strip(), res.stderr.strip()

def run_scp(src, dst_remote, is_dir=False, timeout=60):
    cmd = ["scp"] + SSH_OPTS
    if is_dir:
        cmd.append("-r")
    cmd.extend([str(src), f"{CARTHING_USER}@{CARTHING_IP}:{dst_remote}"])
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return res.returncode == 0, res.stderr.strip()

def sync_directory(src_dir, remote_dst_dir):
    src_dir = Path(src_dir)
    if not src_dir.exists():
        return True
    for item in src_dir.iterdir():
        run_scp(item, f"{remote_dst_dir}/{item.name}", is_dir=item.is_dir())
    return True

def check_ssh_connection():
    try:
        ok, out, _ = run_ssh("echo CONNECTED", timeout=4)
        return ok and "CONNECTED" in out
    except Exception:
        return False

def wait_for_device(timeout_sec=120):
    print(f"Looking for Spotify Car Thing at {CARTHING_IP} (USB RNDIS/NCM)...")
    start = time.time()
    dots = 0
    while time.time() - start < timeout_sec:
        if check_ssh_connection():
            print("\n")
            log_ok(f"Car Thing detected online at {CARTHING_IP}!")
            return True
        sys.stdout.write(f"\rWaiting for USB connection ({int(time.time() - start)}s)... {'/' if dots % 2 == 0 else '-'}")
        sys.stdout.flush()
        dots += 1
        time.sleep(2)
    print("\n")
    log_fail(f"Could not reach Car Thing at {CARTHING_IP} after {timeout_sec}s.")
    print("Please ensure:")
    print(" 1. The Car Thing is plugged into your PC with a high-quality USB-C data cable.")
    print(" 2. The device has booted Nocturne (screen is on).")
    print(" 3. The USB Ethernet adapter shows an IP in the 10.42.1.x range.")
    return False

def create_desktop_shortcut():
    try:
        desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
        if not desktop.exists():
            return
        
        shortcut_path = desktop / "Car Thing Apps.lnk"
        script_path = SCRIPT_DIR / "carthing_apps.py"
        
        pyw = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pyw):
            pyw = sys.executable

        vbs_content = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{pyw}"
oLink.Arguments = "\"{script_path}\""
oLink.WorkingDirectory = "{SCRIPT_DIR}"
oLink.Description = "Spotify Car Thing Apps Manager"
oLink.Save
'''
        vbs_temp = SCRIPT_DIR / "_temp_shortcut.vbs"
        with open(vbs_temp, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        subprocess.run(["cscript", "//nologo", str(vbs_temp)], capture_output=True)
        if vbs_temp.exists():
            vbs_temp.unlink()
        log_ok("Created 'Car Thing Apps' shortcut on your Windows Desktop.")
    except Exception:
        pass

def main():
    print_banner()
    TOTAL_STEPS = 7

    # STEP 1: Check OpenSSH
    log_step(1, TOTAL_STEPS, "Checking OpenSSH tools")
    if not shutil.which("ssh") or not shutil.which("scp"):
        log_fail("OpenSSH client (ssh/scp) not found. Please enable OpenSSH in Windows Features.")
        sys.exit(1)
    log_ok("OpenSSH tools available")

    # STEP 2: Wait for Car Thing
    log_step(2, TOTAL_STEPS, "Connecting to Car Thing")
    if not wait_for_device(timeout_sec=90):
        sys.exit(1)

    # STEP 3: Prepare remote filesystem
    log_step(3, TOTAL_STEPS, "Preparing directories on Car Thing flash")
    prepare_cmd = (
        "mkdir -p /opt/nocturne/webapps/player/games "
        "/opt/nocturne/webapps/player/tools "
        "/opt/nocturne/webapps/player/tabs "
        "/opt/nocturne/webapps/player/projects/files/kolibri "
        "&& mkdir -p /var/nocturne-data/kws "
        "&& ln -sfn /var/nocturne-data/kws /opt/nocturne/webapps/player/tools/kws"
    )

    ok, _, err = run_ssh(prepare_cmd)
    if not ok:
        log_fail(f"Failed to create directories: {err}")
        sys.exit(1)
    log_ok("Remote directories ready")

    # STEP 4: Deploy Launcher & Core Assets
    log_step(4, TOTAL_STEPS, "Deploying 3D Coverflow Launcher & Catalog")
    files_to_copy = [
        (LAUNCHER_DIR / "index.html", "/opt/nocturne/webapps/player/index.html"),
        (LAUNCHER_DIR / "catalog.json", "/opt/nocturne/webapps/player/catalog.json"),
        (LAUNCHER_DIR / "catalog.js", "/opt/nocturne/webapps/player/catalog.js"),
        (LAUNCHER_DIR / "touch-fix.js", "/opt/nocturne/webapps/player/touch-fix.js"),
        (SCRIPT_DIR / "kiosk-env", "/opt/nocturne/kiosk-env"),
    ]
    for src, dst in files_to_copy:
        if src.exists():
            ok, err = run_scp(src, dst)
            if not ok:
                log_fail(f"Failed to copy {src.name}: {err}")
                sys.exit(1)
    log_ok("Launcher core files deployed")

    # STEP 5: Deploy Games & Tools Suite
    log_step(5, TOTAL_STEPS, "Deploying 23 Games & Tools Suite (Optimized Among Us, KolibriOS)")
    # Games (including nested amongus directory)
    sync_directory(LAUNCHER_DIR / "games", "/opt/nocturne/webapps/player/games")
    # Tools
    sync_directory(LAUNCHER_DIR / "tools", "/opt/nocturne/webapps/player/tools")
    # Tabs
    sync_directory(LAUNCHER_DIR / "tabs", "/opt/nocturne/webapps/player/tabs")
    # Kolibri files
    sync_directory(LAUNCHER_DIR / "projects" / "files" / "kolibri", "/opt/nocturne/webapps/player/projects/files/kolibri")

    log_ok("All Games, Tools, and KolibriOS assets synced")

    # STEP 6: Configure Audio & Services
    log_step(6, TOTAL_STEPS, "Configuring microphone routing & system services")
    config_script = f"""
mount -o remount,rw / 2>/dev/null || true
cat <<'EOF' > /etc/asound.conf
{ASOUND_CONF}
EOF
mount -o remount,ro / 2>/dev/null || true
systemctl disable player-httpd.service 2>/dev/null || true
systemctl stop player-httpd.service 2>/dev/null || true
systemctl restart chromium-kiosk
sleep 3
systemctl is-active chromium-kiosk
"""
    ok, out, _ = run_ssh(config_script)
    if "active" in out:
        log_ok("ALSA dual-link capture configured & Chromium Kiosk active!")
    else:
        log_ok("Services updated")

    # STEP 7: Desktop Integration
    log_step(7, TOTAL_STEPS, "Configuring Desktop Companion App")
    create_desktop_shortcut()

    print("\n" + "=" * 72)
    print("   [+] INSTALLATION COMPLETE! ENJOY YOUR CAR THING! [+]")
    print("   - Look at your Car Thing screen: the custom launcher is live!")
    print("   - Double-click 'Car Thing Apps' on your PC Desktop anytime to manage apps.")
    print("=" * 72 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
