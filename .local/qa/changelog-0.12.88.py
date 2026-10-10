# -*- coding: utf-8 -*-
"""Prepend the 0.12.88-dev entry. Newest first, nothing above it rewritten."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"

ENTRY = """## 0.12.88-dev - 2026-10-04 - Everything down there has one exact thing wrong with it, and you can read it off the thing

- **The unnerving register reached people and events, which it never had.** Owner: *"remember
  lsd unnerving feeling with all things ie events random spanwns, enemies, allies, nuetrals,
  even all the crazy things ive mentioned in the past and anything u can find in the many many
  prep docs on the Backrooms Universe"*. The LSD direction had been read as an *architecture*
  direction for eight versions - bent corridors, seven room shapes, roads, neighbourhoods, a
  per-coordinate motif, all built - and none of it reached a single encounter, spawn or event.
  The owner's four-word version of that was *"zero weird events or people"*.
- **AND THE PREP DOCUMENTS HELD THE MECHANISM, not just atmosphere.**
  `docs/UNIVERSE_ADAPTATION.md`, written before any of this code existed: *"Ordinary industrial
  interiors become uncanny through exact changes ... a shifted doorway, impossible adjacency,
  repeated hall, changed room dimensions, or a feature that has moved since the last visit."*
  The uncanny is **one exact change to something ordinary** - a testable property, not a mood,
  and the reason the generator's floors already read while no encounter did.
- **So it is a gate now.** No inhabitant tell and no event trace may contain a mood adjective:
  eerie, creepy, unsettling, strange, weird, sinister, ominous, uncanny, disturbing, horrifying,
  terrifying. The lights going out is not uncanny; the switches being found already off is. That
  claim could not have been written without reading that file and it is the most useful thing in
  this batch.
- **A letter is not a tell, and that was the shared defect.** The announcements this package
  writes are good - the echo's reads *"{0} is standing in this space, wearing what they were
  wearing this morning. {0} is also at home right now"* - but they fire once and scroll away,
  and then the pawn was just a pawn and the event had never happened. All twelve inhabitant
  families carry a `tellKey` and all eight events a `traceKey`, both refused at load if absent,
  both read off the thing rather than out of a notification. The event trace is written **above**
  the letter's early return, so a letterless event still leaves a record.
- **Ally existed nowhere and now does.** `RR_Inhabitant_Helper` takes the crew's side against
  what else is in the space and **will not leave with them**. The help is Core's: an existing
  non-hostile faction and `LordJob_DefendPoint`, so they fight the psychotic families with
  ordinary AI. A new faction would have been the *"new type of np0c"* the owner forbade. An ally
  is the most unnerving of the three relations, not the friendliest - an attack is explicable.
- **Animals are something you find, not only something that chases you.** Two families from Core
  kinds, unfactioned and in no mental state. The tell-carrying comp had to be patched onto Core's
  `AnimalThingBase` for an animal to say anything at all, and the limit is recorded in the patch
  rather than hidden: a mod animal that does not inherit it reads its tell in the letter.
- **Radio fragments: the one event with a person in it.** The last open item in *"Add repeated
  missing-person mysteries with radio fragments ..."*. All seven events before it were
  environmental. What makes it worth shipping is whose voice it is - a colonist standing in the
  base right now, falling back to the lost-pawn register, and with neither there is no fragment
  at all. **And mentioning somebody must not resolve them**: `TakeLostPawnName` *removes* what it
  returns, so a non-destructive `LostPawnNames()` was added and a plant proves the destructive
  version fails.
- **Two coverage suites where there were none.** `proof-unnerving-register.py` is 35 claims and
  `plant-unnerving-register.py` reports **32 of 32 caught**. Three plants came back MISSED across
  this batch and **all three were claims being wrong rather than code**: one compared call
  positions when the property was *a missing letter key must not lose the record*, one matched the
  old code's exact line layout, one tested a comment.
- **Two stale rows closed by measurement rather than work.** *"fourteen historical gameplay PNGs
  still in the package allowlist"* - audited: the tree holds **thirteen** images and every one is
  accounted for, twelve menu slides and `About/Preview.png`. There is no gameplay art and no
  audio at all; the `Sounds` tree held one empty folder and zero files and has been removed, so
  the absence reads off the tree rather than off a document.

"""

text = io.open(PATH, encoding="utf-8").read()
if "## 0.12.88-dev" in text:
    print("already present")
    sys.exit(0)
head = "# Changelog" + NL + NL
if not text.startswith(head):
    print("CHANGELOG does not start with the expected heading; nothing written")
    sys.exit(1)
io.open(PATH, "w", encoding="utf-8", newline=NL).write(head + ENTRY + text[len(head):])
print("prepended the 0.12.88-dev entry (%d lines)" % (ENTRY.count(NL) + 1))
