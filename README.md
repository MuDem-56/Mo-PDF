<p align="center"><img src="build_assets/icon.png" width="96" alt="Mo-PDF Logo"></p>

<h1 align="center">Mo-PDF</h1>

<p align="center">
PDFs lesen, zusammenfügen, teilen, drehen und komprimieren – kostenlos, offline, ohne Upload.
</p>

<p align="center">
<a href="../../releases/latest"><b>⬇ Windows-Installer herunterladen</b></a>
</p>

---

## Funktionen

**📖 Lesen**
- Schneller PDF-Reader (basiert auf Mozillas PDF.js)
- Volltextsuche, Zoom, Seitenminiaturen, Inhaltsverzeichnis
- Drucken
- Text, Freihand-Zeichnungen und Bilder einfügen und als PDF speichern
- Als Programm unter „Öffnen mit“ für PDF-Dateien verfügbar

**✏ Bearbeiten**
- Mehrere PDFs und Bilder zu einer PDF **zusammenfügen**
- Seiten per Drag & Drop **sortieren**, **drehen**, **löschen**, **duplizieren**
- Auswahl als eigene PDF **extrahieren**
- **Teilen**: jede Seite einzeln oder alle N Seiten (als ZIP)
- Seiten als **PNG-Bilder** exportieren
- **Wasserzeichen** und **Seitenzahlen** einfügen
- **Bilder → PDF** (JPG, PNG, WebP …)
- **Komprimieren** (ideal für gescannte Dokumente)

**🔒 Privat:** Alles läuft lokal auf deinem PC. Es werden keine Dateien hochgeladen,
und die App braucht kein Internet.

## Installation (Windows 10/11)

1. Unter [Releases](../../releases/latest) die Datei **`Mo-PDF-Setup.exe`** herunterladen.
2. Doppelklicken → **Installieren**. Es sind keine Administratorrechte nötig.
3. Mo-PDF ist danach im Startmenü und, wenn gewünscht, auf dem Desktop zu finden.

> Weil der Installer nicht digital signiert ist, zeigt Windows evtl. „Der Computer wurde geschützt“.
> Dann auf **Weitere Informationen → Trotzdem ausführen** klicken.

Installiert wird nach `%LOCALAPPDATA%\Programs\Mo-PDF`. Deinstallieren geht über
**Einstellungen → Apps → Mo-PDF**.

Mo-PDF als Standard-App für PDFs festlegen: Rechtsklick auf eine PDF → **Öffnen mit** →
**Andere App auswählen** → **Mo-PDF** → **Immer**.

## Selbst bauen

Voraussetzungen: Windows, Python 3.12+ und Edge WebView2 (bei Windows 11 vorinstalliert).

```bat
python -m venv .venv
.venv\Scripts\python -m pip install pywebview pyinstaller
.venv\Scripts\python main.py        :: App direkt starten
.venv\Scripts\python build.py       :: Installer\Mo-PDF-Setup.exe bauen
```

Die Oberfläche (`app/index.html`) läuft auch ohne Python in jedem modernen Browser,
wenn man den Ordner über einen lokalen Webserver ausliefert, zum Beispiel mit
`python -m http.server` → `http://localhost:8000/app/`.

## Aufbau

| Datei / Ordner | Zweck |
|---|---|
| `app/index.html` | Gesamte Oberfläche: Lesen und Bearbeiten |
| `app/lib/` | pdf-lib, PDF.js und JSZip (lokal, damit die App offline läuft) |
| `app/viewer/` | PDF.js-Reader |
| `main.py` | Desktop-Fenster (pywebview + WebView2), Speichern-Dialog, „Öffnen mit“ |
| `installer.py` | Setup und Deinstallation (pro Benutzer, ohne Adminrechte) |
| `build.py` | Baut `Mo-PDF.exe` und `Mo-PDF-Setup.exe` mit PyInstaller |

## Lizenz

[MIT](LICENSE). Hinweise zu den enthaltenen Fremdkomponenten stehen in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
