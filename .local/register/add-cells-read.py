# -*- coding: utf-8 -*-
"""Add a parameterised read-only cell-rect selector, so the live facility can be inspected.

Owner: *"look at the running game"*. The allowlist is parameterless by design, which is what keeps
it honest -- but it means nothing can answer *where are this player's generators and are they
running*. `rimworld/get_cells_info` is a read and takes a rect up to 1024 cells.

**Still read-only.** The rect comes from the command line, the tool only inspects, and the file's
premise is unchanged: it never discovers, starts, configures or controls a process.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT = os.path.join(REPO, "tools", "qa", "rimbridge_readonly.py")

OLD_ARG = u'''    parser.add_argument("--timeout", type=float, default=3.0, help="per-request timeout in seconds (1 to 10)")'''
NEW_ARG = u'''    parser.add_argument("--timeout", type=float, default=3.0, help="per-request timeout in seconds (1 to 10)")
    # A read of a bounded rectangle. Read-only like every other selector; parameterised because
    # "where are this player's generators" cannot be asked without coordinates.
    parser.add_argument("--rect", help="x,z,width,height to inspect with rimworld/get_cells_info "
                                       "(max 1024 cells)")'''

OLD_SEL = u'''    args = parser.parse_args(argv)'''
NEW_SEL = u'''    args = parser.parse_args(argv)
    if args.rect:
        try:
            rx, rz, rw, rh = (int(part.strip()) for part in args.rect.split(","))
        except ValueError:
            raise ClientError("--rect must be x,z,width,height")
        if rw < 1 or rh < 1 or rw * rh > 1024:
            raise ClientError("--rect must cover between 1 and 1024 cells")
        READ_TOOLS["cells"] = ("rimworld/get_cells_info",
                               {"x": rx, "z": rz, "width": rw, "height": rh})
        args.select = list(args.select or []) + ["cells"]'''

text = io.open(CLIENT, encoding="utf-8").read()
problems = []
for old in (OLD_ARG, OLD_SEL):
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:52]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
text = text.replace(OLD_ARG, NEW_ARG, 1).replace(OLD_SEL, NEW_SEL, 1)

# `--select` validates against a fixed choices tuple, so a runtime-added key has to be allowed.
OLD_CHOICES = u'''        choices=tuple(READ_TOOLS),'''
NEW_CHOICES = u'''        # `cells` is added at runtime by --rect, so it is named here rather than derived.
        choices=tuple(READ_TOOLS) + ("cells",),'''
if text.count(OLD_CHOICES) != 1:
    print("CHOICES ANCHOR PROBLEM: %d" % text.count(OLD_CHOICES))
    raise SystemExit(1)
text = text.replace(OLD_CHOICES, NEW_CHOICES, 1)
io.open(CLIENT, "w", encoding="utf-8", newline="").write(text)

after = io.open(CLIENT, encoding="utf-8").read()
failures = []
if u'"--rect"' not in after:
    failures.append("the rect argument was not added")
if u'READ_TOOLS["cells"] = ("rimworld/get_cells_info"' not in after:
    failures.append("the cells selector is not registered")
if u'rw * rh > 1024' not in after:
    failures.append("the 1024-cell bound is not enforced")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("read-only cell-rect selector added, bounded at 1024 cells")
