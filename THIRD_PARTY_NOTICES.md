# Drittanbieter-Komponenten

Mo-PDF enthält bzw. nutzt die folgenden Open-Source-Komponenten:

| Komponente | Version | Lizenz | Ort |
|---|---|---|---|
| [PDF.js](https://github.com/mozilla/pdf.js) (Mozilla) | 3.11.174 | Apache License 2.0 | `app/lib/pdf*.js`, `app/viewer/` (Lizenztext: `app/viewer/LICENSE`) |
| [pdf-lib](https://github.com/Hopding/pdf-lib) | 1.17.1 | MIT | `app/lib/pdf-lib.min.js` |
| [JSZip](https://github.com/Stuk/jszip) | 3.10.1 | MIT (oder GPLv3, dual lizenziert) | `app/lib/jszip.min.js` |
| [pywebview](https://github.com/r0x0r/pywebview) | 6.x | BSD 3-Clause | im Windows-Build enthalten |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller) | 6.x | GPL 2.0 mit Bootloader-Ausnahme | nur zum Bauen der EXE |

Die Dateien unter `app/lib/` und `app/viewer/` sind unveränderte Kopien der offiziellen Releases
(bei `app/viewer/` wurden lediglich Source-Maps, Debugger-Dateien und die Beispiel-PDF entfernt).
