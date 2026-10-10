# -*- coding: utf-8 -*-
"""The freeze-notice strings, one tone per shipped scenario.

Owner: *"i want u to make a universe of backrooms themed notcie of the pause
that is expected and propely keep it toned to the experience we are trying to
make per scenrio type"*, having given *"Time has froze due to mass distortions,
please wait"* and then said *"but noit that"*. So the sense survives -- time has
stopped, something enormous is the cause, waiting is correct -- and the words do
not.

Broken into paragraphs because `check-info-cards.py` refuses an unbroken wall of
text, which it caught once already on a 485-character gate description.
"""
import io
import sys

NL = chr(10)
PATH = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Generation.xml"

BR = "\\n\\n"

STRINGS = [
    ("RR_Generation_FreezeEvent",
     "Resolving a space that has not been indexed..."),

    ("RR_Generation_FreezeAcknowledge",
     "Understood — hold"),

    # The generic one. Any scenario this mod did not author a tone for still gets told the
    # pause is expected, which is the half of the direction that actually matters.
    ("RR_Generation_FreezeNotice",
     "THE HOLD IS EXPECTED" + BR
     + "A space on the far side is being resolved, and it is larger than anything here. "
     + "Until it finishes, nothing on this side advances: no clock, no movement, no answer "
     + "to anything you do." + BR
     + "This is not a fault and nothing has been lost. Wait for it. It ends."),

    # The company. It reads an instrument, because that is what the company does: the
    # interval is logged, billed, and has a name.
    ("RR_Generation_FreezeNotice_RR_AsyncIndustriesStart",
     "GATE CONNECTION — HOLD" + BR
     + "The aperture is resolving a coordinate that carries no index. Resolution is not "
     + "interruptible and it does not share the tick: while it runs, the company clock and "
     + "everything on it stops. You will see no movement and get no response." + BR
     + "This is expected. Async Industries records the interval as acquisition time and "
     + "bills it to the client." + BR
     + "The hold ends when the far side has a shape."),

    # The furniture store. Somebody's back room, and the stockroom is the wrong size.
    ("RR_Generation_FreezeNotice_RR_FurnitureStoreStart",
     "BACK DOOR — PLEASE WAIT" + BR
     + "Something behind the door is being measured out, and it is a great deal bigger than "
     + "the stockroom. Until the measuring is done, nothing in the shop moves. Not the "
     + "clock. Not the lights. Not you." + BR
     + "This happens every time a door opens onto somewhere new, and it has always "
     + "finished." + BR
     + "Stay where you are."),

    # Alone in the dark. No instrument, no company, no procedure -- and the last line is the
    # only reassurance available, which is that other people have stood here.
    ("RR_Generation_FreezeNotice_RR_SoloGroupStart",
     "IT IS TAKING A MOMENT" + BR
     + "The space past the threshold has not settled on what it is. While it settles, "
     + "nothing moves — not the air, not the light, not your own hands." + BR
     + "Time has not slowed down. It has stopped. It will start again and you will not have "
     + "aged a second." + BR
     + "Wait. Everyone who has gone through has waited here."),
]

text = io.open(PATH, encoding="utf-8-sig").read()
close = "</LanguageData>"
if text.count(close) != 1:
    print("cannot find the single closing tag in %s" % PATH)
    sys.exit(1)

for key, _ in STRINGS:
    if ("<" + key + ">") in text:
        print("key already present, refusing to duplicate: %s" % key)
        sys.exit(1)

block = ["", "  <!-- The generation freeze, told before it happens and toned per scenario.",
         "       Owner direction 2026-10-03: a notice of the pause that is expected, in the",
         "       universe's own voice. The example wording the owner gave was explicitly",
         "       rejected by the owner in the same sentence; the sense it carries is kept. -->"]
for key, value in STRINGS:
    block.append("  <" + key + ">" + value + "</" + key + ">")
block.append("")

at = text.rindex(close)
io.open(PATH, "w", encoding="utf-8", newline=NL).write(
    text[:at] + NL.join(block) + text[at:])
print("added %d keyed strings" % len(STRINGS))
