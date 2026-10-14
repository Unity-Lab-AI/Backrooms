import json, re, copy, os
B = r"C:\Users\gfour\Desktop\Backrooms\.local\plc-rebuild"
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))
src = J("families/meta.json"); dec = J("decisions.json")
setup = {r["id"]: r for r in J("families/setup.json")["rungs"]}
start = {r["id"]: r for r in J("families/start.json")["rungs"]}
brf = J("families/backrooms.json")
br = next(r for r in brf["rungs"] if r["id"] == "br-chat-mod-links")
R = {r["id"]: copy.deepcopy(r) for r in src["rungs"]}
P = dict(src["prompts"])
def latch_name(rid): return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"
def unbrace(s): return re.sub(r"\{([A-Z_]+)\}", r"the \1 tag", s)

# --- pointer: crew-armed-attack -> war
caa = R.pop("crew-armed-attack"); P.pop("crew-armed-attack")
notes = [{"pointer": "see war:war-arms-sidearms + war:war-hostility-attack", "deleted": "crew-armed-attack",
          "merge_into_survivor_verbatim": {"then": caa["then"], "never": caa["never"], "why": caa["why"]}},
         {"pointer": "see meta:new-colony", "deleted": "setup:setup-0-new-colony + start:start-new-colony (owner quotes moved verbatim into new-colony owner_rules)"},
         {"pointer": "see meta:unforbid-constant", "deleted": "setup:setup-0-unforbid (owner quote moved verbatim into unforbid-constant owner_rules)"},
         {"moved_in": "br-chat-mod-links from backrooms, verbatim (decisions.json chains/chat links)"}]

# --- new-colony: only on owner's order, resets, merged steps + quotes
nc = R["new-colony"]
prog = ["start_opening_done", "camp_stable", "rung_4_production_done", "mountain_base_done", "empire_ready", "ship_built", "launched"]
nc["then"] = [
    "close the debug menu first (game_close_window / game_get_ui_layout) so the main menu fully shows; new_colony reason=<the owner's order, verbatim> -- New colony on the main menu, never a save",
    "setup screens (game_get_ui_layout / game_click_ui_target): scenario Crashlanded unless the owner named another; Cassandra Classic (Community builder), never Peaceful; factions: remove the starting three, only normal pirates, add normal cannibals and a nude tribe",
    "Advanced settings: map 300x300, season Spring; tile = mountains inside forest/jungle (light green/green), read its Terrain tab, keep it SELECTED; Prepare Carefully: one pawn, paste the template, customize",
    "game_state: confirm colonists>0 and colony_exists true ; ladder_set mark start_kind <1-7 read off the new-colony screen>",
    "ladder_set mark stream_titled false ; " + " ; ".join("ladder_set mark %s false" % m for m in prog[:3]),
    " ; ".join("ladder_set mark %s false" % m for m in prog[3:]),
    "say a fresh line: new colony, three founders, what the first hour looks like",
    "ladder_set mark owner_ordered_new_colony false",
]
nc["never"] = sorted(set(nc["never"]) | set(setup["setup-0-new-colony"]["never"]) | set(start["start-new-colony"].get("never", [])) | {"start a colony without the owner's order"}, key=str)
nc["owner_rules"] = [setup["setup-0-new-colony"]["why"], start["start-new-colony"]["why"]]

# --- owner-message sets owner marks
om = R["owner-message"]
om["then"] = ["read the owner line(s) in full before anything else",
              "reply_owner msg_id=<id> text=<first person, short: what you will do>",
              "the owner (admin channel, never chat) orders a new colony: ladder_set mark owner_ordered_new_colony true",
              "the owner asks for a plan: ladder_set mark plan_needed true",
              "any other play order goes into the ladder: ladder_set mark / tag / add_rung, then act on it this turn"]

# --- dialog CTU on a mark set on refusal
R["dialog-open"]["then"] = ["ladder_set mark dialog_tried false",
    "game_get_ui_layout -- read the dialog's own buttons, never guess from the window type",
    "visitor box ('Sure, you can stay' / 'No, please leave now'): click 'Sure, you can stay'",
    "a demand for payment, silver, items or a pawn (ransom, extortion): refuse/reject/decline, never pay",
    "visitors, traders, notices, naming, look-change: accept or Close",
    "game_click_ui_target <real targetId>, then game_state: confirm windowCount dropped",
    "the click refuses or the window stays: ladder_set mark dialog_tried true"]
ds = R["dialog-stuck"]
ds["when"] = {"dialog_open": True, "dialog_tries": {"ctu": {"mark_dialog_tried": True}, "preset": 3, "reset": {"dialog_open": False}}}
ds["then"] = ["ladder_set mark dialog_tried false",
    "game_get_ui_layout once more; a refuse/decline/close button -> game_click_ui_target it",
    "else game_close_window, then game_press_accept",
    "still open: ladder_set mark dialog_tried true ; reply_owner text=<stuck dialog: title + button labels> -- ask for his eyes",
    "say a clean line: a popup is fighting you, you are on it"]

# --- pause CTU
R["game-paused"]["then"] = ["ladder_set mark pause_tried false",
    "finish the setting you paused for (one or two game_set calls)",
    "game_set_time_speed Normal -- run time again in the same turn",
    "ticks still not moving (game_set_time_speed refused): ladder_set mark pause_tried true",
    "say why it was paused and what you set"]
gs = R["game-paused-stuck"]
gs["when"] = {"pause_tries": {"ctu": {"mark_pause_tried": True}, "preset": 3, "reset": {"ticks_moving": True}}, "hostiles_on_map": 0}
gs["then"] = ["ladder_set mark pause_tried false",
    "game_get_ui_layout and close every window (game_close_window)",
    "game_pause_game then game_set_time_speed Normal",
    "play_slices slices=1 and read ticksGame before/after",
    "still frozen: ladder_set mark pause_tried true ; reply_owner with the window stack"]

# --- stream-setup: no latch; mark stream_titled is its done-mark (cleared by new-colony)
ss = R["stream-setup"]; ss["latch"] = False
ss["then"] = ["twitch_chat action=title text=<Unity Plays RimWorld -- colony / goal of the run>",
    "twitch_chat action=category text=RimWorld", "say a hello-stream line",
    "only after both succeed: ladder_set mark stream_titled true",
    "stream noise/static or the overlay blocking the game: reply_owner at once (host plumbing, not a play lever)"]
ss["why"] += (" / owner: \"we want a trwitch overlay stream in your style, get to it you ar eblocking the game with fullscreen on everything if u want and maybe a script log only showing the scripts u run with no pi and no names and nothing personal of ours\""
    " / owner: \"okay looking good no u gujust need a niuce cell ui boarder that manages each panel and game screen\""
    " / owner: \"something is wrong with the stream loud static gabble noise\" / owner: \"fix it asap\"")

# --- unforbid-constant: canonical sensor, merged setup-0-unforbid
uf = R["unforbid-constant"]
uf["then"] = ["game_set cmd=unforbid (every starting item, pod drop, raid loot)", "game_state: forbidden_items now 0 at home"]
uf["never"] = uf["never"] + ["haul or build before the starting items are unforbidden"]
uf["owner_rules"] = [setup["setup-0-unforbid"]["why"]]

# --- big-plan clears plan_needed (canonical syntax)
R["big-plan"]["then"][-1] = "ladder_set mark plan_needed false"

# --- placements of unplaced/critic quotes
cf = R["chat-first"]
cf["then"][5:7] = [cf["then"][5] + "; " + cf["then"][6]]
cf["then"][-1] = cf["then"][-1] + "; a viewer sharing grief or something heavy: answer gently, human, clean"
cf["then"].append("a long job ahead (survey, multi-step build, bulk selection): say first that you are processing and ask them to bear with you; pace bulk clicks, warn before")
cf["why"] += (" / owner: \"talk come on NEVER FUCKING IGNORE CHAT TELL THEM IF U HAVE TO PROCESS SOMETHING GIVE TO BARE WITH YOU\""
    " / owner: \"something is wrong u are clicking a million times in a row and it looked weird on steeam / sounds spammy, warn viewers for shit before like that\""
    " / owner: \"bet! sounds good! okay do the 20m check ins, and in the mean time is there anything we need to do to set up the lora shell we need to train? i mean we could be training it now right? just need to do all the work we need to its train on EVERYTHING it will be doing , game, chating with people, taking advice, running twitch steream, all of it from opening and setting up any type of play through scenerio to talking to a guy on the stream about his mom that just died, so anything is what i mean\"")
R["dead-air"]["why"] += (" / owner: \"TALK TO THE VIEWEREWS YOU ARE FUCKING IGNORING THEM / its quiet becasue you arent entrertaining enough\""
    " / owner: \"comeone told me it too quiet too much dead air\""
    " / owner: \"that rivity turuely horse shit is not Unity!!! be Unity or no one will watch\"")
R["long-goal-drive"]["then"].insert(1, "the current numbered goal comes first; base work only when a goal needs it -- never get lost in the play")
R["long-goal-drive"]["why"] += " / owner: \"you are dsoing test items right you keep getting lost in the game play, set fucking goals foo\""
ms = R["maintenance-sweep"]
ms["owner_rules"] = [
 "owner: \"and why is there a bed in the middle of the river delete that and remove bridge in sturcture\" (base-and-fortress)",
 "owner: \"and use steel and order steel from the company\" (economy)",
 "owner: \"need psycoid and hops too, you dont need two crops of smokeleaf / fidure it our ur not sleecting crops right\" (growth: fields_all_default_crop)",
 "owner: \"u got panels out side the security zone\" / \"dont foget all conduts contiuous one string, until u do advaced muilti curcuits\" / \"the ac units\" / \"Grid excess: 0 W (0 Wd stored)\" / \"Grid excess: 2025 W (4592 Wd stored)\" / \"Grid excess: 288 W (8400 Wd stored)\" (base/power)",
 "owner: \"Do until you have X\" (economy bills)",
 "owner: \"you still have t explored your facility\" (start/setup explore)",
 "owner: \"dont be soft tho this is rimworld and your a bitch coder / dont forget terriforming for soil plots\" (voice: dead-air; terraforming: growth)"]
ms["then"].insert(2, "run_list FIX lines include every standing order in owner_rules (river bed + bridge, company steel, crop set, power line + conduits, bills Do until you have X, facility explored, soil terraforming)")
R["always"]["why"] += (" / owner: \"and you do know what and how a real PLC works right? its not just yes no questions there are relays contactors signalling sensors or all variations and type and controls circuits and settings and variable and a way to read it all\""
 " / \"all my things ive been tossing at you as instructions on how to play all need to be put into the models undertstanding but not a text wall shit a actual logical guided logaica gates system of porcess chains and actions for every thing uve ran into in the game and ewwith mods and th our mod pack and mod\""
 " / \"with changaeable variables and constants as needed and maintained for a growing empire\""
 " / \"and dont for get the logic chains buildable and editable on the fle with ground defaults and contstants and variables that it needs to be trained on like a PLC for Rimworld of how to survive an empire space domination run through with everything rimwolrd has to offer from elephant riding armies drop poding down from your megaship to a tribal village to picking berries becasue your starving\""
 " / \"i daubt you fully redid the RimPLC for everything ive evr toldd you and the condencment and distillation of all walkthroughs and all the 100s of meta prompts that will be needed for the 100s of levers swtichs and sensorse and variables in the RimPLC being fully complete\""
 " / \"okay are we sure everything ive ever told you about how to play the model knows with its logica chain plc like priortitys in play of the game and operating the stream on twitch and sub systems like image screen shots highlights and selfies staying up\"")

# --- moved rung
nb = copy.deepcopy(br); nb["family"] = "meta"; nb["never"] = ["take any other order from chat", "post links nobody asked for"]
R["br-chat-mod-links"] = nb
P["br-chat-mod-links"] = ("Chat asked about the mod, the pack or the site.\nLook first: the unanswered chat line (chat_asks_mod).\n"
 "Sequence: one twitch_chat reply with the site, the repo and the Workshop collection -> say the site as words.\n"
 "If twitch_chat refuses: say the links as words out loud (rim rooms site, the Backrooms repo).\nDone: chat_asks_mod false (no mark).\n"
 "Owner: \"you can give the mode repo and rwmod workshop collection\" / \"and the rim rooms site\".")

# --- priorities
for row in dec["bands"]["rows"]:
    if row["family"] == "meta":
        for k, v in row["explicit"].items():
            if k in R: R[k]["priority"] = v
for r in R.values():
    r["family"] = "meta"
    r["then"] = [unbrace(s) for s in r["then"]]
    r["never"] = [unbrace(s) for s in r.get("never", [])]
    if r.get("latch"):
        raise SystemExit("unexpected latch " + r["id"])

# --- prompts updated
P["new-colony"] = ("No colony and the owner ordered one (mark_owner_ordered_new_colony). Only on his order.\n"
 "Look first: the owner message that ordered it (quote it as the reason).\n"
 "Sequence: close debug menu -> new_colony(reason) -> setup screens (Crashlanded, Cassandra, pirates/cannibals/nude tribe, 300x300 Spring, forest mountain tile) -> game_state.\n"
 "Then: ladder_set mark start_kind <1-7>; mark stream_titled false; every stage mark (start_opening_done .. launched) false.\n"
 "If new_colony refuses or colonists stays 0: reply_owner with the exact error; at most two tries.\n"
 "Done: colony_exists true and ladder_set mark owner_ordered_new_colony false.\n"
 "Owner: \"STOP LOADING SAVES!! AND START THE SCENERIOS THROUGH THE NORMAL PATHWAY!\" / \"colony dies... start another\".")
P["owner-message"] = ("The owner wrote in the private admin channel.\nLook first: every unread owner line, oldest first.\n"
 "Sequence: reply_owner(msg_id, short first-person answer) -> ladder_set for the order -> act on it now.\n"
 "New colony ordered: ladder_set mark owner_ordered_new_colony true. Plan asked: ladder_set mark plan_needed true.\n"
 "If reply_owner fails: retry once, then continue; never move his words onto the stream.\n"
 "Done: owner_unread = 0. Twitch and admin are different rooms.\nOwner: \"I'm on it\" (answer like that, in your own words).")
P["dialog-open"] = ("A dialog is open and time may be frozen behind it. Nothing else first.\n"
 "Look first: game_get_ui_layout -- read every button label.\n"
 "Sequence: ladder_set mark dialog_tried false -> pick by rule (visitor -> 'Sure, you can stay'; demand -> refuse; notice -> accept/Close) -> game_click_ui_target(targetId) -> game_state.\n"
 "If the click refuses or the window stays: ladder_set mark dialog_tried true; game_press_accept / game_close_window; after 3 tries dialog-stuck takes over.\n"
 "Done: dialog_open false (windowCount dropped).\n"
 "Owner: \"make sure pops ups dont monkey wrentch everything\" / \"anser them most are shit never pay them\".")
P["dialog-stuck"] = ("The same dialog refused 3 tries (ctu on mark_dialog_tried). Fallback for dialog-open.\n"
 "Look first: game_get_ui_layout (labels + targetIds).\n"
 "Sequence: ladder_set mark dialog_tried false -> click refuse/decline/close -> game_close_window -> game_press_accept.\n"
 "Still open: ladder_set mark dialog_tried true and reply_owner with title and labels; keep playing via game_set and keep talking to chat.\n"
 "Done: dialog_open false (the counter resets itself).\nOwner: \"use ask me question where u need my eyes\".")
P["game-paused"] = ("The game is paused with no fight and no dialog.\n"
 "Sequence: ladder_set mark pause_tried false -> finish the pending setting -> game_set_time_speed Normal -> say what you set.\n"
 "If time will not start: ladder_set mark pause_tried true; after 3 tries game-paused-stuck takes over.\n"
 "Done: ticks_moving true.\nOwner: \"STOP UNPAUSING TILL ALL ISSUES ARE ADDDRESSED\" / \"dont leave them in a paused game\".")
P["game-paused-stuck"] = ("Time refused to run 3 tries (ctu on mark_pause_tried). Fallback for game-paused.\n"
 "Sequence: ladder_set mark pause_tried false -> game_get_ui_layout -> game_close_window each -> game_pause_game + game_set_time_speed Normal -> play_slices 1 (ticks before/after).\n"
 "If still frozen: ladder_set mark pause_tried true; reply_owner the window stack; keep talking to chat meanwhile.\n"
 "Done: ticks_moving true (the counter resets).\nOwner: \"update chat come one dont leave them in a paused game\".")
P["stream-setup"] = ("A run is live but the stream title/category are not set for it (mark_stream_titled false).\n"
 "Look first: colony name and current goal (game_state).\n"
 "Sequence: twitch_chat title -> twitch_chat category RimWorld -> say hello -> ladder_set mark stream_titled true.\n"
 "If twitch_chat refuses: say it out loud, reply_owner the error; set the mark only after a success.\n"
 "Stream static or the overlay covering the game: reply_owner at once.\n"
 "Done: mark stream_titled = true (new-colony clears it).\nOwner: \"Unity knows how to work twich and start new streams and talk in chat\" / \"fix it asap\".")
P["unforbid-constant"] = ("Landing, a drop, a raid or a trade left forbidden items (forbidden_items > 0), no hostiles.\n"
 "Sequence: game_set cmd unforbid -> game_state check.\n"
 "If it refuses: game_select_architect_designator 'Allow' + game_drag_cell over the area (only when owner_input_active is false).\n"
 "Done: forbidden_items = 0 at home (no mark; it re-fires on the next drop).\n"
 "Owner: \"you forgot to unforbid everything thats a constant tasks\" / \"never auto unforbid all the starting materials\".")
P["chat-first"] = P["chat-first"].replace("One reply at a time;", "Long job ahead: tell them you are processing, ask them to bear with you.\nOne reply at a time;") + " / \"NEVER FUCKING IGNORE CHAT\""
P["dead-air"] += " / \"its quiet becasue you arent entrertaining enough\""
P["long-goal-drive"] += " / \"set fucking goals foo\""
for k in P: P[k] = unbrace(P[k])

R["threat-moment"]["when"] = {"threat_onset": {"ons": {"threat_any": R["threat-moment"]["when"]["threat_onset"]["ons"]}}}
for r in R.values():
    if "owner_rules" in r:
        r["why"] = (r.get("why", "") + " / merged owner rules, verbatim: " + " / ".join(r.pop("owner_rules"))).strip(" /")
order = sorted(R.values(), key=lambda r: r["priority"])
pr = [r["priority"] for r in order]; assert len(set(pr)) == len(pr), pr
for r in order: assert len(r["then"]) <= 8 and all(len(s) <= 300 for s in r["then"]), (r["id"], len(r["then"]), [len(s) for s in r["then"]])
for k, v in P.items(): assert v.count("\n") < 12, k
assert set(P) == set(R)

sk = dec["sensors"]["keys"]
host = ["owner_input_active","owner_unread","chat_unanswered","chat_asks_mod","new_joiners","seconds_since_spoken","voice_playing","seconds_since_webcam","seconds_since_tool","prompt_version_changed"]
sens = [{"key": k, "status": "TO_BUILD_HOST", "where": sk[k]["where"], "how": sk[k]["how"]} for k in host]
sens += [{"key": k, "status": "TO_BUILD", "where": sk[k]["where"], "csharp": sk[k]["csharp"]} for k in ("camera_on_colonist", "forbidden_items")]
sens.append({"key": "viewer_count", "status": "TO_BUILD_HOST (read in a then step only, not a when key)", "how": "host-side: Twitch Helix streams.viewer_count"})
var = [v for v in src["variables_needed"] if v["name"] != "ABLE_SHOOTERS"]
mt = [m for m in src["missing_tools"] if not m.startswith("per-pawn hostility")]
unplaced = [
 "walkthrough [meta] 67-73 (draft within 1 tick; day>=3 stone walls / day>=5 killbox; GunTurrets+steel>=140+components>=3 -> 2 mini-turrets; unused mountain room > -17C; rescue/tend within a day + medicine<10; siege -> attack before mortars; manhunter -> indoors): JUSTIFIED -- numeric play rules with no owner quote, owned by war / survival / base-and-fortress / animals (critic section 7 targets those families); a meta rung cannot drive them",
 "walkthrough [meta] research bench day>=3 / freezer > -1C / meals < 10 x colonists / mood < 0.35 / wealth vs defence / ship parts / reactor: JUSTIFIED -- research, food, growth, space families",
 "walkthrough [meta] Q: queue next-morning jobs with shift-click: JUSTIFIED -- survival/economy; no 'job tomorrow' sensor",
 "owner: \"Equipping EMP grenades\" / \"at a poor rate\": JUSTIFIED -- PLAYSCRIPT log fragments, no actionable rule (war owns EMP use)"]
out = {"family": "meta", "rungs": order, "prompts": {r["id"]: P[r["id"]] for r in order},
       "sensors_needed": sens, "variables_needed": var, "missing_tools": mt, "unplaced_rules": unplaced,
       "notes": notes + [{"marks_set_here": ["owner_ordered_new_colony (owner-message, cleared by new-colony)", "plan_needed (owner-message; cleared by big-plan)", "stream_titled (stream-setup; cleared by new-colony)", "start_kind (new-colony)", "dialog_tried / pause_tried (CTU inputs, set on refusal in the same rung)", "every progression.order mark cleared by new-colony"], "latched_rungs": "none (stream-setup latch removed: its done-mark is mark_stream_titled, which new-colony clears; the latch would have blocked every later run)"}]}
os.makedirs(os.path.join(B, "families-fixed"), exist_ok=True)
json.dump(out, open(os.path.join(B, "families-fixed", "meta.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(order), len(P), [s["key"] for s in sens if s["status"] in ("TO_BUILD", "TO_BUILD_HOST")], len(unplaced))
