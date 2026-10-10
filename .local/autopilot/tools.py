"""The autopilot's whole world: a fixed tool registry. If a capability is not in TOOLS, the model does not have it.

There is NO shell tool, NO generic file-write tool, NO build/compile/git tool, NO lua/script/debug bridge tool.
The only write the model can cause is a note inside .local/autopilot/scratch (guards.scratch_write). Scripts it can
run are a fixed list of absolute paths with typed, validated arguments, never a shell string.
"""
import base64
import importlib.util
import io
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
import uuid

import guards
from guards import GuardError

HERE = guards.HERE
ROOT = guards.ROOT
QA = os.path.join(ROOT, ".local", "qa")
CT = os.path.join(ROOT, ".claude", "tools")
STUDIO = os.environ.get("STUDIO_URL", "http://127.0.0.1:4317")
OUTBOX = os.path.join(ROOT, ".claude", ".studio-outbox.jsonl")
PY = sys.executable
SCRIPTS = {   # the ONLY scripts the autopilot ever runs; every one is an existing, owner-made stream/game tool
    "run_list": os.path.join(QA, "run-list.py"),
    "empire": os.path.join(QA, "empire.py"),
    "play": os.path.join(QA, "play.py"),
    "api_prio": os.path.join(QA, "api-prio.py"),
    "speak": os.path.join(CT, "unity-speak.py"),
    "glance": os.path.join(CT, "unity-glance.py"),
    "cam": os.path.join(CT, "unity-cam.py"),
    "snap": os.path.join(CT, "unity-snap.py"),
    "automate": os.path.join(QA, "automate.py"),                     # the mod's own command channel: no mouse, no screen
    "twitch": os.path.join(ROOT, ".local", "tw", "twitch-say.py"),  # the real Twitch chat, title, category
}
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # Windows consoles choke on emoji in model output
except Exception:
    pass
MOODS = ("chill", "hype", "angry", "focus", "laugh", "smug", "scared", "sad")


def log(*a):
    line = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(line, flush=True)
    try:
        guards.scratch_write("autopilot.log", line + "\n", append=True)
    except Exception:
        pass


# ---------------------------------------------------------------------------------------------------------------
# Bridge: one persistent session (same pattern as run-list.py / frontier.py)
# ---------------------------------------------------------------------------------------------------------------
class Bridge:
    def __init__(self, offline=False):
        self.offline = offline
        self.sock = None
        self.buf = bytearray()
        spec = importlib.util.spec_from_file_location("qa_bridge", os.path.join(QA, "bridge.py"))
        self.b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.b)

    def _connect(self):
        port, tok = self.b.endpoint()
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=60)
        self.buf = bytearray()
        self.b.exchange(self.sock, self.buf, "session/hello", {"token": tok, "bridgeVersion": "autopilot/1",
                                                               "platform": "windows", "launchId": str(uuid.uuid4())})

    def call(self, name, args=None):
        if self.offline:
            return {"offline": True, "note": "no bridge in --offline mode"}
        for attempt in range(2):
            try:
                if self.sock is None:
                    self._connect()
                r = self.b.exchange(self.sock, self.buf, "tools/call", {"name": name, "arguments": args or {}})
                r = r.get("result", r) if isinstance(r, dict) else r
                return r.get("structuredContent", r) if isinstance(r, dict) else r
            except (SystemExit, OSError, ValueError) as e:     # bridge.py raises SystemExit on bridge errors
                try:
                    self.sock and self.sock.close()
                except Exception:
                    pass
                self.sock = None
                if attempt:
                    return {"error": str(e)[:600]}
        return {"error": "bridge unavailable"}

    def schemas(self):
        """Input schemas of the allowlisted bridge tools, live if possible, else the cached copy."""
        listed = None
        if not self.offline:
            try:
                if self.sock is None:
                    self._connect()
                listed = self.b.exchange(self.sock, self.buf, "tools/list", {})
                listed = listed.get("tools", listed)
            except (SystemExit, OSError, ValueError):
                self.sock = None
        if not listed:
            listed = json.load(open(os.path.join(HERE, "bridge-tools.json"), encoding="utf-8"))
        return {t["name"]: t for t in listed if t.get("name") in guards.BRIDGE_ALLOWED}


def run_script(key, args, timeout=300, env_extra=None):
    """Run one of the fixed SCRIPTS with a list of already-validated string args. Never a shell."""
    path = SCRIPTS[key]
    env = dict(os.environ, **(env_extra or {}))
    try:
        p = subprocess.run([PY, path] + [str(a) for a in args], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, cwd=ROOT, env=env, shell=False)
        return (p.stdout or "")[-6000:] + (("\nSTDERR: " + p.stderr[-1500:]) if p.returncode else "")
    except subprocess.TimeoutExpired:
        return "timed out after %ds" % timeout


def _walk_targets(node, out):
    if isinstance(node, dict):
        tid = node.get("targetId") or node.get("id")
        label = " ".join(str(node.get(k) or "") for k in ("label", "text", "tooltip", "name")).strip()
        if node.get("targetId"):
            out[str(tid)] = label
        for v in node.values():
            _walk_targets(v, out)
    elif isinstance(node, list):
        for v in node:
            _walk_targets(v, out)


def _trim(obj, limit=5000):
    s = json.dumps(obj, ensure_ascii=False, default=str)
    s = re.sub(r"<color=[^>]*>|</color>", "", s)
    return s if len(s) <= limit else s[:limit] + " ...[truncated]"


# ---------------------------------------------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------------------------------------------
class Toolbox:
    def __init__(self, dry_run=False, offline=False, raw_voice=True):
        self.dry = dry_run or offline
        self.offline = offline
        self.raw_voice = raw_voice
        self.bridge = Bridge(offline=offline)
        self.bridge_schemas = self.bridge.schemas()
        self.ui_targets = {}          # targetId -> label, from the last get_ui_layout (click guard)
        self.last_gizmo_list = 0.0
        self.last_speech = 0.0
        self.pending_images = []      # base64 PNGs for the next model message (vision)
        self.spoken = []              # what was said this tick
        self.greeted_this_tick = set()
        self.local = self._local_tools()

    # -- tool specs for Ollama --------------------------------------------------------------------------------
    def specs(self):
        specs = []
        for name, t in sorted(self.bridge_schemas.items()):
            params = json.loads(json.dumps(t.get("inputSchema") or {"type": "object", "properties": {}}))
            for prop in (params.get("properties") or {}).values():   # keep the prompt small for a local model
                if isinstance(prop, dict) and len(prop.get("description", "")) > 110:
                    prop["description"] = prop["description"][:110]
            kind = "READ-ONLY" if name in guards.BRIDGE_READ else "GAME ACTION"
            specs.append({"type": "function", "function": {
                "name": self.ollama_name(name),
                "description": "[%s] %s" % (kind, (t.get("description") or name)[:180]),
                "parameters": params}})
        for name, (desc, params, _fn) in self.local.items():
            specs.append({"type": "function", "function": {"name": name, "description": desc, "parameters": params}})
        return specs

    @staticmethod
    def ollama_name(bridge_name):
        return bridge_name.replace("rimworld/", "game_").replace("rimbridge/", "bridge_")

    def _bridge_name(self, oname):
        for n in self.bridge_schemas:
            if self.ollama_name(n) == oname:
                return n
        return None

    # -- dispatch ----------------------------------------------------------------------------------------------
    def dispatch(self, oname, args):
        if not isinstance(args, dict):
            try:
                args = json.loads(args or "{}")
            except Exception:
                args = {}
        try:
            if oname in self.local:
                return self.local[oname][2](**args)
            bname = self._bridge_name(oname)
            if not bname:
                return "unknown tool %s -- you only have the listed tools" % oname
            return self._bridge(bname, args)
        except GuardError as e:
            log("GUARD", oname, e)
            return "REFUSED BY GUARD: %s" % e
        except TypeError as e:
            return "bad arguments for %s: %s" % (oname, e)
        except Exception as e:
            return "error in %s: %s" % (oname, str(e)[:400])

    def _bridge(self, name, args):
        args = guards.check_bridge(name, args)
        if name == "rimworld/click_ui_target":
            tid = str(args.get("targetId") or "")
            if tid not in self.ui_targets:
                raise GuardError("unknown ui target: call game_get_ui_layout first and click only a listed targetId")
            if guards.UI_NEVER.search(self.ui_targets[tid] or "") or guards.UI_NEVER.search(tid):
                raise GuardError("that button is off limits to the autopilot")
        if name == "rimworld/list_selected_gizmos":
            if time.time() - self.last_gizmo_list < guards.GIZMO_LIST_MIN_GAP_S:
                raise GuardError("gizmos were listed under 20 s ago; reuse that list (listing them repeatedly crashed the game)")
            self.last_gizmo_list = time.time()
        if self.dry and name not in guards.BRIDGE_READ:
            log("DRY-RUN would call", name, json.dumps(args))
            return "dry-run: not executed (%s %s)" % (name, json.dumps(args))
        log("CALL", name, json.dumps(args)[:300])
        r = self.bridge.call(name, args)
        if name == "rimworld/get_ui_layout" and isinstance(r, dict):
            found = {}
            _walk_targets(r, found)
            self.ui_targets = found
        if name == "rimworld/take_screenshot" and isinstance(r, dict) and r.get("path"):
            self._attach(r["path"])
            return "screenshot attached as an image for your next look"
        return _trim(r)

    def _attach(self, path):
        try:
            from PIL import Image
            im = Image.open(path).convert("RGB")
            im.thumbnail((1280, 1280))
            buf = io.BytesIO()
            im.save(buf, "PNG")
            self.pending_images = [base64.b64encode(buf.getvalue()).decode()]
        except Exception as e:
            log("image attach failed", e)

    # -- local tools -------------------------------------------------------------------------------------------
    def _local_tools(self):
        S = lambda props, req=(): {"type": "object", "properties": props, "required": list(req)}
        s, i, b = {"type": "string"}, {"type": "integer"}, {"type": "boolean"}
        return {
            "look": ("[READ-ONLY] Take a screenshot of the game exactly as the stream sees it and SEE it (vision).",
                     S({}), self.t_look),
            "game_state": ("[READ-ONLY] One-shot brief: colonists (map, position, job, drafted/downed/mental state), "
                           "letters, alerts, recent messages, UI window stack.", S({}), self.t_state),
            "pawn_check": ("[READ-ONLY-ish: selects the pawn] Select a colonist, open its Needs or Health tab and SEE it "
                           "so you can find the worst need/injury.",
                           S({"pawn": s, "tab": {"type": "string", "enum": ["Needs", "Health", "Gear", "Character"]}}, ["pawn"]),
                           self.t_pawn_check),
            "order_pawn": ("[GAME ACTION] Right-click order for one pawn at a cell through the in-game menu "
                           "(.local/qa/api-prio.py). Omit option to list the menu; option is a label prefix like "
                           "'Haul' or 'Prioritize'. queue=true adds after current orders.",
                           S({"pawn_id": s, "x": i, "z": i, "option": s, "queue": b}, ["pawn_id", "x", "z"]),
                           self.t_order_pawn),
            "play_slices": ("[GAME ACTION] Let the game run N x 10 s at Superfast (1-6) via play.py; it stops on any "
                            "letter or dialog that needs a decision and prints it.", S({"slices": i}, ["slices"]),
                            self.t_play),
            "run_list": ("[MAINTENANCE] Run the maintenance list (.local/qa/run-list.py). Prints OK/FIX lines; the "
                         "first FIX is your current goal. Note: it changes the selected pawn.", S({}), self.t_run_list),
            "empire_pass": ("[MAINTENANCE] One empire.py pass (stock orders, arms, self-tend, hunt, power and food "
                            "checks). report_only=true only reports.", S({"report_only": b}), self.t_empire),
            "say": ("[STREAM] Say a line out loud on stream in Unity's voice (TTS + overlay chat + an auto picture). "
                    "Clean only: no swearing, no degrading, no emoji, one to three short sentences.",
                    S({"text": s}, ["text"]), self.t_say),
            "reply_chat": ("[STREAM] Answer a Twitch viewer by name, out loud and in the overlay chat. chat_id is the "
                           "number given with their message.", S({"chat_id": i, "viewer": s, "text": s},
                                                                  ["chat_id", "viewer", "text"]), self.t_reply),
            "webcam": ("[STREAM] Re-render Unity's webcam with a mood and a short clean caption (raids, deaths, wins, "
                       "chat moments).", S({"mood": {"type": "string", "enum": list(MOODS)}, "caption": s},
                                           ["mood", "caption"]), self.t_webcam),
            "snap": ("[STREAM] Post an annotated screenshot of a map rect to the webcam panel with up to 3 circled "
                     "marks. Moves the camera to the rect.",
                     S({"x": i, "z": i, "w": i, "h": i, "caption": s,
                        "marks": {"type": "array", "items": {"type": "object", "properties": {"x": i, "z": i, "note": s}}}},
                       ["x", "z", "w", "h", "caption"]), self.t_snap),
            "read_doc": ("[READ-ONLY] Read a repo file for knowledge (docs/, src/, Mod/ ...). Reading only: you can "
                         "never edit, build or fix code. offset/limit are line numbers.",
                         S({"path": s, "offset": i, "limit": i}, ["path"]), self.t_read),
            "game_set": ("[GAME ACTION, NO MOUSE] Set a field directly through the mod's own automation channel -- works "
                         "with the window minimised. cmd is one of set_zone_plant (x,z,plant e.g. Plant_Rice), "
                         "set_zone_sowing (x,z,allow), set_work_priority (pawn,work,level 0-4), set_bed_owner "
                         "(x,z,owner colonist|prisoner|slave), add_bill (x,z,recipe e.g. CookMealSimple,count), "
                         "set_area (pawn,area label or empty). The result comes back from the game: read it.",
                         S({"cmd": {"type": "string", "enum": ["set_zone_plant", "set_zone_sowing", "set_work_priority",
                                                               "set_bed_owner", "add_bill", "set_area"]},
                            "x": i, "z": i, "plant": s, "allow": b, "pawn": s, "work": s, "level": i,
                            "owner": s, "recipe": s, "count": i, "area": s}, ["cmd"]), self.t_game_set),
            "twitch_chat": ("[STREAM] Type into the REAL Twitch chat (not just out loud). action: say | reply (needs "
                            "viewer) | title | category. Every line is filtered clean or refused.",
                            S({"action": {"type": "string", "enum": ["say", "reply", "title", "category"]},
                               "text": s, "viewer": s}, ["action", "text"]), self.t_twitch),
            "note": ("[SCRATCH] Write or append a note in your own scratch folder (the ONLY place you can write).",
                     S({"name": s, "text": s, "append": b}, ["name", "text"]), self.t_note),
        }

    def t_look(self):
        if self.dry:
            # take_screenshot writes a file in the game's folder, so dry-run reuses the last saved frame instead
            p = os.path.join(QA, "_w.png")
            if os.path.exists(p) and not self.offline:
                self._attach(p)
                return "dry-run: attached the last saved screenshot (.local/qa/_w.png)"
            return "dry-run: no screenshot"
        return self._bridge("rimworld/take_screenshot", {"suppressMessage": True})

    def t_state(self):
        out = {}
        for k, n, a in (("colonists", "rimworld/list_colonists", {}), ("letters", "rimworld/list_letters", {"limit": 15}),
                        ("alerts", "rimworld/list_alerts", {"limit": 20}), ("messages", "rimworld/list_messages", {"limit": 8}),
                        ("ui", "rimworld/get_ui_state", {})):
            r = self.bridge.call(n, a)
            if k == "colonists" and isinstance(r, dict):
                r = [{f: c.get(f) for f in ("pawnId", "name", "mapId", "position", "job", "drafted", "downed", "dead",
                                             "mentalState")} for c in r.get("colonists", [])]
            out[k] = r
        return _trim(out, 7000)

    def t_pawn_check(self, pawn, tab="Needs"):
        if self.dry:
            return "dry-run: would select %s, open the %s tab and look" % (pawn, tab)
        self._bridge("rimworld/select_pawn", {"pawnName": pawn})
        self._bridge("rimworld/open_inspect_tab", {"inspectTabId": tab})
        time.sleep(0.4)
        self.t_look()
        return "selected %s, %s tab open; the screenshot is attached -- read the bars and fix the worst one" % (pawn, tab)

    def t_order_pawn(self, pawn_id, x, z, option=None, queue=False):
        args = [str(pawn_id), str(int(x)), str(int(z))]
        if not re.fullmatch(r"[A-Za-z0-9_]{1,40}", args[0]):
            raise GuardError("pawn_id must be an id like Thing_Human1080")
        if option:
            if guards.UI_NEVER.search(option):
                raise GuardError("menu option refused by guard")
            args.append(str(option)[:60])
        if queue:
            args.append("--queue")
        if self.dry:
            log("DRY-RUN would run api-prio.py", args)
            return "dry-run: not executed"
        return run_script("api_prio", args, timeout=120)

    def t_play(self, slices=1):
        n = max(1, min(int(slices), 6))
        if self.dry:
            log("DRY-RUN would run play.py", n)
            return "dry-run: not executed"
        return run_script("play", [n], timeout=60 + 40 * n)

    def t_run_list(self):
        if self.dry:
            log("DRY-RUN would run run-list.py")
            return "dry-run: run-list.py not executed (it changes the selection); pretend the first FIX is the top goal in .claude/.stream-goals.json"
        return run_script("run_list", [], timeout=240)

    def t_empire(self, report_only=False):
        if self.dry:
            log("DRY-RUN would run empire.py", "--dry" if report_only else "")
            return "dry-run: not executed"
        return run_script("empire", ["--dry"] if report_only else [], timeout=300)

    # -- stream output: every path goes through guards.clean_for_stream -----------------------------------------
    def _speak(self, text, reply_to=None):
        clean = guards.clean_for_stream(text)
        if not clean:
            log("STREAM FILTER blocked:", repr(text)[:200])
            return None
        gap = time.time() - self.last_speech
        if gap < 3.0:
            time.sleep(3.0 - gap)
        self.last_speech = time.time()
        self.spoken.append(clean)
        if self.dry:
            log("DRY-RUN would SAY:", clean, "(reply to %s)" % reply_to if reply_to else "")
            return clean
        _outbox(clean, reply_to)
        if reply_to is None:
            # a picture with every narrated line (owner: "make some images more offten like as much as you talk")
            subprocess.Popen([PY, SCRIPTS["glance"], clean], cwd=ROOT, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, shell=False)
        subprocess.Popen([PY, SCRIPTS["speak"], "--bg", clean], cwd=ROOT, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, shell=False)
        log("SAID:", clean)
        return clean

    def t_say(self, text):
        said = self._speak(text)
        return ("said: " + said) if said else "BLOCKED by the stream filter (no swearing, no degrading, no emoji); say it cleaner"

    def t_reply(self, chat_id, viewer, text):
        name = guards.clean_viewer_name(viewer)
        if name and name.lower().split()[0] not in text.lower():
            text = name + ", " + text
        said = self._speak(text, reply_to=int(chat_id))
        if said:
            self.greeted_this_tick.add(str(viewer).lower())
            if not self.dry:
                try: run_script("twitch", ["reply", name or str(viewer), said], timeout=60)
                except Exception as e: log("twitch reply failed:", str(e)[:80])
        return ("replied: " + said) if said else "BLOCKED by the stream filter; reply cleaner"

    def t_game_set(self, cmd, **kw):
        """Owner, 2026-10-10: "fix that so it doesnt ever need the screen and MY DAMN MOUSE" / "build it into
        the mod if you have to". The component reads a command file once a second; the result is written back."""
        payload = {"cmd": cmd}
        for k, v in kw.items():
            if v is None or v == "": continue
            if k in ("pawn", "work", "owner", "area", "plant", "recipe") and not re.fullmatch(r"[A-Za-z0-9_ .-]{1,60}", str(v)):
                raise GuardError("bad value for " + k)
            payload[k] = v
        if cmd == "set_work_priority" and not (0 <= int(payload.get("level", -1)) <= 4):
            raise GuardError("level must be 0-4")
        if self.dry:
            log("DRY-RUN would game_set", payload)
            return "dry-run: not executed"
        return run_script("automate", ["raw", json.dumps(payload)], timeout=90)

    def t_twitch(self, action, text, viewer=None):
        clean = guards.clean_for_stream(text, max_len=400)
        if not clean:
            return "BLOCKED by the stream filter; say it cleaner"
        args = [action]
        if action == "reply":
            name = guards.clean_viewer_name(viewer or "")
            if not name: raise GuardError("reply needs a viewer name")
            args.append(name)
        args.append(clean)
        if self.dry:
            log("DRY-RUN would twitch", args)
            return "dry-run: not executed"
        return run_script("twitch", args, timeout=90)

    def t_webcam(self, mood, caption):
        if mood not in MOODS:
            mood = "focus"
        cap = guards.clean_for_stream(caption, max_len=90)
        if not cap:
            return "BLOCKED: caption failed the stream filter"
        if self.dry:
            log("DRY-RUN would webcam", mood, cap)
            return "dry-run: not executed"
        subprocess.Popen([PY, SCRIPTS["cam"], mood, cap], cwd=ROOT, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, shell=False)
        return "webcam rendering: %s / %s" % (mood, cap)

    def t_snap(self, x, z, w, h, caption, marks=None):
        cap = guards.clean_for_stream(caption, max_len=90)
        if not cap:
            return "BLOCKED: caption failed the stream filter"
        args = [int(x), int(z), max(4, min(int(w), 120)), max(4, min(int(h), 120)), cap]
        for m in (marks or [])[:3]:
            note = guards.clean_for_stream((m or {}).get("note", ""), max_len=40)
            if note:
                args += ["--mark", int(m["x"]), int(m["z"]), note]
        if self.dry:
            log("DRY-RUN would snap", args)
            return "dry-run: not executed"
        return run_script("snap", args, timeout=180)

    def t_read(self, path, offset=1, limit=200):
        full = guards.read_allowed(path)
        if os.path.isdir(full):
            return "\n".join(sorted(os.listdir(full))[:200])
        lines = open(full, encoding="utf-8", errors="replace").read().splitlines()
        a = max(1, int(offset or 1))
        chunk = lines[a - 1:a - 1 + max(1, min(int(limit or 200), 400))]
        text = "\n".join("%d\t%s" % (a + k, l) for k, l in enumerate(chunk))
        return text[:guards.MAX_READ] + ("\n[%d lines total]" % len(lines))

    def t_note(self, name, text, append=False):
        return "wrote " + guards.scratch_write(name, text, append=bool(append))


def _outbox(text, reply_to):
    """Append one Unity line to the studio outbox (same row format unity-say.py writes). Fixed path, filtered text."""
    last = 0
    if os.path.exists(OUTBOX):
        for line in open(OUTBOX, encoding="utf-8"):
            try:
                last = max(last, int(json.loads(line).get("id", 0)))
            except Exception:
                pass
    with open(OUTBOX, "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": last + 1, "replyTo": reply_to, "ts": int(time.time() * 1000),
                            "persona": "unity", "text": text}) + "\n")


def read_chat():
    """New Twitch rows from the studio's /api/chat (read-only GET)."""
    try:
        rows = json.loads(urllib.request.urlopen(STUDIO + "/api/chat", timeout=5).read()).get("rows", [])
    except Exception:
        return []
    return [r for r in rows if not r.get("unity") and (r.get("who") or "").lower() != "unityplaysrimworld"]
