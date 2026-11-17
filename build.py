"""Baut Mo-PDF.exe und den Installer  ->  Installer/Mo-PDF-Setup.exe

Aufruf:  .venv\\Scripts\\python build.py
"""
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
ICON = os.path.join(ROOT, "build_assets", "icon.ico")
ICON_PNG = os.path.join(ROOT, "build_assets", "icon.png")
OUT = os.path.join(ROOT, "Installer")


def pyinstaller(*args):
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--log-level", "WARN", *args], check=True, cwd=ROOT)


def main():
    shutil.rmtree(BUILD, ignore_errors=True)
    # 1) the app itself (folder build = fast start)
    pyinstaller(
        os.path.join(ROOT, "main.py"),
        "--name", "Mo-PDF", "--windowed", "--onedir",
        "--icon", ICON,
        "--add-data", f"{os.path.join(ROOT, 'app')}{os.pathsep}app",
        "--distpath", os.path.join(BUILD, "dist"),
        "--workpath", os.path.join(BUILD, "work"),
        "--specpath", BUILD,
    )
    app_dir = os.path.join(BUILD, "dist", "Mo-PDF")
    # 2) zip it as installer payload
    payload = os.path.join(BUILD, "payload.zip")
    with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for dp, _, files in os.walk(app_dir):
            for f in files:
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, app_dir))
    # 3) single-file setup
    pyinstaller(
        os.path.join(ROOT, "installer.py"),
        "--name", "Mo-PDF-Setup", "--windowed", "--onefile",
        "--icon", ICON,
        "--add-data", f"{payload}{os.pathsep}.",
        "--add-data", f"{ICON_PNG}{os.pathsep}.",
        "--distpath", OUT,
        "--workpath", os.path.join(BUILD, "work_setup"),
        "--specpath", BUILD,
    )
    setup = os.path.join(OUT, "Mo-PDF-Setup.exe")
    print(f"\nFertig: {setup}  ({os.path.getsize(setup) / 1048576:.1f} MB)")


if __name__ == "__main__":
    main()
