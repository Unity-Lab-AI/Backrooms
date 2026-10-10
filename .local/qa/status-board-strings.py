# -*- coding: utf-8 -*-
"""Keyed strings for the compact status board, and retire the two line formats it replaced.

Owner: *"things can be shortend and more concise and dirrect with tools tips
would less cluter it making them all concise and accurate"*. The row is a
number and a label; the instruction is the tooltip, in full. Nothing was
shortened by dropping the condition it describes.
"""
import io
import os
import re
import sys

NL = chr(10)
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_GateSteps.xml"
SOURCE = "src/RimroomsAsyncIndustries/UI/OperationsGateSteps.cs"

ADD = [
    ("RR_Steps_Row", "{0}. {1}"),
    ("RR_Steps_TipDone", "{0}\\n\\nDone. {1}"),
    ("RR_Steps_TipToDo", "{0}\\n\\nNot done yet. {1}"),
]

# Replaced by the board. A keyed string nothing draws is a string somebody will later believe
# is on screen.
RETIRE = ["RR_Steps_Heading", "RR_Steps_LineDone", "RR_Steps_LineToDo"]

text = io.open(KEYED, encoding="utf-8-sig").read()
source = io.open(SOURCE, encoding="utf-8").read()

for key in RETIRE:
    if ('"' + key + '"') in source:
        print("refusing to retire %s: the source still draws it" % key)
        sys.exit(1)

removed = 0
for key in RETIRE:
    pattern = re.compile(r"[ \t]*<" + key + r">.*?</" + key + r">[ \t]*" + NL, re.S)
    text, count = pattern.subn("", text)
    removed += count

close = "</LanguageData>"
if text.count(close) != 1:
    print("cannot find the single closing tag")
    sys.exit(1)

block = ["", "  <!-- The compact status board. One row per system; the instruction is the row's",
         "       tooltip rather than a paragraph beside it. Owner 2026-10-04: \"with tools tips",
         "       would less cluter it making them all concise and accurate\". -->"]
added = 0
for key, value in ADD:
    if ("<" + key + ">") in text:
        continue
    block.append("  <" + key + ">" + value + "</" + key + ">")
    added += 1
block.append("")

at = text.rindex(close)
io.open(KEYED, "w", encoding="utf-8", newline=NL).write(text[:at] + NL.join(block) + text[at:])
print("added %d key(s), retired %d" % (added, removed))
