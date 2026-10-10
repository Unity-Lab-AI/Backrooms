# -*- coding: utf-8 -*-
"""Row 1055: `disposition_stance()` counts a NEGATED "required" as Required.

Fourteen of the seventeen rows the register called Required say the opposite in their own words --
row 88 *"not required for materials/progression"*, row 101 *"never a required input"*, row 259
*"do not make it a required Rimrooms path"*. The classifier tested `"required" in lowered` and a
negator before the word does not change that substring.

The fix strips every negated occurrence before the plain test, rather than adding a list of
negative phrases to check first: a phrase list has to anticipate every way English negates
something, and the register's dispositions take 104 distinct forms.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "tools", "research", "build-mod-register.py")

s = io.open(PATH, encoding="utf-8").read()

old = '''def disposition_stance(text):
    """Coarse bucket for what we actually do with a mod.

    The raw FinalDisposition strings take 104 distinct forms, which is useless as
    a filter. The order of these tests is the priority order: a row reading
    "required only for the selected co-op path; optional for solo play" is
    Required, not Optional.
    """
    lowered = (text or "").lower()
    if not lowered.strip():
        return "Unrecorded"
    if "required" in lowered:
        return "Required"'''

new = '''# Words that turn a nearby "required" into its opposite. Checked inside a short window before
# the word, because a disposition reading "optional; not required for progression" negates the
# second clause and not the sentence.
NEGATORS = ("not", "never", "no", "without", "isn't", "is not", "aren't", "are not",
            "rather than", "instead of", "avoid", "don't", "do not", "nor")

# How far back from a "required" a negator still applies. Eight words is enough for
# "do not make it a required Rimrooms path" and short enough that a negation about something
# else earlier in the sentence does not reach it.
NEGATION_WINDOW_WORDS = 8


def requirement_is_asserted(lowered):
    """Whether any occurrence of "required" in this text is a real requirement.

    Row 1055. The classifier used to test `"required" in lowered`, and a negator before the word
    does not change that substring, so **14 of the 17 rows it called Required said the opposite**:
    "not required for materials/progression", "never a required input", "do not make it a required
    Rimrooms path".

    Negated occurrences are stripped rather than negative phrases being listed and checked first.
    A phrase list has to anticipate every way English negates something, and these dispositions
    take 104 distinct forms; asking "is this particular occurrence negated" is a question about
    the text in front of us instead.
    """
    words = lowered.replace("-", " ").split()
    for index, word in enumerate(words):
        if "required" not in word and "requires" not in word:
            continue
        window = words[max(0, index - NEGATION_WINDOW_WORDS):index]
        joined = " " + " ".join(window) + " "
        if any((" " + negator + " ") in joined for negator in NEGATORS):
            continue
        return True
    return False


def disposition_stance(text):
    """Coarse bucket for what we actually do with a mod.

    The raw FinalDisposition strings take 104 distinct forms, which is useless as
    a filter. The order of these tests is the priority order: a row reading
    "required only for the selected co-op path; optional for solo play" is
    Required, not Optional.
    """
    lowered = (text or "").lower()
    if not lowered.strip():
        return "Unrecorded"
    if requirement_is_asserted(lowered):
        return "Required"'''

assert s.count(old) == 1, s.count(old)
io.open(PATH, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
print("disposition_stance fixed")
