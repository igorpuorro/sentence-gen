# PyInstaller spec: sentence_gen as a one-folder app (sentence_gen.exe plus _internal/).
# Built by packaging/build.py -- on Windows for the release, on Linux to test the same bundle.
import re
import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent
VERSION = re.search(r'__version__ = "([^"]+)"', (ROOT / "sentence_gen.py").read_text(encoding="utf-8")).group(1)

# the example sentences.toml, copied next to the exe on first start (not in the zip itself, so
# unzipping an update over the folder keeps the user's own); listed by name, so no private
# template file from the project folder can get in
datas = [(str(ROOT / "sentences.toml"), ".")]


def version_info(name):
    """File properties of the exe (also a small plus for antivirus heuristics); Windows only."""
    if sys.platform != "win32":
        return None
    from PyInstaller.utils.win32.versioninfo import (FixedFileInfo, StringFileInfo, StringStruct,
                                                     StringTable, VarFileInfo, VarStruct, VSVersionInfo)
    nums = tuple(int(x) for x in VERSION.split(".")) + (0,)
    info = VSVersionInfo(
        ffi=FixedFileInfo(filevers=nums, prodvers=nums),
        kids=[StringFileInfo([StringTable("040904B0", [
                  StringStruct("ProductName", "sentence-gen"),
                  StringStruct("FileDescription", name),
                  StringStruct("FileVersion", VERSION),
                  StringStruct("ProductVersion", VERSION),
                  StringStruct("InternalName", name),
                  StringStruct("OriginalFilename", f"{name}.exe")])]),
              VarFileInfo([VarStruct("Translation", [1033, 1200])])])
    path = Path(workpath) / f"version_info_{name}.txt"
    path.write_text(str(info), encoding="utf-8")
    return str(path)


a = Analysis([str(ROOT / "sentence_gen.py")], pathex=[str(ROOT)], datas=datas, excludes=["tkinter"])
exe = EXE(
    PYZ(a.pure),
    a.scripts,
    [],
    exclude_binaries=True,  # one folder: the exe plus _internal/, nothing unpacked at start
    name="sentence_gen",
    console=True,
    upx=False,  # compressed exes are flagged by antivirus more often
    version=version_info("sentence_gen"),
)
# the zip's one top-level folder, named after the project
coll = COLLECT(exe, a.binaries, a.datas, name="sentence-gen", upx=False)
