# -*- coding: utf-8 -*-
"""Plant a fault against every freeze-notice claim.

Built from a token for the literal backslash-n, because an escape written
through a shell heredoc has been mangled twelve times in this repo.
"""
import io
import sys

NL = chr(10)
BS_N = chr(92) + "n"
TOKEN = "@@NEWLINE@@"
PATH = ".local/register/plant-menu-slides.py"

NEW = '''
    # ------------------------------------------------------- the generation freeze, told in time
    ("THE NOTICE IS QUEUED AFTER THE FREEZE INSTEAD OF BEFORE IT", NOTICE,
     "            Find.WindowStack.Add(new Dialog_RimroomsGenerationNotice(NoticeText(), () =>@@NEWLINE@@"
     "                LongEventHandler.QueueLongEvent(work, LongEventKey, false, null)));",
     "            work();"),

    ("the work stops running inside a long event, so the freeze is unexplained again", NOTICE,
     "                LongEventHandler.QueueLongEvent(work, LongEventKey, false, null)));",
     "                work()));"),

    ("THE NOTICE FIRES ON EVERY CROSSING, so it becomes the nuisance instead of the warning",
     NOTICE,
     "            return coordinate != null && coordinate.Site == null;",
     "            return coordinate != null;"),

    ("and it stops firing at all, because a re-entry test swallows a first build", NOTICE,
     "            return coordinate != null && coordinate.Site == null;",
     "            return false;"),

    ("the pane stops announcing before the laboratory address is taken", PANE,
     "                Presentation.RimroomsGenerationNotice.Announce(opening, () =>@@NEWLINE@@"
     "                    ShowResult(PortalAddressService.RegisterLaboratoryAddress(opened, opening)));",
     "                ShowResult(PortalAddressService.RegisterLaboratoryAddress(opened, opening));"),

    ("THE BACKDROP STOPS BEING THE MOD'S OWN ART", NOTICE,
     "            backdrop = RimroomsSlideArt.RandomSlide();",
     "            backdrop = null;"),

    ("and the backdrop stops filling the screen", NOTICE,
     "                GUI.DrawTexture(RimroomsSlideArt.FullScreenRect(backdrop), backdrop,",
     "                GUI.DrawTexture(inRect, backdrop,"),

    # **THE WORST ONE, AND IT IS SILENT.** Unity's IMGUI state is process-wide. A leaked
    # zero-alpha `GUI.color` from any of 294 other mods makes a frameless full-screen window draw
    # nothing at all -- so the player sees a frozen game with no notice on it, which is the exact
    # failure the feature exists to prevent, arriving through the feature.
    ("THE WINDOW DRAWS WITH WHATEVER GUI STATE IT INHERITED", NOTICE,
     "            using (RimroomsWindowState.Clean()) { Draw(inRect); }",
     "            Draw(inRect);"),

    ("the per-scenario tone is gone, so every opening reads the same", NOTICE,
     "                if (scoped.CanTranslate()) { key = scoped; }",
     "                if (false) { key = scoped; }"),

    ("and the scenario is no longer consulted at all", NOTICE,
     "            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;",
     "            ScenPart_RimroomsStart part = null;"),

    ("THE COMPANY NOTICE LOSES THE WORDS THAT SAY THE PAUSE IS EXPECTED", KEYS,
     "This is expected.",
     "Something has gone wrong."),

    ("and the owner's rejected placeholder wording comes back", KEYS,
     "THE HOLD IS EXPECTED",
     "Time has froze due to mass distortions, please wait"),
]'''

text = io.open(PATH, encoding="utf-8").read()
problems = 0

old_paths = 'BACKGROUND = SRC + "/Presentation/RimroomsMenuBackground.cs"'
if text.count(old_paths) != 1:
    print("path block not found")
    problems += 1
else:
    text = text.replace(old_paths, old_paths + NL
                        + 'NOTICE = SRC + "/Presentation/RimroomsGenerationNotice.cs"' + NL
                        + 'PANE = SRC + "/UI/OperationsPortalNetwork.cs"' + NL
                        + 'KEYS = ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed"' + NL
                        + '        "/RR_Generation.xml")')

at = text.rfind(NL + "]" + NL)
if at == -1:
    print("plant list terminator not found")
    problems += 1
else:
    text = text[:at] + NEW.replace(TOKEN, BS_N) + text[at + len(NL + "]"):]

if problems:
    sys.exit(1)
io.open(PATH, "w", encoding="utf-8", newline=NL).write(text)
print("added %d notice plants" % NEW.count('    ("'))
