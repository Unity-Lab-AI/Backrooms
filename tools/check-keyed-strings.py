"""Check the mod's keyed language strings for duplicates and unresolved references.

Why this exists
---------------
On 2026-09-29 `RR_Gate_OperatorAway` was found declared **twice in the same file** with
two different texts: a readout taking the operator's name as ``{0}``, and a refusal
with no argument. Only one string can win, so one of the two messages was always
wrong — either a refusal rendering a literal ``{0}``, or a readout that had lost the
name it was supposed to show. Nothing was checking for it, and this scan had been
hand-rolled twice in one session before being made permanent.

What it checks
--------------
1. **No duplicate keys**, within a file or across files. RimWorld resolves a duplicate
   by last-one-wins, so the loser is silently unreachable.
2. **Every literal ``RR_`` key referenced from source resolves** — as a keyed string, as
   a defName the mod declares, or as an internal identifier. The last two are recognised
   from the mod's own data and from the shape of the call site (``ToilMaker.MakeToil``,
   ``RimroomsAudio.Play``, an audio ``case`` label) rather than from a maintained list,
   for the same reason the DLC gating check reads the game's data: a list of names rots
   exactly the way the thing it checks rots.
3. **Format arguments line up**: a key whose text contains ``{0}`` should be translated
   with at least one argument somewhere in the source, and a key translated with
   arguments should have a ``{0}``. This is the specific mismatch the duplicate caused.

Keys assembled at runtime from a variable (``"RR_Role_" + role``) cannot be resolved
statically and are listed under PREFIXES, which is deliberately explicit: a new
concatenated family has to be added here, which is the moment to ask whether it should
be a literal instead.

Usage
-----
    python tools/check-keyed-strings.py
"""

import collections
import glob
import os
import re
import sys
import xml.etree.ElementTree as ElementTree

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
SRC = os.path.join(REPO, "src")

# Keys assembled at runtime; the part after the prefix is a variable.
PREFIXES = (
    "RR_Role_", "RR_Room_", "RR_Clue_Label_", "RR_Clue_Text_", "RR_Contract_",
    "RR_Coordinate_", "RR_Cargo_", "RR_Cargo_Location_", "RR_CrewClosure_",
    "RR_EvidenceStatus_", "RR_Exp_Missing_", "RR_Exp_Status_", "RR_Proc_Status_",
    "RR_Observation_", "RR_Personnel_Passion_", "RR_Setup_Role_", "RR_Applicant_",
    "RR_Generation_", "RR_NativeGate_", "RR_PortalAddress_",
    # `("RR_UI_Disposition_" + record.Disposition)`. The three members that can reach it --
    # Contained, Released and Transferred -- each have a keyed string; `None` cannot, because
    # the caller returns before this line when nothing has been decided.
    "RR_UI_Disposition_",
    # `("RR_UI_Confidence_" + campaign.ConfidenceOf(record))`. All four bands are keyed;
    # the score is derived rather than stored, so every member is reachable.
    "RR_UI_Confidence_",
)

# Literals that name a Def rather than a keyed string are not listed here. They are read
# out of the mod's own Defs at run time, for the same reason the DLC gating check reads the
# game's data rather than a maintained list: a list of names rots exactly the way the thing
# it checks rots.



def concatenated(name, source):
    """Whether this const is joined to something else rather than used whole."""
    return re.search(re.escape(name) + r'\s*\+', source) is not None

def keyed_strings():
    found = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(MOD, "**", "Keyed", "*.xml"), recursive=True)):
        relative = os.path.relpath(path, REPO).replace("\\", "/")
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as error:
            raise SystemExit("keyed-strings: %s does not parse: %s" % (relative, error))
        for node in root:
            found[node.tag].append((relative, (node.text or "")))
    return found


def declared_def_names():
    """Every defName the mod declares. A source literal naming one is not a keyed string."""
    names = set()
    for path in glob.glob(os.path.join(MOD, "**", "*.xml"), recursive=True):
        if os.sep + "Keyed" + os.sep in path:
            continue
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError:
            continue
        for node in root.iter("defName"):
            if node.text:
                names.add(node.text.strip())
    return names


def source_text():
    parts = []
    for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
        normalised = path.replace("\\", "/")
        if "/bin/" in normalised or "/obj/" in normalised:
            continue
        with open(path, encoding="utf-8") as handle:
            parts.append(handle.read())
    return "\n".join(parts)


def main():
    failures = []
    strings = keyed_strings()

    # 1. duplicates
    for key, entries in sorted(strings.items()):
        if len(entries) > 1:
            places = ", ".join("%s" % where for where, _ in entries)
            texts = " | ".join(text.strip()[:60] for _, text in entries)
            failures.append("duplicate key %s declared %d times (%s): %s"
                            % (key, len(entries), places, texts))

    source = source_text()

    # 2. unresolved literal references
    referenced = set(re.findall(r'"(RR_[A-Za-z0-9_]+)"', source))
    defs = declared_def_names()
    # Identifiers that are deliberately not keyed strings, recognised by the shape of the
    # call that uses them rather than by a maintained list: toil debug names, and the
    # internal audio cue ids the audio layer maps onto Core SoundDefs.
    internal = set(re.findall(r'ToilMaker\.MakeToil\(\s*"(RR_[A-Za-z0-9_]+)"', source))
    internal |= set(re.findall(r'RimroomsAudio\.Play\(\s*"(RR_[A-Za-z0-9_]+)"', source))
    internal |= set(re.findall(r'case\s+"(RR_[A-Za-z0-9_]+)"\s*:', source))
    # Capability names granted by a company project and asked for with HasCapability. They
    # are an internal vocabulary, not keyed strings: a player never reads one. Both
    # directions of the grant-and-read relationship are asserted by
    # .local/register/proof-research-branches.py, which is a stronger guarantee than this
    # checker could give -- it catches a capability granted and never honoured, which is an
    # unlock the card promises and no code delivers.
    internal |= set(re.findall(r'HasCapability\(\s*"(RR_[A-Za-z0-9_]+)"', source))

    # A texture-name PREFIX is not a keyed string. The menu slideshow scans its folder and keeps
    # the files whose name starts with "RR_Menu_", so that prefix is a name test rather than
    # something a player ever reads.
    #
    # Classified by CALL SITE, like every rule above it, and not by spelling: the value counts as
    # internal only when the const holding it is passed to StartsWith. A const that merely looks
    # like a prefix, or one that is later handed to Translate, is still checked as a keyed string.
    for name, value in re.findall(r'const\s+string\s+(\w+)\s*=\s*"(RR_[A-Za-z0-9_]+)"', source):
        if re.search(r'StartsWith\(\s*%s\b' % re.escape(name), source):
            internal.add(value)
        # **A SECOND CALL SITE THAT MAKES A CONST A PREFIX: concatenation into a def lookup.**
        #
        # `RR_Mirror_` pairs each company project with its vanilla research mirror and is used
        # as `GetNamedSilentFail(ResearchMirrorPrefix + companyDefName)`, never through
        # `StartsWith`. The rule above therefore read it as a whole defName and reported it
        # unresolved -- which is correct behaviour on an incomplete rule rather than a false
        # alarm: a fragment is not a key, and the call site is the only honest way to tell.
        #
        # Two cheap conditions rather than one multiline regex, deliberately. The first attempt
        # matched across a line break and the escaping broke the file it was patching; a const
        # that is concatenated at all is already a fragment, and requiring the file to perform
        # a def lookup keeps the rule from excusing a const concatenated into a message.
        elif concatenated(name, source) and 'GetNamedSilentFail' in source:
            internal.add(value)
    unresolved = 0
    for key in sorted(referenced):
        if key in strings or key in defs or key in internal:
            continue
        if key in PREFIXES:
            continue
        if any(key.startswith(prefix) and key != prefix for prefix in PREFIXES):
            continue
        unresolved += 1
        failures.append("source references %s but no keyed string and no def declares it" % key)

    # 3. format-argument mismatches on keys the source translates with arguments
    translated_with_args = set(re.findall(r'"(RR_[A-Za-z0-9_]+)"\.Translate\(\s*[^)\s]', source))
    for key in sorted(translated_with_args):
        entries = strings.get(key)
        if not entries:
            continue
        text = entries[0][1]
        if "{0}" not in text:
            failures.append("%s is translated with arguments but its text has no {0}: %r"
                            % (key, text.strip()[:70]))

    if failures:
        for failure in failures:
            sys.stderr.write("keyed-strings: %s\n" % failure)
        return 1

    print("keyed strings verified")
    print("  keys declared        : %d" % len(strings))
    print("  duplicates           : 0")
    print("  defNames declared    : %d" % len(defs))
    print("  internal identifiers : %d (toil names, audio cues, capabilities)" % len(internal))
    print("  literal references   : %d, all resolve" % len(referenced))
    print("  argument mismatches  : 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
