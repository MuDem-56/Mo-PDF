"""Mo-PDF – installer / uninstaller (per user, no admin rights). German or English UI."""
import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import winreg
import zipfile
from tkinter import messagebox, ttk

APP_NAME = "Mo-PDF"
APP_EXE = "Mo-PDF.exe"
VERSION = "1.1.0"
PUBLISHER = "Mo-PDF"
REG_UNINSTALL = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\MoPDF"
PROGID = "MoPDF.Dokument"
INSTALL_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Programs", APP_NAME)
START_MENU_LNK = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs", APP_NAME + ".lnk")
NO_WINDOW = 0x08000000


def _ui_lang():
    try:
        return "de" if (ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF) == 0x07 else "en"
    except Exception:
        return "en"


LANG = _ui_lang()
TEXT = {
    "de": {
        "desc": "PDFs lesen, zusammenfügen, teilen, drehen und komprimieren",
        "doctype": "PDF-Dokument",
        "closing": "Beende laufende Instanz …", "copying": "Kopiere Dateien …", "shortcuts": "Erstelle Verknüpfungen …",
        "registering": "Registriere Programm …", "done": "Fertig!",
        "tagline": "PDFs lesen, zusammenfügen, teilen, drehen,\nkomprimieren – komplett offline auf deinem PC.",
        "folder": "Installationsordner:", "desktop": "Verknüpfung auf dem Desktop",
        "openwith": "Bei PDF-Dateien unter „Öffnen mit“ anzeigen", "launch": "Nach der Installation starten",
        "noadmin": "Keine Administratorrechte nötig.", "install": "Installieren", "cancel": "Abbrechen",
        "failed": "Installation fehlgeschlagen:\n{e}", "finished": "Installation abgeschlossen. Du findest die App im Startmenü.",
        "finish": "Fertig", "confirm_uninstall": "{app} wirklich vollständig entfernen?", "removed": "{app} wurde entfernt.",
    },
    "en": {
        "desc": "Read, merge, split, rotate and compress PDFs",
        "doctype": "PDF Document",
        "closing": "Closing running instance …", "copying": "Copying files …", "shortcuts": "Creating shortcuts …",
        "registering": "Registering app …", "done": "Done!",
        "tagline": "Read, merge, split, rotate and compress PDFs –\nfully offline on your PC.",
        "folder": "Install folder:", "desktop": "Create a desktop shortcut",
        "openwith": "Show under “Open with” for PDF files", "launch": "Launch after installation",
        "noadmin": "No administrator rights needed.", "install": "Install", "cancel": "Cancel",
        "failed": "Installation failed:\n{e}", "finished": "Installation complete. You'll find the app in the Start menu.",
        "finish": "Finish", "confirm_uninstall": "Completely remove {app}?", "removed": "{app} has been removed.",
    },
}[LANG]
SETTINGS_DIR = os.path.join(os.environ.get("APPDATA", ""), APP_NAME)


def resource(name):
    return os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), name)


def desktop_dir():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"],
            capture_output=True, text=True, creationflags=NO_WINDOW, timeout=20,
        ).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return os.path.join(os.environ["USERPROFILE"], "Desktop")


def make_shortcut(lnk, target, workdir):
    ps = (
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:LNK);"
        "$s.TargetPath=$env:TGT;$s.WorkingDirectory=$env:WD;$s.IconLocation=$env:TGT+',0';"
        "$s.Description=$env:DESC;$s.Save()"
    )
    env = dict(os.environ, LNK=lnk, TGT=target, WD=workdir, DESC=TEXT["desc"])
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], env=env, creationflags=NO_WINDOW, timeout=30, check=True)


def set_key(path, values):
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as k:
        for name, val in values.items():
            if isinstance(val, int):
                winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, val)
            else:
                winreg.SetValueEx(k, name, 0, winreg.REG_SZ, val)


def delete_tree(root, path):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as k:
            while True:
                try:
                    sub = winreg.EnumKey(k, 0)
                except OSError:
                    break
                delete_tree(root, path + "\\" + sub)
        winreg.DeleteKey(root, path)
    except FileNotFoundError:
        pass


def delete_value(path, name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS) as k:
            winreg.DeleteValue(k, name)
    except FileNotFoundError:
        pass


def notify_shell():
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
    except Exception:
        pass


def kill_running():
    subprocess.run(["taskkill", "/f", "/im", APP_EXE], capture_output=True, creationflags=NO_WINDOW)


def register_open_with(exe):
    cmd = f'"{exe}" "%1"'
    set_key(rf"Software\Classes\{PROGID}", {"": TEXT["doctype"], "FriendlyTypeName": TEXT["doctype"]})
    set_key(rf"Software\Classes\{PROGID}\DefaultIcon", {"": f'"{exe}",0'})
    set_key(rf"Software\Classes\{PROGID}\shell\open\command", {"": cmd})
    set_key(r"Software\Classes\.pdf\OpenWithProgids", {PROGID: ""})
    set_key(rf"Software\Classes\Applications\{APP_EXE}", {"FriendlyAppName": APP_NAME})
    set_key(rf"Software\Classes\Applications\{APP_EXE}\shell\open\command", {"": cmd})
    set_key(rf"Software\Classes\Applications\{APP_EXE}\SupportedTypes", {".pdf": "", ".png": "", ".jpg": "", ".jpeg": ""})


def install(progress, desktop_shortcut, open_with):
    progress(TEXT["closing"], 5)
    kill_running()
    progress(TEXT["copying"], 15)
    if os.path.isdir(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR, ignore_errors=True)
    os.makedirs(INSTALL_DIR, exist_ok=True)
    with zipfile.ZipFile(resource("payload.zip")) as z:
        names = z.infolist()
        for i, info in enumerate(names):
            z.extract(info, INSTALL_DIR)
            if i % 25 == 0:
                progress(TEXT["copying"], 15 + int(65 * i / max(1, len(names))))
    exe = os.path.join(INSTALL_DIR, APP_EXE)
    uninstaller = os.path.join(INSTALL_DIR, "Uninstall.exe")
    if getattr(sys, "frozen", False):
        shutil.copy2(sys.executable, uninstaller)

    progress(TEXT["shortcuts"], 85)
    make_shortcut(START_MENU_LNK, exe, INSTALL_DIR)
    if desktop_shortcut:
        make_shortcut(os.path.join(desktop_dir(), APP_NAME + ".lnk"), exe, INSTALL_DIR)

    progress(TEXT["registering"], 93)
    size_kb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(INSTALL_DIR) for f in fs) // 1024
    set_key(REG_UNINSTALL, {
        "DisplayName": APP_NAME,
        "DisplayVersion": VERSION,
        "Publisher": PUBLISHER,
        "DisplayIcon": f'"{exe}",0',
        "InstallLocation": INSTALL_DIR,
        "UninstallString": f'"{uninstaller}" --uninstall',
        "QuietUninstallString": f'"{uninstaller}" --uninstall --quiet',
        "NoModify": 1,
        "NoRepair": 1,
        "EstimatedSize": int(size_kb),
    })
    if open_with:
        register_open_with(exe)
    notify_shell()
    progress(TEXT["done"], 100)
    return exe


def uninstall():
    kill_running()
    for lnk in (START_MENU_LNK, os.path.join(desktop_dir(), APP_NAME + ".lnk")):
        try:
            os.remove(lnk)
        except FileNotFoundError:
            pass
    delete_tree(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}")
    delete_tree(winreg.HKEY_CURRENT_USER, rf"Software\Classes\Applications\{APP_EXE}")
    delete_value(r"Software\Classes\.pdf\OpenWithProgids", PROGID)
    delete_tree(winreg.HKEY_CURRENT_USER, REG_UNINSTALL)
    shutil.rmtree(SETTINGS_DIR, ignore_errors=True)
    notify_shell()
    # remove files; the running uninstaller lives inside the folder, so finish via a detached cmd
    for entry in os.listdir(INSTALL_DIR) if os.path.isdir(INSTALL_DIR) else []:
        p = os.path.join(INSTALL_DIR, entry)
        try:
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        except OSError:
            pass


def schedule_folder_removal():
    subprocess.Popen(
        f'cmd /c ping -n 6 127.0.0.1 >nul & rmdir /s /q "{INSTALL_DIR}"',
        creationflags=NO_WINDOW | 0x00000008, cwd=tempfile.gettempdir(), shell=False,
    )


# ---------------------------------------------------------------- GUI
class InstallerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} {VERSION} – Setup")
        self.root.resizable(False, False)
        try:
            self.icon = tk.PhotoImage(file=resource("icon.png")).subsample(16, 16)
            self.root.iconphoto(True, self.icon)
            self.big = tk.PhotoImage(file=resource("icon.png")).subsample(12, 12)
        except Exception:
            self.big = None
        f = ttk.Frame(self.root, padding=22)
        f.pack(fill="both", expand=True)
        head = ttk.Frame(f)
        head.pack(fill="x")
        if self.big:
            ttk.Label(head, image=self.big).pack(side="left", padx=(0, 14))
        txt = ttk.Frame(head)
        txt.pack(side="left", fill="x")
        ttk.Label(txt, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(txt, text=TEXT["tagline"],
                  foreground="#555").pack(anchor="w")
        ttk.Separator(f).pack(fill="x", pady=14)
        ttk.Label(f, text=TEXT["folder"]).pack(anchor="w")
        ttk.Label(f, text=INSTALL_DIR, foreground="#555").pack(anchor="w", pady=(0, 10))
        self.v_desk = tk.BooleanVar(value=True)
        self.v_open = tk.BooleanVar(value=True)
        self.v_start = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text=TEXT["desktop"], variable=self.v_desk).pack(anchor="w")
        ttk.Checkbutton(f, text=TEXT["openwith"], variable=self.v_open).pack(anchor="w")
        self.cb_start = ttk.Checkbutton(f, text=TEXT["launch"], variable=self.v_start)
        self.cb_start.pack(anchor="w")
        self.status = ttk.Label(f, text=TEXT["noadmin"], foreground="#555")
        self.status.pack(anchor="w", pady=(14, 4))
        self.bar = ttk.Progressbar(f, length=420, maximum=100)
        self.bar.pack(fill="x")
        btns = ttk.Frame(f)
        btns.pack(fill="x", pady=(16, 0))
        self.btn = ttk.Button(btns, text=TEXT["install"], command=self.start)
        self.btn.pack(side="right")
        self.cancel = ttk.Button(btns, text=TEXT["cancel"], command=self.root.destroy)
        self.cancel.pack(side="right", padx=8)
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        self.root.geometry(f"+{(self.root.winfo_screenwidth() - w) // 2}+{(self.root.winfo_screenheight() - h) // 3}")

    def progress(self, msg, pct):
        self.root.after(0, lambda: (self.status.config(text=msg), self.bar.config(value=pct)))

    def start(self):
        self.btn.config(state="disabled")
        self.cancel.config(state="disabled")
        threading.Thread(target=self.work, daemon=True).start()

    def work(self):
        try:
            exe = install(self.progress, self.v_desk.get(), self.v_open.get())
        except Exception as e:  # noqa: BLE001
            self.root.after(0, lambda: (messagebox.showerror(APP_NAME, TEXT["failed"].format(e=e)),
                                        self.btn.config(state="normal"), self.cancel.config(state="normal")))
            return
        self.root.after(0, lambda: self.done(exe))

    def done(self, exe):
        self.status.config(text=TEXT["finished"])
        self.btn.config(text=TEXT["finish"], state="normal", command=lambda: self.finish(exe))

    def finish(self, exe):
        if self.v_start.get():
            subprocess.Popen([exe], cwd=INSTALL_DIR)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    if "--uninstall" in sys.argv:
        quiet = "--quiet" in sys.argv
        if not quiet:
            r = tk.Tk()
            r.withdraw()
            if not messagebox.askyesno(APP_NAME, TEXT["confirm_uninstall"].format(app=APP_NAME)):
                return
        uninstall()
        if not quiet:
            messagebox.showinfo(APP_NAME, TEXT["removed"].format(app=APP_NAME))
        schedule_folder_removal()
        return
    if "--quiet" in sys.argv:
        install(lambda *_: None, True, True)
        return
    InstallerUI().run()


if __name__ == "__main__":
    main()
