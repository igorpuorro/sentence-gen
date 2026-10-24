# sentence-gen

Prints one sentence built from the templates in `sentences.toml`, with random word choices,
optional parts and emojis. Standard library only (Python 3.11+).

```bash
uv run sentence_gen.py                  # one sentence
uv run sentence_gen.py -f minhas.toml    # another template file
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

For people without Python or uv: `sentence_gen.exe` in a one-folder zip (the exe plus
`_internal/`, built with PyInstaller). Started for the first time without `-f`, it creates `sentences.toml`
next to the exe from the bundled example; the zip doesn't contain it, so unzipping an update
over the folder keeps the user's own. `-f NAME` looks in the current folder, then next to the
exe. A double-clicked exe waits for Enter before its window closes; run from a terminal or
another program (e.g. feed_autoplay's `--comment-script`), it doesn't. Output is UTF-8.

```bash
uv run --group build packaging/build.py   # → build/sentence-gen-<windows|linux>-<version>.zip + .sha256
```

`packaging/build.py` runs PyInstaller (`packaging/sentence_gen.spec`), adds
the files in `packaging/windows/` (`README.txt`, `minhas_frases.bat`) and `LICENSES/`, self-checks the app from another folder, makes
sure no template file other than the bundled example is inside, then zips it. On Linux it
builds the same bundle for Linux, to test the bundling without a Windows PC.

**Releases:** set the new version in `pyproject.toml` and `__version__` in `sentence_gen.py`,
commit, then push a tag `v<version>`. GitHub Actions (`.github/workflows/windows-release.yml`)
builds on Windows and publishes a Release with the zip, its `.sha256` and
`packaging/release-notes.md`. Run by hand (Actions → windows-release → Run workflow), it only
builds; the zip is the run's artifact.
