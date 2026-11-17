"""Mo-PDF – Desktop-Start (pywebview + Edge WebView2)."""
import base64
import json
import mimetypes
import os
import sys

import webview

APP_NAME = "Mo-PDF"


def resource(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


SAVE = getattr(getattr(webview, "FileDialog", None), "SAVE", None) or webview.SAVE_DIALOG

FILE_TYPES = {
    "de": {".pdf": "PDF-Dateien (*.pdf)", ".zip": "ZIP-Archive (*.zip)", "*": "Alle Dateien (*.*)"},
    "en": {".pdf": "PDF files (*.pdf)", ".zip": "ZIP archives (*.zip)", "*": "All files (*.*)"},
}
SETTINGS = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME, "settings.json")


def load_settings():
    try:
        with open(SETTINGS, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


class Api:
    def __init__(self):
        self._window = None
        self._last_dir = None
        args = [os.path.abspath(a) for a in sys.argv[1:] if os.path.isfile(a)]
        self._args = args
        if args:
            self._last_dir = os.path.dirname(args[0])

    def get_lang(self):
        return load_settings().get("lang")

    def set_lang(self, lang):
        data = load_settings()
        data["lang"] = lang
        os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
        with open(SETTINGS, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return True

    def save_file(self, filename, b64, lang="de"):
        ext = os.path.splitext(filename)[1].lower()
        names = FILE_TYPES.get(lang, FILE_TYPES["en"])
        types = (names[ext], names["*"]) if ext in names else (names["*"],)
        kwargs = dict(save_filename=filename, file_types=types)
        if self._last_dir:
            kwargs["directory"] = self._last_dir
        result = self._window.create_file_dialog(SAVE, **kwargs)
        if not result:
            return None
        path = result if isinstance(result, str) else result[0]
        if ext and not path.lower().endswith(ext):
            path += ext
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        self._last_dir = os.path.dirname(path)
        return path

    def initial_files(self):
        out = []
        for p in self._args:
            with open(p, "rb") as f:
                out.append({
                    "name": os.path.basename(p),
                    "mime": mimetypes.guess_type(p)[0] or "",
                    "b64": base64.b64encode(f.read()).decode("ascii"),
                })
        self._args = []
        return out


def main():
    api = Api()
    api._window = webview.create_window(
        APP_NAME,
        url=resource("app", "index.html"),
        js_api=api,
        width=1320,
        height=860,
        min_size=(720, 520),
    )
    webview.start(gui="edgechromium", debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
