# -*- coding: utf-8 -*-
"""Teach `check-keyed-strings.py` the second call site that makes a const a prefix.

Written as a file rather than a nested heredoc because the regex involved needs backslashes and two
layers of Python escaping turned `\\r?\\n` into a real newline inside a string literal -- a
`SyntaxError` in the file being patched. The recorded rule is to use the editing tools for scripts;
this is the same lesson one level up.
"""
import io
import sys

NL = chr(10)
TARGET = "tools/check-keyed-strings.py"

BROKEN_START = "        # **A SECOND CALL SITE THAT MAKES A CONST A PREFIX"
ANCHOR = "            internal.add(value)"

BLOCK = [
    "        # **A SECOND CALL SITE THAT MAKES A CONST A PREFIX: concatenation into a def lookup.**",
    "        #",
    "        # `RR_Mirror_` pairs each company project with its vanilla research mirror and is used",
    "        # as `GetNamedSilentFail(ResearchMirrorPrefix + companyDefName)`, never through",
    "        # `StartsWith`. The rule above therefore read it as a whole defName and reported it",
    "        # unresolved -- which is correct behaviour on an incomplete rule rather than a false",
    "        # alarm: a fragment is not a key, and the call site is the only honest way to tell.",
    "        #",
    "        # Two cheap conditions rather than one multiline regex, deliberately. The first attempt",
    "        # matched across a line break and the escaping broke the file it was patching; a const",
    "        # that is concatenated at all is already a fragment, and requiring the file to perform",
    "        # a def lookup keeps the rule from excusing a const concatenated into a message.",
    "        elif concatenated(name, source) and 'GetNamedSilentFail' in source:",
    "            internal.add(value)",
]

HELPER = [
    "",
    "def concatenated(name, source):",
    '    """Whether this const is joined to something else rather than used whole."""',
    "    return re.search(re.escape(name) + r'\\s*\\+', source) is not None",
    "",
]


def main():
    text = io.open(TARGET, encoding="utf-8-sig").read()
    lines = text.split(NL)

    # Remove the broken insert if it is there.
    start = next((i for i, l in enumerate(lines) if l.startswith(BROKEN_START)), None)
    if start is not None:
        end = start
        while end < len(lines) and lines[end].strip() != "internal.add(value)":
            end += 1
        del lines[start:end + 1]
        print("removed the broken insert (%d lines)" % (end + 1 - start))

    # Insert after the StartsWith branch's own `internal.add(value)`.
    hits = [i for i, l in enumerate(lines) if l == ANCHOR]
    if len(hits) != 1:
        print("anchor matched %d time(s); refusing" % len(hits))
        return 1
    at = hits[0] + 1
    lines = lines[:at] + BLOCK + lines[at:]

    # The helper goes beside the other module-level functions.
    marker = next((i for i, l in enumerate(lines) if l.startswith("def ")), None)
    if marker is None:
        print("no module-level function to sit beside; refusing")
        return 1
    lines = lines[:marker] + HELPER + lines[marker:]

    io.open(TARGET, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    import ast
    ast.parse(NL.join(lines))
    print("patched and parses clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
