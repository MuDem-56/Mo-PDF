# Third-party components

Mo-PDF includes or uses the following open-source components:

| Component | Version | License | Location |
|---|---|---|---|
| [PDF.js](https://github.com/mozilla/pdf.js) (Mozilla) | 3.11.174 | Apache License 2.0 | `app/lib/pdf*.js`, `app/viewer/` (license text: `app/viewer/LICENSE`) |
| [pdf-lib](https://github.com/Hopding/pdf-lib) | 1.17.1 | MIT | `app/lib/pdf-lib.min.js` |
| [JSZip](https://github.com/Stuk/jszip) | 3.10.1 | MIT (or GPLv3, dual-licensed) | `app/lib/jszip.min.js` |
| [pywebview](https://github.com/r0x0r/pywebview) | 6.x | BSD 3-Clause | bundled in the Windows build |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller) | 6.x | GPL 2.0 with bootloader exception | used only to build the EXE |

The files in `app/lib/` and `app/viewer/` are unmodified copies of the official releases.
In `app/viewer/`, only the source maps, debugger files and the sample PDF were removed.
