# These PNGs are historical. Do not read them as the current register.

**Row 1269, verbatim:** *"The register preview PNGs under `outputs/` depict the superseded
two-sheet layout. Not deleted — they are tracked artifacts and removing them is the owner's call —
but they must not be read as showing the current file."*

So this note exists instead of a deletion. **Nothing in this folder has been removed.**

## What is authoritative, and what is not

| File | Status |
|---|---|
| `Rimrooms_Async_Industries_294_Mod_Integration_Register.html` | **THE REGISTER.** Authoritative. `tools/register-query.py` reads this file and nothing else |
| `Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx` | not authoritative — kept as the original artifact |
| `*.png` | **historical previews of a superseded two-sheet layout** |
| `*.staged.inspect.ndjson` | an inspection record of the staged workbook, dated |

**The HTML is the register.** Not the xlsx, not these images, and not anybody's memory. That has
been the rule since 0.10.4-dev and it is the reason the register is queryable at all.

## Why the images are wrong rather than merely old

They show **two sheets**. Query the register today and it parses **295 rows** out of the HTML, and
the companion campaign workbook — the other spreadsheet in this repository — transcribes to
**five** sheets, not two. An image of a two-sheet layout is not a stale view of the current file;
it is a view of a different file.

## How to read the register instead

```
python tools/register-query.py families
python tools/register-query.py family <text>
python tools/register-query.py trace <code>        what applies to what you are building
python tools/register-query.py use <code>          how to use the mods bearing on a feature
python tools/register-query.py card <id|text>      one mod's full review card
```

`tools/make-readable-html.py` renders the project's own documents to
`outputs/readable/index.html`, and `tools/extract-economy-workbook.py` does for the campaign
economy workbook what was done for the register: a tracked source, a generator, and an HTML
output that says plainly that its figures are transcribed rather than verified.

**No game has ever been launched from this repository.** Nothing depicted anywhere in this folder
has been observed in play.
