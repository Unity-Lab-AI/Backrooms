#!/usr/bin/env python3
"""Click the actionable element with this exact label on the top window, from a fresh capture.

For the pages the bridge CAN enumerate -- every real window -- this is better than a pixel: the
id is scoped to the capture that produced it, and `start-scenario.click_label` captures and clicks
in one breath. `--list` prints what the top surface offers, so a label is copied rather than guessed.

Usage:
    python .local/qa/click-label.py --list
    python .local/qa/click-label.py "Load saved..."
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rr_start", os.path.join(HERE, "start-scenario.py"))
_start = importlib.util.module_from_spec(_spec)
sys.modules["rr_start"] = _start
_spec.loader.exec_module(_start)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    session = _start.Session()
    try:
        if argv[0] == "--list":
            for target, kind, label, actionable in _start.elements(session):
                if label:
                    print("  %-28s %-8s %s%s" % (target, kind, label[:70], "  [click]" if actionable else ""))
            return 0
        if argv[0] == "--labelled-after" and len(argv) > 2:
            # **In a Core file list the unlabelled button after a name is DELETE.** That is how
            # the owner's ideoligion file came one click from gone. The action for a row is its
            # labelled button -- "Load" -- and it is the first one carrying that label after the
            # row's name, never the first one on the window.
            found = _start.elements(session)
            wanted = argv[2].strip().lower()
            start = None
            for index, (_t, kind, label, _a) in enumerate(found):
                if kind == "label" and label.strip().lower() == argv[1].strip().lower():
                    start = index
                    break
            if start is None:
                print("no label %r on the top window" % argv[1])
                return 1
            for target, _kind, label, actionable in found[start + 1:]:
                if actionable and label.strip().lower() == wanted:
                    session.call("rimworld/click_ui_target", {"targetId": target, "timeoutMs": 15000})
                    print("clicked %r for %r via %s" % (argv[2], argv[1], target))
                    return 0
            print("no %r button after %r" % (argv[2], argv[1]))
            return 1
        if argv[0] == "--nth-after" and len(argv) > 2:
            # **A ROW IS LABEL, INFO ICON, THEN THE ROW ITSELF.** `--after` takes the first
            # actionable and on a recipe list that is the little `i`, which opens a description
            # instead of adding the bill. The index says which one is meant.
            found = _start.elements(session)
            wanted = argv[1].strip().lower()
            start = None
            for index, (_t, kind, label, _a) in enumerate(found):
                if kind == "label" and label.strip().lower() == wanted:
                    start = index
                    break
            if start is None:
                print("no label %r on the top window" % argv[1])
                return 1
            seen = 0
            for target, _kind, _label, actionable in found[start + 1:start + 12]:
                if not actionable:
                    continue
                seen += 1
                if seen == int(argv[2]):
                    session.call("rimworld/click_ui_target", {"targetId": target, "timeoutMs": 15000})
                    print("clicked actionable #%s after %r via %s" % (argv[2], argv[1], target))
                    return 0
            print("fewer than %s actionable elements follow %r" % (argv[2], argv[1]))
            return 1
        if argv[0] == "--after" and len(argv) > 1:
            # A Core page button is a label followed by an unlabelled button, the same shape as a
            # scenario row; `row_button` is that reading.
            found = _start.elements(session)
            target = _start.row_button(found, argv[1])
            if target is None:
                print("no button follows a label %r on the top window" % argv[1])
                return 1
            session.call("rimworld/click_ui_target", {"targetId": target, "timeoutMs": 15000})
            print("clicked the button after %r via %s" % (argv[1], target))
            return 0
        clicked = _start.click_label(session, argv[0])
        if clicked is None:
            print("no actionable element labelled %r on the top window" % argv[0])
            return 1
        print("clicked %r via %s" % (argv[0], clicked))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
