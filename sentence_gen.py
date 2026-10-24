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
    sentence_gen.exe [same options]    (the Windows app, packaging/build.py)
"""
import argparse
import os
import random
import re
import shutil
import sys
import tomllib
from pathlib import Path

__version__ = "0.1.0"  # == pyproject.toml's version == the release tag (packaging/build.py checks)

FROZEN = getattr(sys, "frozen", False)  # the PyInstaller app
WINDOWS = os.name == "nt"
# the app keeps sentences.toml next to the exe, whatever the current folder; the copy bundled in
# _internal is the default it creates on first start (not in the zip itself, so unzipping an
# update over the folder keeps the user's own)
APP_DIR = Path(sys.executable).parent if FROZEN else Path(__file__).parent
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
DEFAULT_FILE = APP_DIR / "sentences.toml"
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


def find_file(path):
    """The template file as given, else the one of that name next to the app."""
    if path.exists() or path.is_absolute() or not (APP_DIR / path).exists():
        return path
    return APP_DIR / path


def create_default():
    """Windows app, first start: put the example sentences.toml next to the exe."""
    if FROZEN and not DEFAULT_FILE.exists():
        try:
            shutil.copy(BUNDLE_DIR / "sentences.toml", DEFAULT_FILE)
            print(f"created {DEFAULT_FILE} with example sentences: edit it with Notepad", file=sys.stderr)
        except OSError as e:
            print(f"couldn't create {DEFAULT_FILE}: {e.strerror or e}", file=sys.stderr)


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
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = p.parse_args()

    create_default()
    args.file = find_file(args.file)
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


def owns_console():
    """Windows app started by a double-click: the console window belongs to it alone (from a
    terminal or another program, they share it) -- then it must not close before it can be read."""
    if not (FROZEN and WINDOWS):
        return False
    try:
        import ctypes
        return ctypes.windll.kernel32.GetConsoleProcessList((ctypes.c_uint * 2)(), 2) <= 1
    except Exception:
        return False


def entry():
    """main(), with UTF-8 output (emojis on an old Windows console or into a pipe) and, in a
    double-clicked app's own window, a wait for Enter at the end, after errors too."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        code = main()
    except SystemExit as e:
        code = e.code
        if isinstance(code, str):  # sys.exit("message"): print it before the wait
            print(code, file=sys.stderr)
            code = 1
    if owns_console():
        try:
            input("\nPress Enter to close this window ")
        except EOFError:
            pass
    return code


if __name__ == "__main__":
    sys.exit(entry())
