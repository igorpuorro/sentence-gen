# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print one sentence built from a template file, with random variations and emojis.

Template syntax (in sentences.toml):
    {slot}      random item from [slots]; slot items may contain markers too
    {a|b|c}     one of the listed options (an empty option is allowed: {muito|})
    [text]      the text half the time
    {:pool}     one emoji from that [emojis] pool, at that position
Markers nest: [{muito|super} {adj}]. Trailing emojis follow [settings] emoji_chance / max_emojis.

Usage:
    uv run sentence_gen.py [-f sentences.toml] [--tag TAG] [--no-emoji] [--seed N] [--check]
"""
import argparse
import random
import re
import sys
import tomllib
from pathlib import Path

DEFAULT_FILE = Path(__file__).with_name("sentences.toml")
INNERMOST = re.compile(r"\{[^{}\[\]]*\}|\[[^{}\[\]]*\]")  # a marker with no marker inside
REFERENCE = re.compile(r"\{(:?)([\w-]+)\}")  # {slot} or {:pool}
MAX_STEPS = 1000  # guards against slots that expand into themselves


def load(path):
    """Read the template file and return (settings, slots, emojis, sentences), or exit on errors."""
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        sys.exit(f"{path}: {e}")
    settings = {"emoji_chance": 0.7, "max_emojis": 2} | data.get("settings", {})
    slots, emojis, sentences = data.get("slots", {}), data.get("emojis", {}), data.get("sentences", [])

    errors = []
    if not sentences:
        errors.append("no [[sentences]]")
    for name, items in slots.items():
        if not items:
            errors.append(f"slot '{name}' is empty")
        for item in items:
            errors += check_refs(item, slots, emojis, f"slot '{name}'")
    for name, items in emojis.items():
        if not items:
            errors.append(f"emoji pool '{name}' is empty")
    for i, s in enumerate(sentences, 1):
        if "text" not in s:
            errors.append(f"sentence #{i}: no text")
            continue
        errors += check_refs(s["text"], slots, emojis, f"sentence #{i}")
        errors += [f"sentence #{i}: unknown emoji pool '{p}'" for p in s.get("emojis", []) if p not in emojis]
    if errors:
        sys.exit("\n".join(f"{path}: {e}" for e in errors))
    return settings, slots, emojis, sentences


def check_refs(text, slots, emojis, where):
    """Return errors for {slot} / {:pool} references in text that don't exist."""
    errors = []
    for is_pool, name in REFERENCE.findall(text):
        if is_pool and name not in emojis:
            errors.append(f"{where}: unknown emoji pool '{name}'")
        elif not is_pool and name not in slots:
            errors.append(f"{where}: unknown slot '{name}'")
    return errors


def expand(text, slots, emojis, rng, use_emoji=True):
    """Replace markers, innermost first, until none are left."""
    for _ in range(MAX_STEPS):
        m = INNERMOST.search(text)
        if not m:
            return text
        marker, inner = m.group(), m.group()[1:-1]
        if marker.startswith("["):
            value = inner if rng.random() < 0.5 else ""
        elif "|" in inner:
            value = rng.choice(inner.split("|"))
        elif inner.startswith(":"):
            value = rng.choice(emojis[inner[1:]]) if use_emoji else ""
        else:
            value = rng.choice(slots[inner])
        text = text[: m.start()] + value + text[m.end() :]
    raise ValueError(f"still expanding after {MAX_STEPS} steps; does a slot refer to itself?")


def trailing_emojis(sentence, settings, emojis, rng):
    """Return 0..max_emojis distinct emojis from the sentence's pools (all pools if none listed)."""
    pool = sorted({e for name in sentence.get("emojis") or emojis for e in emojis[name]})
    if not pool or rng.random() >= settings["emoji_chance"]:
        return ""
    return "".join(rng.sample(pool, rng.randint(1, min(settings["max_emojis"], len(pool)))))


def tidy(text):
    """Collapse spaces, drop spaces before punctuation, capitalize the first letter."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:…])", r"\1", text).strip()
    return text[:1].upper() + text[1:]


def generate(sentence, settings, slots, emojis, rng, use_emoji=True):
    text = tidy(expand(sentence["text"], slots, emojis, rng, use_emoji))
    tail = trailing_emojis(sentence, settings, emojis, rng) if use_emoji else ""
    return f"{text} {tail}" if tail else text


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-f", "--file", type=Path, default=DEFAULT_FILE, help="template file (default: sentences.toml)")
    p.add_argument("--tag", help="only sentences with this tag")
    p.add_argument("--no-emoji", action="store_true", help="no emojis at all")
    p.add_argument("--seed", type=int, help="same output for the same seed")
    p.add_argument("--check", action="store_true", help="validate the file and print one expansion per sentence")
    args = p.parse_args()

    settings, slots, emojis, sentences = load(args.file)
    rng = random.Random(args.seed)
    if args.tag:
        sentences = [s for s in sentences if args.tag in s.get("tags", [])]
        if not sentences:
            sys.exit(f"no sentence has the tag '{args.tag}'")

    try:
        if args.check:
            for i, s in enumerate(sentences, 1):
                print(f"#{i}: {generate(s, settings, slots, emojis, rng, not args.no_emoji)}")
            print(f"{args.file}: ok, {len(sentences)} sentences")
            return 0
        sentence = rng.choices(sentences, weights=[s.get("weight", 1) for s in sentences])[0]
        print(generate(sentence, settings, slots, emojis, rng, not args.no_emoji))
    except ValueError as e:
        sys.exit(str(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
