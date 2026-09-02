"""Car Thing manager: see, add, remove HTML, pick tabs, create tabs, sync over USB."""
from __future__ import annotations

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import add_project as ap

BG = "#0b0c0f"
FG = "#e5e7eb"
MUTED = "#9ca3af"
GREEN = "#34d399"
CARD = "#14161c"
PY = Path(r"C:\Users\Gilzh\AppData\Local\Programs\Python\Python312\python.exe")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Car Thing Apps")
        self.geometry("920x740+40+30")
        self.configure(bg=BG)
        self.minsize(780, 620)
        self.lift()
        self.attributes("-topmost", True)
        self.after(2000, lambda: self.attributes("-topmost", False))
        self.connected = False
        self.busy = False
        self.tab_id = "games"
        self.device_names: dict[str, set[str]] | None = None

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TButton", background=CARD, foreground=FG, padding=8)
        style.map("TButton", background=[("active", "#1f2937")])
        style.configure("Treeview", background=CARD, foreground=FG, fieldbackground=CARD, rowheight=26)
        style.configure("Treeview.Heading", background="#111827", foreground=FG, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", GREEN)], foreground=[("selected", "#052e1a")])

        top = ttk.Frame(self)
        top.pack(fill="x", padx=16, pady=(16, 8))
        ttk.Label(top, text="CAR THING", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.status = ttk.Label(top, text="Plug in the USB cable…", foreground=MUTED)
        self.status.pack(side="right")
        self.dot = tk.Canvas(top, width=14, height=14, bg=BG, highlightthickness=0)
        self.dot.pack(side="right", padx=8)
        self._set_dot(False)

        ttk.Label(self, text="Manage HTML on the Car Thing", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16)
        ttk.Label(
            self,
            text="Pick a tab, add or remove pages, then Sync. New tabs show up on the device.",
            foreground=MUTED,
        ).pack(anchor="w", padx=16, pady=(0, 8))

        tabrow = ttk.Frame(self)
        tabrow.pack(fill="x", padx=16, pady=4)
        ttk.Label(tabrow, text="Tab:").pack(side="left")
        self.tab_combo = ttk.Combobox(tabrow, state="readonly", width=22)
        self.tab_combo.pack(side="left", padx=8)
        self.tab_combo.bind("<<ComboboxSelected>>", lambda e: self.on_tab_change())
        ttk.Button(tabrow, text="New tab", command=self.new_tab).pack(side="left", padx=4)
        ttk.Button(tabrow, text="Delete tab", command=self.delete_tab).pack(side="left", padx=4)

        cols = ttk.Frame(self)
        cols.pack(fill="both", expand=True, padx=16, pady=8)

        left = ttk.Frame(cols)
        left.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text="In this tab", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.tree = ttk.Treeview(left, columns=("file", "ondev"), show="headings", height=14)
        self.tree.heading("file", text="Name")
        self.tree.heading("ondev", text="On device")
        self.tree.column("file", width=360)
        self.tree.column("ondev", width=110)
        ys = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ys.set)
        self.tree.pack(side="left", fill="both", expand=True)
        ys.pack(side="left", fill="y")

        right = ttk.Frame(cols)
        right.pack(side="right", fill="y", padx=(12, 0))
        ttk.Button(right, text="Add HTML to this tab", command=self.add_html).pack(fill="x", pady=3)
        ttk.Button(right, text="Add folder to this tab", command=self.add_folder).pack(fill="x", pady=3)
        ttk.Button(right, text="Remove selected", command=self.remove_selected).pack(fill="x", pady=3)
        ttk.Button(right, text="Move to another tab", command=self.move_selected).pack(fill="x", pady=3)
        ttk.Separator(right).pack(fill="x", pady=10)
        self.pad_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(right, text="WASD pad on new HTML", variable=self.pad_var).pack(anchor="w", pady=3)
        ttk.Separator(right).pack(fill="x", pady=10)
        self.sync_btn = ttk.Button(right, text="Sync to Car Thing", command=self.sync)
        self.sync_btn.pack(fill="x", pady=3)
        ttk.Button(right, text="Refresh", command=self.refresh).pack(fill="x", pady=3)

        self.log = tk.Text(self, height=8, bg="#050506", fg=MUTED, relief="flat", font=("Consolas", 9))
        self.log.pack(fill="x", padx=16, pady=(4, 14))
        self._log("Open this after plugging in USB. Add HTML to a tab, then Sync.")
        self.refresh()
        self.after(400, self.poll)

    def _set_dot(self, on: bool) -> None:
        self.dot.delete("all")
        self.dot.create_oval(2, 2, 12, 12, fill=GREEN if on else "#4b5563", outline="")

    def _log(self, msg: str) -> None:
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def catalog(self) -> dict:
        return ap.load_catalog()

    def tabs(self) -> list[dict]:
        return self.catalog().get("tabs", [])

    def refresh_tab_combo(self) -> None:
        names = [f"{t.get('label') or t['id']}  ({t['id']})" for t in self.tabs()]
        ids = [t["id"] for t in self.tabs()]
        self.tab_combo["values"] = names
        if self.tab_id in ids:
            self.tab_combo.current(ids.index(self.tab_id))
        elif names:
            self.tab_combo.current(0)
            self.tab_id = ids[0]

    def on_tab_change(self) -> None:
        idx = self.tab_combo.current()
        tabs = self.tabs()
        if 0 <= idx < len(tabs):
            self.tab_id = tabs[idx]["id"]
            self.fill_items()

    def fill_items(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        cat = self.catalog()
        rows = [it for it in cat.get("items", []) if it.get("tab") == self.tab_id]
        ondev = self.device_names
        if not rows:
            self.tree.insert("", "end", values=("(empty tab — add HTML)", ""))
            return
        for it in rows:
            fname = Path(it.get("file", "")).name
            mark = ""
            if ondev is not None:
                bucket = "game" if self.tab_id == "games" else "tool" if self.tab_id == "tools" else "app"
                names = ondev.get(bucket, set()) | ondev.get(self.tab_id, set())
                mark = "yes" if fname in names else "not yet"
            self.tree.insert("", "end", iid=it.get("file"), values=(it.get("name", fname), mark))

    def refresh(self) -> None:
        self.refresh_tab_combo()
        if self.connected:
            try:
                self.device_names = ap.device_file_names()
            except Exception as e:
                self._log("device list: " + str(e))
                self.device_names = None
        else:
            self.device_names = None
        self.fill_items()

    def poll(self) -> None:
        threading.Thread(target=self._poll_worker, daemon=True).start()
        self.after(2500, self.poll)

    def _poll_worker(self) -> None:
        ok = ap.ssh_ok()
        self.after(0, lambda: self._set_conn(ok))

    def _set_conn(self, ok: bool) -> None:
        if ok == self.connected:
            return
        self.connected = ok
        self._set_dot(ok)
        self.status.configure(
            text="Car Thing connected" if ok else "Plug in the USB cable…",
            foreground=GREEN if ok else MUTED,
        )
        self._log("Connected." if ok else "Disconnected.")
        if ok:
            self.refresh()

    def selected_item(self) -> dict | None:
        sel = self.tree.selection()
        if not sel:
            return None
        file = sel[0]
        for it in self.catalog().get("items", []):
            if it.get("file") == file:
                return it
        return None

    def add_html(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Pick HTML for tab " + self.tab_id,
            filetypes=[("HTML", "*.html *.htm"), ("All files", "*.*")],
        )
        self._add_paths([Path(p) for p in paths])

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Folder of HTML files")
        if not folder:
            return
        paths = [p for p in Path(folder).iterdir() if p.suffix.lower() in {".html", ".htm"}]
        self._add_paths(paths)

    def _add_paths(self, paths: list[Path]) -> None:
        if not paths:
            return
        pad = self.pad_var.get()
        added = []
        try:
            for p in paths:
                it = ap.add(p, None, None, None, None, pad, self.tab_id)
                added.append(Path(ap.LAUNCHER / it["file"]))
                self._log("added " + it["name"] + " -> " + it["tab"])
        except Exception as e:
            messagebox.showerror("Car Thing Apps", str(e))
            return
        self.refresh()
        if self.connected:
            self._start_sync(extra=added)

    def remove_selected(self) -> None:
        it = self.selected_item()
        if not it:
            messagebox.showinfo("Car Thing Apps", "Select an item in the list first.")
            return
        if not messagebox.askyesno("Remove", "Remove “" + it["name"] + "” from the " + self.tab_id + " tab?"):
            return
        try:
            ap.remove(it["file"])
            self._log("removed " + it["file"])
            self.refresh()
            if self.connected:
                self._start_sync(delete=[it["file"]])
        except Exception as e:
            messagebox.showerror("Car Thing Apps", str(e))

    def move_selected(self) -> None:
        it = self.selected_item()
        if not it:
            messagebox.showinfo("Car Thing Apps", "Select an item first.")
            return
        ids = [t["id"] for t in self.tabs()]
        dest = simpledialog.askstring("Move", "Move to tab id:\n" + ", ".join(ids), parent=self)
        if not dest:
            return
        try:
            ap.move_item(it["file"], dest.strip())
            self.tab_id = dest.strip()
            self._log("moved " + it["name"] + " -> " + dest)
            self.refresh()
            if self.connected:
                self._start_sync()
        except Exception as e:
            messagebox.showerror("Car Thing Apps", str(e))

    def new_tab(self) -> None:
        name = simpledialog.askstring("New tab", "Tab name (shows on the Car Thing):", parent=self)
        if not name:
            return
        try:
            tab = ap.add_tab(name)
            self.tab_id = tab["id"]
            self._log("new tab " + tab["id"])
            self.refresh()
            if self.connected:
                self._start_sync()
        except Exception as e:
            messagebox.showerror("Car Thing Apps", str(e))

    def delete_tab(self) -> None:
        if self.tab_id in {"games", "tools"}:
            messagebox.showinfo("Car Thing Apps", "Games and Tools tabs stay. You can still remove items from them.")
            return
        if not messagebox.askyesno("Delete tab", "Delete tab “" + self.tab_id + "” and its items from the launcher?"):
            return
        try:
            files = [it["file"] for it in self.catalog().get("items", []) if it.get("tab") == self.tab_id]
            ap.remove_tab(self.tab_id)
            self.tab_id = "apps"
            self._log("deleted tab")
            self.refresh()
            if self.connected:
                self._start_sync(delete=files)
        except Exception as e:
            messagebox.showerror("Car Thing Apps", str(e))

    def sync(self) -> None:
        if not self.connected:
            messagebox.showwarning("Car Thing Apps", "Plug in the Car Thing USB cable first.")
            return
        self._start_sync()

    def _start_sync(self, extra: list[Path] | None = None, delete: list[str] | None = None) -> None:
        if self.busy:
            return
        self.busy = True
        self.sync_btn.configure(state="disabled")
        threading.Thread(target=self._sync_worker, args=(extra, delete), daemon=True).start()

    def _sync_worker(self, extra, delete) -> None:
        def log(msg: str) -> None:
            self.after(0, lambda m=msg: self._log(m))
        try:
            ap.save_catalog(ap.load_catalog())
            ap.deploy_connected(log, extra_files=extra, delete_remote=delete)
            self.after(0, self._sync_done)
        except Exception as e:
            self.after(0, lambda: self._sync_fail(str(e)))

    def _sync_done(self) -> None:
        self.busy = False
        self.sync_btn.configure(state="normal")
        self.refresh()
        self._log("Synced. Check the Car Thing tabs.")

    def _sync_fail(self, err: str) -> None:
        self.busy = False
        self.sync_btn.configure(state="normal")
        self._log("ERROR " + err)
        messagebox.showerror("Car Thing Apps", err)


if __name__ == "__main__":
    App().mainloop()
