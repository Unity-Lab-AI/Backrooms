# -*- coding: utf-8 -*-
"""Rebuild the subject-guard claim so its needle cannot be mangled by an escape.

The claim's needle was written as a normal single-quoted Python string containing `r"\\b"`. Inside a
non-raw string, `\\b` is the **backspace** escape, so the needle evaluated to a control character
and could never match the source. That is the third time one backslash has broken this one line --
once in the checker as a doubled backslash, once as a real backspace, and now in the claim meant to
guard it.

So the two characters are assembled from `chr(92)` at run time, where no literal and no shell can
reach them.
"""
import io
import sys

PATH = ".local/register/proof-public-export.py"
BS = chr(92)

OLD = ("      'if not any(re.search(r\"" + BS + "b\" + subject + r\"" + BS + "b\", lowered)'"
       " in conform_code" + chr(10)
       + '      and "for subject in DEPENDENCY_SUBJECTS)" in conform_code,')

NEW = (
    "      # **THE NEEDLE IS BUILT FROM chr(92), NOT WRITTEN AS AN ESCAPE.** Written as a normal"
    + chr(10) +
    "      # string, r\"\\b\" inside it is the BACKSPACE escape, so the needle became a control"
    + chr(10) +
    "      # character and could never match. One backslash has now broken this single line three"
    + chr(10) +
    "      # times: doubled in the checker (making the rule a no-op), a real backspace in the"
    + chr(10) +
    "      # repair, and an escape in the claim written to guard it."
    + chr(10) +
    "      ('if not any(re.search(r\"%sb\" + subject + r\"%sb\", lowered)'"
    + chr(10) +
    "       % (chr(92), chr(92))) in conform_code" + chr(10)
    + '      and "for subject in DEPENDENCY_SUBJECTS)" in conform_code,')

text = io.open(PATH, encoding="utf-8").read()
if OLD not in text:
    print("old claim text not found; check by hand")
    sys.exit(1)
io.open(PATH, "w", encoding="utf-8", newline=chr(10)).write(text.replace(OLD, NEW, 1))
print("needle rebuilt from chr(92)")
