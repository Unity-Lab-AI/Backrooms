#!/usr/bin/env python3
"""Start a NEW colony on a named scenario, driving RimWorld's own new-game pages.

Owner direction, 2026-10-06, verbatim:

    "okay u fucking play the game and restart the scenerios as needed to test whats needed"

and, when I reached for a saved game instead:

    "do not load old saves ... stasart new fucking colonoly scenerios that we need to test"

and, when I started RimWorld's built-in quick-test colony instead:

    "wtf? u started a gamer thats not even one of the scenerios"
    "the button you are looking for is new colony on the main menu"

**Both corrections were right and both were mine.** A save from 2026-10-02 was built by an older
package and tests nothing about today's; and the built-in quick test has **no Rimrooms branch at
all**, which the gizmo list proved on the spot -- nine gizmos on a spawned door and not one of
ours, because `Set Gate` needs a company that a quick-test colony never creates.

## Why this exists rather than a sequence of hand-clicks

**A target id is scoped to the capture that produced it.** `get_ui_layout` stamps every id with an
incrementing capture number -- `ui-element:7:1:59` becomes `ui-element:8:1:59` on the next call --
so a plan written from one capture and clicked from the next is clicking a stale handle. Capture and
click have to happen together, which is a loop rather than a list of commands.

## The main menu cannot be clicked, and that is why this opens a page directly

`get_ui_layout` captures "dialogs, windows, main tabs, the inspect strip, or the gizmo grid". The
main menu is none of those: RimWorld draws it from the entry UI root, outside the window stack, so
neither it nor `get_screen_targets` can see the **New colony** button. `rimbridge/run_lua` does not
help either -- it is a lowered subset that orchestrates these same capabilities and gives no
arbitrary access to game code.

**What New colony actually does is push `Page_SelectScenario`**, and `open_window_by_type` can push
that page itself. Same code path, same page, reached through the one door the bridge has.

Usage
-----
    python .local/qa/start-scenario.py --list
    python .local/qa/start-scenario.py "Async Industries"
    python .local/qa/start-scenario.py "Async Industries" --save RRQA-async-fresh
"""
import argparse
import importlib.util
import os
import re
import socket
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))

_spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
_bridge = importlib.util.module_from_spec(_spec)
sys.modules["rr_bridge"] = _bridge
_spec.loader.exec_module(_bridge)

# What each new-game page needs chosen before its Next will do anything, keyed on the window type.
#
# **A QA COLONY IS DELIBERATELY PEACEFUL AND RELOADABLE, and both choices are testing decisions
# rather than taste.** Threats are the one thing that can end a test colony before the thing under
# test ever happens -- a raid at hour two is not a finding about a gate frame -- and commitment mode
# would make a save-and-reload row impossible to run twice. Named here so a later reader sees the
# reason instead of a preference.
#
# Only labels that are missing are a problem: a page that already has a storyteller selected is left
# alone, which is why each entry is attempted and not required.
PAGE_CHOICES = {
    # owner, 2026-10-09: "not peace full you cheap skat community buiilder go back" -- Cassandra Classic on
    # Community builder, the same preset Marble Hollow runs, never Peaceful
    "RimWorld.Page_SelectStoryteller": ("Cassandra Classic", "Community builder", "Reload anytime mode"),
}

# **NOT EVERY PAGE ADVANCES WITH A BUTTON CALLED "Next".** `Page_CreateWorldParams` advances with
# **Generate**, and a driver that only knows "Next" reports *"no Next on this page"* and stops one
# step short of a world. Tried in order, so a page that has more than one of them still advances and
# an unknown page falls back to the common names rather than needing an entry here.
ADVANCE_LABELS = ("Next", "Generate", "Start", "Accept", "Continue")

ELEMENT = re.compile(
    r'"targetId":\s*"([^"]+)",\s*"kind":\s*"([^"]+)",\s*"source":\s*"([^"]*)",'
    r'\s*"label":\s*("[^"]*"|null)[^}]*?"actionable":\s*(true|false)', re.S)


class Session(object):
    """One bridge connection, with the two calls this driver needs."""

    def __init__(self):
        port, token = _bridge.endpoint()
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=_bridge.TIMEOUT)
        self.sock.settimeout(_bridge.TIMEOUT)
        self.buf = bytearray()
        _bridge.exchange(self.sock, self.buf, "session/hello",
                         {"token": token, "bridgeVersion": "RimroomsScenarioStart/1",
                          "platform": "windows", "launchId": str(uuid.uuid4())})

    def call(self, name, arguments=None):
        return _bridge.exchange(self.sock, self.buf, "tools/call",
                                {"name": name, "arguments": arguments or {}})

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def elements(session):
    """[(targetId, kind, label, actionable)] for the current top surface, freshly captured.

    Returned from a single capture so every id in the list belongs to the same generation.
    """
    import json
    payload = session.call("rimworld/get_ui_layout", {})
    raw = json.dumps(payload, ensure_ascii=False, default=str)
    found = []
    for target, kind, _source, label, actionable in ELEMENT.findall(raw):
        found.append((target, kind, label.strip('"'), actionable == "true"))
    return found


def row_button(found, name):
    """The actionable button belonging to the row labelled `name`, or None.

    A scenario row draws its title, then its description, then the invisible button covering the
    whole row. So the button is **the first actionable element after the label**, which is how the
    list reads on screen and does not depend on a fixed offset.
    """
    lowered = name.strip().lower()
    for index, (_target, kind, label, _actionable) in enumerate(found):
        if kind == "label" and label.strip().lower() == lowered:
            for target, _k, _l, actionable in found[index + 1:index + 6]:
                if actionable:
                    return target
    return None


def labelled(found):
    """Scenario-looking labels, for --list and for error messages that help."""
    out = []
    for target, kind, label, _actionable in found:
        if kind == "label" and label and len(label) < 44 and not label.endswith("."):
            out.append((target, label))
    return out


def click_label(session, label, timeout_ms=15000):
    """Click the actionable element whose own label is `label`, from a fresh capture.

    **Capture and click in one breath, because an id is scoped to its capture.** A plan written
    from one `get_ui_layout` and clicked after another is clicking a stale handle: the ids carry an
    incrementing capture number, so `ui-element:7:1:94` and `ui-element:11:1:94` are the same
    control through different generations and only the current one is live.

    Returns the id clicked, or None when no actionable element carries that label.
    """
    wanted = label.strip().lower()
    found = elements(session)
    for target, _kind, text, actionable in found:
        if actionable and text.strip().lower() == wanted:
            session.call("rimworld/click_ui_target",
                         {"targetId": target, "timeoutMs": timeout_ms})
            return target
    return None


def window_types(session):
    import json
    blob = json.dumps(session.call("rimworld/get_ui_state", {}), ensure_ascii=False, default=str)
    return re.findall(r'"type":\s*"([^"]+)"', blob)


def open_scenario_page(session):
    """A genuinely clean slate, then the scenario page.

    **`go_to_main_menu` does NOT clear the new-game page stack**, and three attempts in a row left
    `Page_SelectScenario`, `Page_SelectStoryteller` and `Page_CreateWorldParams` all open at once.
    `get_ui_layout` captures the top surface, so from the second attempt on the driver was reading
    and clicking a page it had not opened -- which is how a run reported *"Next did not change the
    page"* while sitting on a world-params page left over from the attempt before.

    So every page window is closed explicitly until the stack stops shrinking. Bounded rather than
    `while True`, because a window that refuses to close must end the run rather than spin.
    """
    session.call("rimworld/go_to_main_menu", {})
    time.sleep(5.0)
    for _ in range(12):
        open_pages = [w for w in window_types(session) if ".Page_" in w]
        if not open_pages:
            break
        session.call("rimworld/close_window", {"windowType": open_pages[0].split(".")[-1]})
        time.sleep(0.8)
    leftover = [w for w in window_types(session) if ".Page_" in w]
    if leftover:
        print("start-scenario: could not clear the page stack: %s" % ", ".join(leftover))
        return False
    session.call("rimworld/open_window_by_type",
                 {"windowType": "Page_SelectScenario", "replaceExisting": True})
    time.sleep(2.5)
    return True


def press_next(session, attempts=3):
    """Advance a new-game page. `press_accept` is RimWorld's own Next/Accept action."""
    for _ in range(attempts):
        result = session.call("rimworld/press_accept", {})
        if isinstance(result, dict) and result.get("success"):
            time.sleep(2.0)
            return True
        time.sleep(1.0)
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("scenario", nargs="?", help="exact scenario name as the page shows it")
    parser.add_argument("--list", action="store_true", help="open the page and list what is on it")
    parser.add_argument("--save", help="save under this name once the colony is playable")
    # **The landing-tile page is the one step the bridge cannot drive, and `hands.py` can.** So a
    # run stops there, a screen pixel is clicked, and this picks the page loop back up from
    # whatever new-game page is on top, without reopening the scenario list.
    parser.add_argument("--resume", action="store_true",
                        help="skip scenario selection and advance from the page that is open now")
    # Owner, 2026-10-07: the world is made at 300x300 and Spring from the world page's Advanced
    # settings, and the tile is chosen by reading the Terrain pane. Both are things to do ON a
    # page rather than a press of Next, so the driver can be told to stop when a page opens.
    parser.add_argument("--stop-at", help="stop as soon as the top window's type contains this text")
    args = parser.parse_args(argv)

    if not args.scenario and not args.list and not args.resume:
        parser.error("name a scenario, pass --list, or --resume")

    session = Session()
    try:
        if not args.resume:
            if not open_scenario_page(session):
                return 1
            found = elements(session)
            if not found:
                print("start-scenario: the scenario page captured no elements; is the bridge live?")
                return 1

            if args.list:
                print("scenarios on the page:")
                for target, label in labelled(found):
                    print("  %-22s %s" % (target, label))
                return 0

            button = row_button(found, args.scenario)
            if button is None:
                print("start-scenario: no row labelled %r. What the page actually offers:"
                      % args.scenario)
                for _target, label in labelled(found):
                    print("  %s" % label)
                return 1

            print("start-scenario: selecting %r via %s" % (args.scenario, button))
            session.call("rimworld/click_ui_target", {"targetId": button, "timeoutMs": 15000})
            time.sleep(2.0)

        # **`press_accept` does not advance these pages.** It reported *"Dispatched semantic
        # 'accept' input ... UI state did not change"*, because a new-game page's Next is an
        # ordinary text button rather than the window's accept action. So it is clicked by name.
        for page in range(12):
            before = window_types(session)
            if args.stop_at and before and args.stop_at in before[0]:
                print("start-scenario: stopped at %s as asked" % before[0])
                return 0
            # Satisfy whatever this page requires before asking it to advance.
            for choice in PAGE_CHOICES.get(before[0] if before else "", ()):
                if click_label(session, choice):
                    print("  chose %r" % choice)
                    time.sleep(1.5)
            clicked = None
            used = None
            for label in ADVANCE_LABELS:
                clicked = click_label(session, label)
                if clicked:
                    used = label
                    break

            # ## A PAGE THAT DRAWS INTO THE WORLD UI HAS NO CLICKABLE BUTTONS, AND accept IS THE
            # ## WAY THROUGH IT -- BUT ONLY WHEN IT IS THE TOP WINDOW
            #
            # `Page_SelectStartingSite` reports a **0x0 rect**, because it draws the globe and its
            # own bottom buttons through `WorldInterface` rather than as window content. So
            # `get_ui_layout` finds nothing to click, exactly as on the main menu.
            #
            # `press_accept` dispatches to the **window stack**, and `Page.OnAcceptKeyPressed` is
            # what Next does. The first attempt reported *"UI state did not change"* -- and the
            # stack at that moment also held a `MapPreviewToolbar` and an `ImmediateWindow` **above
            # the page**, so the accept had somewhere else to land. Clearing everything that is not
            # the page first is the difference between dispatching at it and dispatching near it.
            if clicked is None:
                for window in window_types(session):
                    if ".Page_" not in window:
                        session.call("rimworld/close_window",
                                     {"windowType": window.split(".")[-1]})
                        time.sleep(0.5)
                result = session.call("rimworld/press_accept", {})
                if isinstance(result, dict) and result.get("changed"):
                    clicked, used = "accept", "accept"
                else:
                    message = result.get("message", "") if isinstance(result, dict) else ""
                    print("  accept   -> no change (%s)" % message[:70])

            if clicked is None:
                print("start-scenario: nothing to advance %s with (tried %s); stopping rather "
                      "than guessing" % (before[0] if before else "this window",
                                         "/".join(ADVANCE_LABELS)))
                break
            time.sleep(3.0)
            # **World and map generation are LONG EVENTS and three seconds is not enough.** Pressing
            # Next on `Page_CreateWorldParams` starts world generation; the page looked unchanged
            # simply because it was still working. The bridge has a wait for exactly this, so the
            # driver asks instead of sleeping longer and hoping.
            try:
                session.call("rimbridge/wait_for_long_event_idle", {"timeoutMs": 300000})
            except SystemExit:
                pass            # No long event pending is not an error.
            after = window_types(session)
            print("  %-8s -> %s" % (used, after[0] if after else "(no window)"))
            if after == before:
                print("start-scenario: Next did not change the page; stopping rather than looping")
                break
            if not after:
                break
        print("start-scenario: window now: %s" % ", ".join(window_types(session) or ["(none)"]))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
