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
