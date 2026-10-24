@echo off
rem Prints one sentence from minhas.toml with sentence_gen.exe -- from any folder, for any
rem program that runs it and reads its output (e.g. feed_autoplay's --comment-script).
rem
rem It is in the sentence-gen folder, next to sentence_gen.exe. Make minhas.toml there (copy
rem sentences.toml and edit it), then call this file by its full path:
rem   "C:\Users\me\Desktop\sentence-gen\minhas_frases.bat"
rem   "C:\Users\me\Desktop\sentence-gen\minhas_frases.bat" --tag video --no-emoji
rem Extra options are passed on to sentence_gen.exe. Keep the file elsewhere (e.g. in a
rem folder on PATH) by setting SG_DIR below to the sentence-gen folder instead.
rem
rem Nothing else may be printed: the caller takes all output as the sentence.
setlocal

rem the sentence-gen folder: by default the one this .bat is in (%~dp0 ends with "\")
set "SG_DIR=%~dp0"
rem set "SG_DIR=C:\Users\me\Desktop\sentence-gen\"

rem the template file: a full path, so the current folder doesn't matter
set "TEMPLATES=%SG_DIR%minhas.toml"
if not exist "%TEMPLATES%" (
    echo %TEMPLATES% not found: copy sentences.toml to minhas.toml and edit it 1>&2
    exit /b 1
)

"%SG_DIR%sentence_gen.exe" -f "%TEMPLATES%" %*
exit /b %errorlevel%
