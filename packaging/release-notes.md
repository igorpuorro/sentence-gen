**sentence-gen for Windows**: prints one sentence built from your templates, with random
variations and emojis. Nothing to install (no Python, no uv, no git).

1. Download `sentence-gen-windows-<version>.zip` below and unzip it (e.g. to your Desktop).
2. Double-click **`sentence_gen.exe`**: it prints a sentence and creates **`sentences.toml`**
   with examples next to it. Edit that file with Notepad (keep it in UTF-8 so emoji come out right).
3. From a terminal or another program: `sentence_gen.exe --tag video`, `--no-emoji`,
   `-f other.toml`, `--check`; see `README.txt` in the folder.

Windows may say **"Windows protected your PC"** the first time: click **More info → Run
anyway** (the app isn't signed with a paid certificate). Check the download with the
`.sha256` file: `Get-FileHash sentence-gen-windows-<version>.zip` in PowerShell must show the
same value.

**Updating:** unzip the new version over the old folder; your `sentences.toml` is kept.

Third-party licenses: the `LICENSES` folder in the zip.
