# -*- coding: utf-8 -*-
"""Rewrite the two room-count comments that now name the old numbers.

The grid went 8 -> 9 and the ceiling 60 -> 80 on owner direction. Both constants carried doc
comments asserting the previous values -- `MaxRooms` *"unchanged at 60"* and a grid of *"64
slots"* -- which is the stale-comment defect this checkpoint has been cutting all day: a comment
is what somebody reads when they write a page.
"""
import io
import sys

NL = chr(10)
Q = chr(34)
PATH = "src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs"


def line(text):
    return "        /// " + text if text else "        ///"


OLD_BLOCK = NL.join([
    line("This also settles what looked like two contradictory directions. *" + Q
         + "leas than 60-100"),
    line("romms" + Q + "* asks for fewer, larger rooms and *" + Q
         + "FILL THE SPACE WITH ROOMS" + Q + "* asks for less"),
    line("bare rock — and they are **the same instruction**, because fewer larger rooms is what"),
    line("fills a fixed map. `MaxRooms` is unchanged at 60 and the grid is now 64 slots, so the"),
    line("room count is still the owner's number and the four slots over are what the sealed"),
    line("vaults are reserved from."),
    line(""),
    line("Deeper is still more rooms and tighter ones — 6, 7, then 8 — it simply stops before "
         "the"),
    line("point where another slot costs more rock than it adds room."),
])

NEW_BLOCK = NL.join([
    line("This also settles what looked like two contradictory directions. *" + Q
         + "leas than 60-100"),
    line("romms" + Q + "* asks for fewer, larger rooms and *" + Q
         + "FILL THE SPACE WITH ROOMS" + Q + "* asks for less"),
    line("bare rock — and they are **the same instruction**, because fewer larger rooms is what"),
    line("fills a fixed map."),
    line(""),
    line("**RAISED FROM 8 TO 9 AT 0.12.98-dev, on owner direction, and the measurement is why"),
    line("it was safe.** Asked whether the deep bands should reach the *" + Q + "60-100" + Q
         + "* they were"),
    line("originally specified at, the owner chose the middle: eighty. Nine slots is what affords"),
    line("it — eighty-one slots against a ceiling of eighty rooms, with the one over plus the"),
    line("sealed vaults coming out of the same budget."),
    line(""),
    line("**Measured over 200 seeds at seven depths before it was kept.** Depth 1 and 2 did not"),
    line("move at all, because their slot counts are below the ceiling either way; depth 3 went"),
    line("from 60 rooms to 63 and its room fill went **up**, 44.9% to 47.1%; depth 4 and deeper"),
    line("reach the full eighty at 42.6% fill, 2.3 points below where they were. `refused 0/200`"),
    line("and `fellback 0` at every band, degree rose from 5.22 to 5.49, and back-to-back pairs"),
    line("rose from 3,115 to 3,194."),
    line(""),
    line("**The cost is in the span, which is the honest trade:** the widest room at depth 4 and"),
    line("deeper falls from 62 cells to 54. That is *" + Q + "going deeping in can mean the "
         "numner of"),
    line("branch hallways and rooms distancing from the main portal spawn" + Q + "* arriving in "
         "the"),
    line("numbers — deeper is more rooms, smaller and tighter — and it is why the grand rooms"),
    line("and the shallow bands were left alone."),
    line(""),
    line("Deeper is still more rooms and tighter ones — 6, 7, 8, then 9 — and it still stops"),
    line("before the point where another slot costs more rock than it adds room: at ten the span"),
    line("had fallen to sixteen cells and fill measured 17.1%."),
])

OLD_CEILING = ("        /// <summary>The ceiling the owner named: *" + Q
               + "leas than 60-100 romms" + Q + "*.</summary>")

NEW_CEILING = NL.join([
    "        /// <summary>",
    line("The ceiling, and it is **eighty** since 0.12.98-dev."),
    line(""),
    line("The owner named *" + Q + "leas than 60-100 romms" + Q + "*; it sat at the bottom of "
         "that band"),
    line("at 60 and, asked directly, they chose the middle. Reached at depth 4 and deeper, where"),
    line("eighty-one slots are available; the shallow bands never approach it because their grids"),
    line("are smaller on purpose."),
    "        /// </summary>",
])


def main():
    text = io.open(PATH, encoding="utf-8-sig").read()
    for old, new, label in ((OLD_BLOCK, NEW_BLOCK, "slot-count reasoning"),
                            (OLD_CEILING, NEW_CEILING, "room ceiling")):
        if text.count(old) != 1:
            print("REFUSED (%d matches): %s" % (text.count(old), label))
            return 1
        text = text.replace(old, new, 1)
        print("rewrote: %s" % label)
    io.open(PATH, "w", encoding="utf-8-sig", newline=NL).write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
