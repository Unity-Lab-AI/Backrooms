# -*- coding: utf-8 -*-
"""Author the normalization close-out strings, one per start, toned like the hold notices.

Owner direction, 2026-10-05, verbatim: *"the notice needs to appear before the map bagins to load
then close out with a normalization notice"*.

Each close-out answers its own hold notice in the same voice: the company bills the interval, the
shopkeeper counts the lights back on, the person alone checks their own hands. Written as the
other half of a pair rather than as a generic "done".
"""
import io
import sys

NL = chr(10)
PATH = ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Generation.xml")
ANCHOR = "  <RR_Generation_FreezeNotice_RR_SoloGroupStart>"

LINES = [
    "  <RR_Generation_NormalAcknowledge>Continue</RR_Generation_NormalAcknowledge>",

    "  <RR_Generation_NormalNotice>TIME HAS NORMALIZED" + chr(92) + "n" + chr(92) + "n"
    "The space resolved and the hold is over. Nothing on this side lost a second to it, and "
    "nothing of yours was left in the interval."
    "</RR_Generation_NormalNotice>",

    "  <RR_Generation_NormalNotice_RR_AsyncIndustriesStart>COORDINATE INDEXED — HOLD RELEASED"
    + chr(92) + "n" + chr(92) + "n"
    "The far side has a shape and now carries an index. The company clock is running again and "
    "the interval is on the client's invoice as acquisition time." + chr(92) + "n" + chr(92) + "n"
    "Nothing was lost and nobody aged. Operations is answering."
    "</RR_Generation_NormalNotice_RR_AsyncIndustriesStart>",

    "  <RR_Generation_NormalNotice_RR_FurnitureStoreStart>THE SHOP IS BACK"
    + chr(92) + "n" + chr(92) + "n"
    "The measuring finished. The clock is ticking, the lights are doing what lights do, and the "
    "back door leads somewhere that now stays where it was put." + chr(92) + "n" + chr(92) + "n"
    "It finished. It always has."
    "</RR_Generation_NormalNotice_RR_FurnitureStoreStart>",

    "  <RR_Generation_NormalNotice_RR_SoloGroupStart>IT HAS SETTLED"
    + chr(92) + "n" + chr(92) + "n"
    "The space decided what it is. The air moves, the light holds still, and your hands are your "
    "own again." + chr(92) + "n" + chr(92) + "n"
    "You did not age. Check anyway — everyone does."
    "</RR_Generation_NormalNotice_RR_SoloGroupStart>",
]


def main():
    text = io.open(PATH, encoding="utf-8-sig").read()
    if "RR_Generation_NormalNotice" in text:
        print("the close-out strings are already authored; nothing written")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    end = text.index(NL, at) + 1
    io.open(PATH, "w", encoding="utf-8-sig", newline=NL).write(
        text[:end] + NL.join(LINES) + NL + text[end:])
    print("authored %d close-out string(s)" % len(LINES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
