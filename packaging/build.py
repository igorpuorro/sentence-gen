#!/usr/bin/env python3
"""Build the Windows app (sentence_gen.exe) as a one-folder zip.

  uv run --group build packaging/build.py

On Windows this makes the release zip (GitHub Actions runs it on every v* tag); on Linux it
builds the same bundle for Linux, to test the bundling without a Windows PC. Steps: PyInstaller
(packaging/sentence_gen.spec), add README.txt next to the exe, collect the third-party license
notices, self-check the app, check the contents, zip + SHA-256.
Output: build/sentence-gen-<windows|linux>-<version>.zip, everything in one folder sentence-gen/
"""
import hashlib
import importlib.metadata as md
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
WINDOWS = os.name == "nt"
PLATFORM = "windows" if WINDOWS else "linux"
# files next to the exe; sentences.toml is bundled instead: the app creates it on first start,
# so updates keep the user's own
EXTRAS = sorted((ROOT / "packaging" / "windows").iterdir())
# the only template file allowed in the bundle: private ones (see .gitignore) must never get in
ALLOWED_TOML = "_internal/sentences.toml"


def version():
    """The version, checked: pyproject.toml == sentence_gen.__version__ (== the tag on CI)."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    app = re.search(r'__version__ = "([^"]+)"', (ROOT / "sentence_gen.py").read_text(encoding="utf-8")).group(1)
    if project != app:
        sys.exit(f"version mismatch: pyproject.toml {project}, sentence_gen.py {app}")
    tag = os.environ.get("GITHUB_REF_NAME", "")
    if os.environ.get("GITHUB_REF_TYPE") == "tag" and tag != f"v{app}":
        sys.exit(f"tag {tag} doesn't match the version v{app}")
    return app


def collect_licenses(dest):
    """Third-party license notices: Python and PyInstaller's bootloader (no other packages ship)."""
    dest.mkdir()
    index = ["Third-party software in this folder and the licenses it is distributed under.", ""]
    dist = md.distribution("pyinstaller")
    files = [f for f in dist.files or [] if ".dist-info" in str(f)
             and re.search(r"LICEN[CS]E|COPYING|NOTICE", f.name, re.I)]
    if not files:
        sys.exit("no license file found for PyInstaller")
    for f in files:
        shutil.copy(f.locate(), dest / f"PyInstaller-{dist.version}-{f.name}")
    lic = dist.metadata.get("License-Expression") or dist.metadata.get("License") or "see files"
    index.append(f"PyInstaller {dist.version} (bootloader in sentence_gen.exe): {lic.splitlines()[0][:80]}")
    py = Path(sys.base_prefix)
    py_license = next((p for p in (py / "LICENSE.txt",
                                   py / "lib" / f"python{sys.version_info[0]}.{sys.version_info[1]}" / "LICENSE.txt")
                       if p.exists()), None)
    if not py_license:
        sys.exit("Python's LICENSE.txt not found")
    shutil.copy(py_license, dest / f"Python-{sys.version.split()[0]}-LICENSE.txt")
    index.append(f"Python {sys.version.split()[0]}: PSF License Agreement")
    (dest / "README.txt").write_text("\n".join(index) + "\n", encoding="utf-8")


def main():
    ver = version()
    app = BUILD / "dist" / "sentence-gen"
    shutil.rmtree(BUILD / "dist", ignore_errors=True)
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", str(BUILD / "dist"), "--workpath", str(BUILD / "work"),
                    str(ROOT / "packaging" / "sentence_gen.spec")], check=True)
    for f in EXTRAS:
        shutil.copy(f, app / f.name)
    collect_licenses(app / "LICENSES")

    # run from another folder: the app must find (and on the first run create) sentences.toml
    # next to the exe; the output must be UTF-8 even into a pipe (emojis)
    exe = app / ("sentence_gen.exe" if WINDOWS else "sentence_gen")
    for cmd in (["--version"], ["--help"], ["--check"], ["--seed", "1"], ["--tag", "video", "--no-emoji"]):
        print(f"$ {exe.name} {' '.join(cmd)}", flush=True)
        r = subprocess.run([str(exe), *cmd], check=True, stdin=subprocess.DEVNULL, cwd=BUILD,
                           capture_output=True)
        sys.stdout.write(r.stdout.decode("utf-8") + r.stderr.decode("utf-8"))
        if not r.stdout.strip():
            sys.exit(f"{exe.name} {' '.join(cmd)} printed nothing")
    if not (app / "sentences.toml").exists():
        sys.exit("the app didn't create sentences.toml next to the exe")

    (app / "sentences.toml").unlink()  # created by the checks; the app creates it on first start
    names = [p.relative_to(app).as_posix() for p in app.rglob("*")]
    bad = [n for n in names if n.endswith(".toml") and n != ALLOWED_TOML]
    if bad or ALLOWED_TOML not in names:
        sys.exit(f"unexpected template files in the bundle: {bad[:10]}" if bad else f"{ALLOWED_TOML} missing")

    zip_base = BUILD / f"sentence-gen-{PLATFORM}-{ver}"
    zip_path = Path(shutil.make_archive(str(zip_base), "zip", root_dir=app.parent, base_dir=app.name))
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    # "\n" line end on every system: `sha256sum -c` (Linux/macOS) fails on Windows' "\r\n"
    zip_path.with_suffix(".zip.sha256").write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8",
                                                    newline="\n")
    size = zip_path.stat().st_size / 1e6
    print(f"\n{zip_path.relative_to(ROOT)}  {size:.0f} MB  {len(names)} files  sha256 {digest[:16]}…")


if __name__ == "__main__":
    main()
