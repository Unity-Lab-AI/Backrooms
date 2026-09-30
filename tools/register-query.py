"""Read the mod integration register and answer questions about it from the command line.

Owner direction, 2026-09-29, verbatim: *"add a memory and a law to always check the registry
of mods before building something to see what if anything applies, and do this retro actively
dfor regress too"*.

The register is 294 reviewed rows in an HTML table, and the LAW now requires it to be
consulted **before** anything is built. A LAW that needs somebody to open a browser, scroll a
294-row table and eyeball a column is a LAW that gets skipped when it is inconvenient, which
is exactly when it matters. So it is queryable.

**The HTML is the register.** Not the xlsx, not the preview images, and not anybody's memory.

Usage
-----
    python tools/register-query.py families
    python tools/register-query.py family <text>     rows whose system family matches
    python tools/register-query.py find <text>       rows matching anywhere
    python tools/register-query.py row <id>          one row in full
    python tools/register-query.py traces            every trace code, with row counts
    python tools/register-query.py trace <code>      rows bearing on one feature, eg RR-OUT
    python tools/register-query.py card <id|text>    ONE MOD'S REVIEW CARD, every field
    python tools/register-query.py use <code>        HOW TO USE the mods bearing on a feature

The **trace** column is the one that answers the question the LAW asks -- *what applies to the
thing I am about to build* -- because it names the Rimrooms feature each row bears on rather
than the mod's own subject matter. It had no query until 0.12.20-dev, which made it the column
that got skipped. Codes in use: RR-COMPAT, RR-STA, RR-FAC, RR-EXP, RR-THREAT, RR-OUT, RR-ECO,
RR-DLC, RR-EVD, RR-MP, RR-UI, RR-GATE, RR-MSN, RR-STYLE, RR-SPACE, RR-SCEN.

The **card** is where the guidance actually is, and until 0.12.24-dev nothing could reach it.
The index table's own `card` column holds the words *"open card"* -- it is a hyperlink label,
not content. Every real instruction (**Planned Use**, **Integration Approach**, **Compatibility
Watch**, **FinalDisposition**) lives in the register's `#cards` section and in a per-mod review
record under `docs/research/reviews/mods/`, and the LAW says to read them:

    *"filter the register by system family before designing, read the per-mod reviews it points
    at, and state in the implementation record what was checked and what applied"*

A LAW that points at a document the tool cannot open is a LAW that gets satisfied by reading
four short columns and calling it consulted. `use <code>` is the query the LAW actually
describes: for every mod bearing on the feature being built, it prints how this mod is
supposed to use it.
"""

import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLUMNS = ["load", "mod", "family", "stance", "firmness", "trace", "card"]


def register_path():
    found = glob.glob(os.path.join(REPO, "outputs", "**", "*Register.html"), recursive=True)
    if not found:
        raise SystemExit("register HTML not found under outputs/")
    return sorted(found)[-1]


def strip_tags(text):
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return " ".join(text.split())


def rows():
    html = io.open(register_path(), encoding="utf-8", errors="replace").read()
    found = []
    for match in re.finditer(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", match.group(1), re.S | re.I)
        if len(cells) < len(COLUMNS):
            continue
        values = [strip_tags(cell) for cell in cells[: len(COLUMNS)]]
        if values[0].lower() in ("load", ""):
            continue
        found.append(dict(zip(COLUMNS, values)))

    # The register HTML carries two tables over the same 294 mods with different column
    # layouts; the second puts a Steam workshop id where the system family belongs. Keeping
    # both would double every count and make a family filter miss half its rows, so the row
    # whose family reads as a family is the one kept.
    best = {}
    for row in found:
        key = row["load"].strip()
        family = row["family"].strip()
        usable = bool(family) and not family.isdigit()
        if key not in best or (usable and not best[key][1]):
            best[key] = (row, usable)
    return [pair[0] for pair in sorted(best.values(), key=lambda p: _order(p[0]["load"]))]


# The fields a card carries, in the order a card prints them. USE_FIELDS is the subset that
# answers "how is this mod supposed to be used by ours" -- the question the LAW asks -- and is
# deliberately short, because a query that dumps fourteen fields per mod across 149 rows is a
# query nobody runs twice.
USE_FIELDS = ["Backrooms Dependency", "Planned Use", "Integration Approach", "Compatibility Watch"]


def cards():
    """Every review card in the register, keyed by load number as an int.

    The cards are `<article id="mod-N">` blocks of `<dt>`/`<dd>` pairs. Parsed separately from
    the index table because the index cannot carry them: its `card` cell is the hyperlink that
    says "open card".
    """
    html = io.open(register_path(), encoding="utf-8", errors="replace").read()
    found = {}
    for match in re.finditer(r'<article[^>]*id="mod-(\d+)"[^>]*>(.*?)</article>', html, re.S | re.I):
        body = match.group(2)
        heading = re.search(r"<h3[^>]*>(.*?)</h3>", body, re.S | re.I)
        # The heading holds the index number, the workshop id, two pills and a back-link in
        # spans and anchors; the mod's own name is the text left once those are removed.
        name = strip_tags(re.sub(r"<span[^>]*>.*?</span>|<a[^>]*>.*?</a>", " ",
                                 heading.group(1) if heading else "", flags=re.S | re.I))
        fields = []
        for key, value in re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", body, re.S | re.I):
            fields.append((strip_tags(key), strip_tags(value)))
        found[int(match.group(1))] = {"name": name, "fields": fields}
    return found


def review_path(card):
    """The on-disk review record a card names, if it is really there."""
    for key, value in card["fields"]:
        if key.lower().startswith("reviewrecord"):
            candidate = os.path.join(REPO, value.replace("/", os.sep))
            return value, os.path.isfile(candidate)
    return None, False


def _order(load):
    try:
        return (0, int(load.strip()))
    except ValueError:
        return (1, 0)


def show(row, full=False):
    print("  [%s] %s" % (row["load"], row["mod"]))
    print("      family   : %s" % row["family"])
    print("      stance   : %s" % row["stance"][:160])
    print("      firmness : %s" % row["firmness"][:160])
    if full:
        print("      trace    : %s" % row["trace"])
        print("      card     : %s" % row["card"][:1200])


def main(argv):
    data = rows()
    if not data:
        raise SystemExit("no rows parsed; the register layout may have changed")
    if len(argv) < 2:
        print(__doc__)
        print("rows parsed: %d" % len(data))
        return 0

    command = argv[1].lower()

    if command == "traces":
        # The trace column names which Rimrooms feature a row bears on, and it is the column
        # that answers the question the LAW actually asks: "what applies to the thing I am about
        # to build". It had no query, so it was the column that got skipped.
        counts = {}
        for row in data:
            for code in re.findall(r"RR-[A-Z]{2,14}", row["trace"]):
                counts[code] = counts.get(code, 0) + 1
        print("rows parsed: %d" % len(data))
        for code in sorted(counts, key=lambda k: (-counts[k], k)):
            print("  %-14s %d" % (code, counts[code]))
        return 0

    if command == "families":
        counts = {}
        for row in data:
            for part in re.split(r"[;,/]| and ", row["family"]):
                part = part.strip().lower()
                if part:
                    counts[part] = counts.get(part, 0) + 1
        print("rows parsed: %d" % len(data))
        for name in sorted(counts, key=lambda k: (-counts[k], k)):
            print("  %-46s %d" % (name[:46], counts[name]))
        return 0

    needle = " ".join(argv[2:]).lower()
    if not needle:
        raise SystemExit("give something to search for")

    if command in ("card", "use"):
        detail = cards()
        if not detail:
            raise SystemExit("no review cards parsed; the register layout may have changed")

    if command == "card":
        # By load number when the argument is one, otherwise by name, so both
        # `card 4` and `card adaptive storage` work.
        wanted = needle.strip()
        if wanted.isdigit():
            keys = [int(wanted)] if int(wanted) in detail else []
        else:
            keys = [k for k in sorted(detail) if wanted in detail[k]["name"].lower()]
        if not keys:
            print("no card matching %r" % needle)
            return 1
        for key in keys:
            card = detail[key]
            print("  [%d] %s" % (key, card["name"]))
            for field, value in card["fields"]:
                print("      %-22s %s" % (field[:22], value))
            path, present = review_path(card)
            if path:
                print("      %-22s %s" % ("review on disk",
                                          "yes" if present else "MISSING -- the card names a file that is not there"))
            print("")
        return 0

    if command == "use":
        wanted = needle.strip().upper()
        hits = [r for r in data
                if wanted in re.findall(r"RR-[A-Z]{2,14}", r["trace"].upper())]
        if not hits:
            print("no rows bearing trace %r" % wanted)
            return 1
        print("%d mod(s) bearing on %s -- how this mod is to use them" % (len(hits), wanted))
        missing = 0
        for row in hits:
            try:
                key = int(row["load"].strip())
            except ValueError:
                continue
            card = detail.get(key)
            if card is None:
                missing += 1
                continue
            print("")
            print("  [%d] %s  (%s)" % (key, card["name"], row["stance"][:60]))
            for field, value in card["fields"]:
                if field in USE_FIELDS:
                    print("      %-22s %s" % (field[:22], value))
            path, present = review_path(card)
            if path and not present:
                print("      %-22s %s" % ("review on disk", "MISSING -- %s" % path))
        if missing:
            print("")
            print("  %d row(s) had no matching card" % missing)
        return 0

    if command == "family":
        hits = [r for r in data if needle in r["family"].lower()]
    elif command == "trace":
        # Matched as a whole code, so RR-OUT never also returns RR-OUTPOST-style codes and a
        # short code cannot quietly pull in a longer one it is a prefix of.
        wanted = needle.strip().upper()
        hits = [r for r in data
                if wanted in re.findall(r"RR-[A-Z]{2,14}", r["trace"].upper())]
    elif command == "find":
        hits = [r for r in data
                if any(needle in r[column].lower() for column in COLUMNS)]
    elif command == "row":
        hits = [r for r in data if r["load"].strip() == needle.strip()]
        for row in hits:
            show(row, full=True)
        return 0 if hits else 1
    else:
        raise SystemExit("unknown command %r" % command)

    print("%d row(s) matching %r" % (len(hits), needle))
    for row in hits:
        show(row)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
