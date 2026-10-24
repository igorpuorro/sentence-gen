sentence-gen for Windows
========================

sentence_gen.exe prints one sentence built from the templates in sentences.toml, with random
word choices, optional parts and emojis. Nothing to install.


1. First start
--------------
Double-click sentence_gen.exe. It prints a sentence and creates sentences.toml next to it,
with example templates in Brazilian Portuguese. The window waits for Enter.
The first time, Windows may say "Windows protected your PC": click "More info", then
"Run anyway" (the app isn't signed with a paid certificate).


2. Your own sentences
---------------------
Open sentences.toml with Notepad and keep it in UTF-8 (Notepad: Save as, Encoding UTF-8) so
emoji come out right. Each [[sentences]] entry is one template:

  [[sentences]]
  text   = "{saudacao}! Esse video ficou {adj} [de verdade]"
  emojis = ["feliz", "fogo"]   (pools for the emojis at the end; all pools if left out)
  weight = 2                   (picked twice as often; 1 if left out)
  tags   = ["video"]           (for --tag)

Markers in the text:
  {slot}     a random item from [slots], e.g. {saudacao} -> Bom dia
  {a|b|c}    one of the options; an empty one means nothing: {muito|super|}
  [text]     the text half the time
  {:pool}    one emoji from that [emojis] pool, at that spot
Markers can be nested: [{muito|super}] {adj}. [settings] sets emoji_chance (chance of
emojis at the end) and max_emojis (how many at most).

You can keep several template files in this folder and pick one with -f.


3. From a terminal or another program
-------------------------------------
  sentence_gen.exe                     one sentence from sentences.toml
  sentence_gen.exe -f other.toml       another template file (as given, or in this folder)
  sentence_gen.exe --tag video         only templates tagged "video"
  sentence_gen.exe --no-emoji          no emojis
  sentence_gen.exe --seed 42           the same sentence for the same number
  sentence_gen.exe --check             check the file: one example per template, errors named

The sentence is printed in UTF-8. With feed_autoplay (android-instagram-tools) it can write
the comments: in its settings.txt, --comment-script with the full path of sentence_gen.exe.

minhas_frases.bat runs sentence_gen.exe with your own template file, minhas.toml, from any
folder -- for programs that take one command without options, like --comment-script:
  1. Copy sentences.toml to minhas.toml (in this folder) and edit it.
  2. Call the .bat by its full path, e.g. "C:\Users\me\Desktop\sentence-gen\minhas_frases.bat".
     Options after it go to sentence_gen.exe: minhas_frases.bat --tag video
Copy and rename it for more template files (change minhas.toml inside it with Notepad).


4. Updating
-----------
Unzip the new version over this folder: sentences.toml and your other template files are
kept. minhas_frases.bat is replaced: keep your own changes in a copy with another name.

Third-party licenses: the LICENSES folder.
