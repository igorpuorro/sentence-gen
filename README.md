# sentence-gen

Prints one sentence built from the templates in `sentences.toml`, with random word choices,
optional parts and emojis. Standard library only (Python 3.11+).

```bash
uv run sentence_gen.py                  # one sentence
uv run sentence_gen.py -f minhas.toml   # another template file
uv run sentence_gen.py --tag video      # only sentences tagged "video"
uv run sentence_gen.py --no-emoji       # no emojis
uv run sentence_gen.py --seed 42        # same output for the same seed
uv run sentence_gen.py --check          # validate the file, print one expansion per sentence
```

## Template syntax

| Marker | Meaning | Example |
|---|---|---|
| `{slot}` | random item from `[slots]` | `{saudacao}` → `Bom dia` |
| `{a\|b\|c}` | one of the options; an empty one means "nothing" | `{muito\|super\|}` |
| `[text]` | the text half the time | `[de verdade]` |
| `{:pool}` | one emoji from that `[emojis]` pool, at that spot | `{:amor}` → `😍` |

Markers nest (`[{muito|super}] {adj}`), and slot items may contain markers too.
Each `[[sentences]]` entry has `text` and optionally `emojis` (pools for the trailing emojis;
all pools if omitted), `weight` (default 1) and `tags`. `[settings]` sets `emoji_chance`
and `max_emojis` for the trailing emojis. The output gets its spaces tidied, no space before
punctuation, and a capital first letter.

Only `sentences.toml` is tracked in git; any other `*.toml` template file in this folder
is ignored (see `.gitignore`), so your own template files stay local.

## Windows app

For people without Python or uv: download `sentence-gen-windows-<version>.zip` from the
[Releases](https://github.com/igorpuorro/sentence-gen/releases) and unzip it. The folder has
`sentence_gen.exe` (plus `_internal/`, built with PyInstaller), `minhas_frases.bat`,
`README.txt` and `LICENSES/`.

- Started for the first time without `-f`, the exe creates `sentences.toml` next to itself from
  the bundled example. The zip doesn't contain it, so unzipping an update over the folder keeps
  the user's own.
- `-f NAME` looks in the current folder, then next to the exe.
- Double-clicked, the exe waits for Enter before its window closes; run from a terminal or
  another program, it doesn't. Output is UTF-8.

### minhas_frases.bat: your own template file, from any folder

Programs that take one command without options (e.g. feed_autoplay's `--comment-script`)
can't pass `-f`. `minhas_frases.bat` does it for them: it runs `sentence_gen.exe -f minhas.toml`
with full paths taken from its own location (`%~dp0`), so it works whatever the current folder.

1. Run `sentence_gen.exe` once (double-click) so it creates `sentences.toml`, then copy that to
   `minhas.toml` in the same folder and edit it (Notepad, UTF-8).
2. Call the `.bat` by its full path. Options after it go to the exe:

   ```bat
   "C:\Users\me\Desktop\sentence-gen\minhas_frases.bat"
   "C:\Users\me\Desktop\sentence-gen\minhas_frases.bat" --tag video --no-emoji
   ```

   From another program, e.g. feed_autoplay's `settings.txt`:

   ```text
   --comment-script C:\Users\me\Desktop\sentence-gen\minhas_frases.bat
   ```

   Or capture the sentence in a script:

   ```bat
   for /f "delims=" %%s in ('call "C:\Users\me\Desktop\sentence-gen\minhas_frases.bat"') do set "FRASE=%%s"
   ```

   ```powershell
   $frase = & "C:\Users\me\Desktop\sentence-gen\minhas_frases.bat"
   ```

- It prints only the sentence, and passes on the exe's exit code (1 on errors). Without
  `minhas.toml` it says so on stderr and exits with 1.
- More template files: copy the `.bat` under another name and change `minhas.toml` in it.
  To keep the `.bat` elsewhere (e.g. a folder on PATH), set `SG_DIR` in it to the
  `sentence-gen` folder.
- An update replaces `minhas_frases.bat`: keep your own changes in a copy with another name.

### Building

```bash
uv run --group build packaging/build.py   # → build/sentence-gen-<windows|linux>-<version>.zip + .sha256
```

`packaging/build.py` runs PyInstaller (`packaging/sentence_gen.spec`), adds the files in
`packaging/windows/` (`README.txt`, `minhas_frases.bat`) and `LICENSES/`, self-checks the app
from another folder, makes sure no template file other than the bundled example is inside,
then zips it. On Linux it builds the same bundle for Linux, to test the bundling without a
Windows PC.

**Releases:** set the new version in `pyproject.toml` and `__version__` in `sentence_gen.py`,
commit, then push a tag `v<version>`. GitHub Actions (`.github/workflows/windows-release.yml`)
builds on Windows and publishes a Release with the zip, its `.sha256` and
`packaging/release-notes.md`. Run by hand (Actions → windows-release → Run workflow), it only
builds; the zip is the run's artifact.
