# -*- coding: utf-8 -*-
"""Two corrections to the stance classifier, both found by measuring rather than by reading.

1. **A false positive my own first fix introduced.** Scoping negation to a window before the word
   was not enough: row 288 Prison Labor says *"Pawn.IsColonist **requires** Faction.IsPlayer"* --
   a sentence about Core's source code, in a disposition whose actual claim is *"no Rimrooms
   dependency or adapter"*. Row 1055 predicted exactly three genuinely-required rows (1, 4, 14)
   and my fix gave four. The requirement question is about the disposition's **own claim**, which
   lives in its first sentence; everything after it is evidence and notes.

2. **The `Unclassified` fallback, which row 1055 also names.** Row 196 RimWorld Together -- the
   co-op backbone -- fell through to `Unclassified`, and so did row 2. Measured: those are the
   **only two** of 294. Both describe a planned use without asserting a requirement or an
   exclusion, which is what the register means by Optional everywhere else, so the fallback
   becomes Optional and the bucket empties.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "tools", "research", "build-mod-register.py")

s = io.open(PATH, encoding="utf-8").read()


def sub(old, new):
    global s
    assert s.count(old) == 1, "anchor count %d: %r" % (s.count(old), old[:70])
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ 1. first-sentence scoping
sub('''def requirement_is_asserted(lowered):
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
    words = lowered.replace("-", " ").split()''',
    '''def disposition_claim(lowered):
    """The sentence in which a disposition states what it is, with the notes cut off.

    A disposition is written as a claim followed by evidence. Row 288 Prison Labor reads
    *"no Rimrooms dependency or adapter; preserve this mod and vanilla prisoner controls;
    custody/UI interactions need testing."* and then goes on for three more sentences of Core
    source analysis, one of which contains *"Pawn.IsColonist **requires** Faction.IsPlayer"*.

    That sentence is about RimWorld's code, not about whether the mod is required, and scoping
    negation to a window before the word cannot tell the two apart -- there is no negator in
    front of it because nothing is being negated. **The requirement question is about the
    disposition's own claim**, so only the first sentence is asked.

    Splitting on ". " rather than "." keeps `Pawn.IsColonist` and `0.12.36-dev` in one piece.
    """
    head = (lowered or "").split(". ")[0]
    # A leading "provisional:" is the firmness axis, not part of the claim.
    return head.split("provisional:")[-1] if "provisional:" in head else head


def requirement_is_asserted(text):
    """Whether this disposition claims the mod is required.

    Row 1055. The classifier used to test `"required" in lowered`, and a negator before the word
    does not change that substring, so **14 of the 17 rows it called Required said the opposite**:
    "not required for materials/progression", "never a required input", "do not make it a required
    Rimrooms path".

    Negated occurrences are skipped rather than negative phrases being listed and checked first.
    A phrase list has to anticipate every way English negates something, and these dispositions
    take 104 distinct forms; asking "is this particular occurrence negated" is a question about
    the text in front of us instead.

    Asked of the claim alone -- see `disposition_claim` for why.
    """
    words = disposition_claim(text).replace("-", " ").split()''')

# ------------------------------------------------------------------ 2. the Unclassified fallback
sub('''    if ("no integration" in lowered or "no rimrooms patch" in lowered
            or "no rimrooms dependency" in lowered):
        return "No integration"
    return "Unclassified"''',
    '''    if ("no integration" in lowered or "no rimrooms patch" in lowered
            or "no rimrooms dependency" in lowered):
        return "No integration"
    # Row 1055 names this too: RimWorld Together, the co-op backbone, fell through to
    # "Unclassified" because its disposition describes a planned use without using any of the
    # words above. Measured across all 294 rows, it and row 2 were the ONLY two that fell
    # through, and both say the same thing -- in the profile, used, not required. That is what
    # Optional means everywhere else in this register, so it is what they are. A row with no
    # disposition at all is still Unrecorded, which is the honest bucket for silence.
    return "Optional"''')

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("stance classifier corrected twice")
