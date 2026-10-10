"""BRB countdown on the stream (owner: "update stream with a count down of the estimate time till back up").
Usage: brb-countdown.py <minutes>. Writes the end time to _brb_until; edit that file to move the estimate;
delete it to stop. Updates the BRB text every second."""
import os, sys, time
import obsws_python as o
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(HERE, "_brb_until")
if len(sys.argv) > 1:
    open(F, "w").write(str(int(time.time() + float(sys.argv[1]) * 60)))
c = None
while os.path.exists(F):
    try:
        until = int(open(F).read().strip())
        left = max(0, until - int(time.time()))
        h, m, sec = left // 3600, (left % 3600) // 60, left % 60
        eta = ("%d:%02d:%02d" % (h, m, sec)) if left > 0 else "any minute now"
        # the message sits in "BRB text", the ticking clock in its own big "BRB clock" (owner: "i dont see the
        # live clock in the stream")
        if c is None:
            c = o.ReqClient(host="127.0.0.1", port=4455, timeout=5)
            c.set_input_settings("BRB text", {"text": "Technical difficulties, honest version:\n"
                                                      "I am being trained to play RimWorld properly\n"
                                                      "and to talk to you like myself, not a script.\n\n"
                                                      "Back in about"}, True)
        c.set_input_settings("BRB clock", {"text": eta}, True)
    except Exception:
        c = None
    time.sleep(1)
