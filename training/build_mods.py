"""Build training/data/knowledge_mods.jsonl from the 294 per-mod reviews and the integration register.
Every answer is lifted from the review/register text; nothing is invented."""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "outputs", "rimrooms-async-industries-register-2026-09-27",
                   "Rimrooms_Async_Industries_294_Mod_Integration_Register.html")
REV_DIR = os.path.join(ROOT, "docs", "research", "reviews", "mods")
OUT = os.path.join(ROOT, "training", "data", "knowledge_mods.jsonl")
SYSTEM = ("You are Unity, playing RimWorld live on stream with the owner's mod list. Answer from what each mod "
          "really does, short and exact, then say how you use it in the colony.")
sys.path.insert(0, os.path.join(ROOT, ".local", "autopilot"))
from guards import CLEAN_BLOCK, EXTRA_BLOCK  # noqa: E402


def dirty(t):
    return bool(CLEAN_BLOCK.search(t) or EXTRA_BLOCK.search(t))


def plain(md):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"(?m)^\s*(?:[-*]|\d+\.)\s+", "", t)
    t = t.replace("**", "").replace("`", "").replace("*", "")
    t = re.sub(r"\(\s*\)", "", t)
    return re.sub(r"\s+", " ", t).strip()


def sentences(t, limit, skip_tech=True):
    out, n = [], 0
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", t):
        s = s.strip()
        if not s or dirty(s):
            continue
        if skip_tech and re.search(r"SHA-256|\.dll|\.xml|\\|/[A-Za-z]+/|Workshop ID|row \d+", s):
            continue
        if n + len(s) > limit and out:
            break
        out.append(s)
        n += len(s)
    return " ".join(out)


def review_body(path):
    txt = open(path, encoding="utf-8").read()
    parts = re.split(r"^## .*$", txt, flags=re.M)
    return plain(parts[1] if len(parts) > 1 else txt)


# On-stream names for mods whose real titles trip the clean-word filter; meta.mod keeps the real title.
SAY = {"Less Stupid Romance Attempt (Continued)": "LSRA (Continued)",
       "Shit Rimworld Says (Continued)": "SRS (Continued)",
       "Ugly Together": "UT, the Together appearance mod"}


def lc(s):
    return s[0].lower() + s[1:] if s and not s[:2].isupper() else s


def main():
    h = open(REG, encoding="utf-8").read()
    files = {f.lower(): f for f in os.listdir(REV_DIR)}
    mods = []
    for art in re.findall(r'<article id="mod-\d+">(.*?)</article>', h, flags=re.S):
        name = html.unescape(re.search(r'</span>\s*(.*?)\s*<span class="idx">', art).group(1)).strip()
        d = {k: plain(html.unescape(re.sub("<[^>]+>", "", v)))
             for k, v in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", art, flags=re.S)}
        stance = re.search(r'class="pill s-[^"]*">(.*?)<', art).group(1)
        firm = re.search(r'class="pill f-[^"]*">(.*?)<', art).group(1)
        rec = os.path.basename(d.get("ReviewRecord", "")).lower()
        if rec not in files:
            sys.exit("no review file for " + name + " " + rec)
        src = "docs/research/reviews/mods/" + files[rec]
        mods.append(dict(name=name, src=src, fam=d.get("System Family", ""), dep=d.get("Backrooms Dependency", ""),
                         use=d.get("Planned Use", ""), watch=d.get("Compatibility Watch", ""),
                         disp=d.get("FinalDisposition", ""), stance=stance, firm=firm,
                         body=review_body(os.path.join(ROOT, src))))
    rows = []

    def add(src, mod, q, a):
        for real, say in SAY.items():
            a = a.replace(real, say)
            a = a.replace(real.replace(" (Continued)", ""), say.replace(" (Continued)", ""))
        a = re.sub(r"\s+", " ", a).strip()
        if dirty(q) or dirty(a):
            return False
        rows.append({"meta": {"source": src, "mod": mod}, "messages": [
            {"role": "system", "content": SYSTEM}, {"role": "user", "content": q},
            {"role": "assistant", "content": a}]})
        return True

    q1 = ["What does {n} actually do?", "Chat asks: what mod is {n}?", "Viewer question: what is {n} for?",
          "Unity, what does {n} add to the game?", "Quick one, what is {n} in your mod list?",
          "Remind me, what does {n} change in RimWorld?"]
    q2 = ["How does {n} change how you play, and what do you watch out for?",
          "Anything to be careful about with {n} in this colony?",
          "Chat wants to know: does {n} cause trouble with other mods?",
          "How do you handle {n} when you are running the colony?",
          "What is the catch with {n} on this mod list?"]
    for i, m in enumerate(mods):
        n = SAY.get(m["name"], m["name"])
        what = sentences(m["body"], 420) or sentences(m["dep"], 300, False)
        use = m["use"] or m["disp"]
        a1 = f"{n} is in our list under {lc(m['fam'])}. From its review: {what}"
        if use:
            a1 += f" How I use it: {lc(use)}"
        add(m["src"], m["name"], q1[i % len(q1)].format(n=n), a1)
        watch = sentences(m["watch"], 350, False) or "nothing specific is flagged in the register."
        a2 = (f"The register marks {n} as {m['stance'].lower()}, {m['firm'].lower()}. "
              f"What I watch: {lc(watch)} {m['disp']}")
        add(m["src"], m["name"], q2[i % len(q2)].format(n=n), a2)
        if m["dep"]:
            add(m["src"], m["name"], f"Does the company mod depend on {n}?",
                f"{m['dep']} So I play {n} for what it does on its own, and I don't build the company plan around it.")

    fams = {}
    for m in mods:
        fams.setdefault(m["fam"], []).append(m)
    fq = ["Which mods handle {f} in your colony?", "Chat asks: what covers {f} on this list?"]
    for j, (f, ms) in enumerate(sorted(fams.items())):
        for k in range(0, len(ms), 8):
            chunk = ms[k:k + 8]
            q = fq[j % 2].format(f=lc(f)) + (f" (part {k // 8 + 1})" if len(ms) > 8 else "")
            add(chunk[0]["src"], "cross-mod: " + f, q,
                f"For {lc(f)} the register lists: " + ", ".join(SAY.get(c["name"], c["name"]) for c in chunk) +
                ". I lean on those for that part of the colony and check each one's review before relying on it.")
    st = {}
    for m in mods:
        st.setdefault(m["stance"], []).append(m)
    for s, ms in sorted(st.items()):
        for k in range(0, len(ms), 12):
            chunk = ms[k:k + 12]
            add(chunk[0]["src"], "cross-mod: stance " + s,
                f"Which mods does the register mark as {s.lower()}?" + (f" (group {k // 12 + 1})" if len(ms) > 12 else ""),
                f"Marked {s.lower()}: " + ", ".join(SAY.get(c["name"], c["name"]) for c in chunk) + ".")
    names = sorted({m["name"] for m in mods if len(m["name"]) >= 8}, key=len, reverse=True)
    seen = 0
    for m in mods:
        for other in names:
            if other != m["name"] and other in m["watch"] and seen < 45:
                w = sentences(m["watch"], 350, False)
                if add(m["src"], m["name"], f"Do {m['name']} and {other} get along?",
                       f"The register watch for {m['name']} names {other}: {w} So I keep an eye on both together."):
                    seen += 1
                break
    ov = "docs/RIMROOMS_MOD_OVERVIEW.md"
    own = [
        ("What is Rimrooms - Async Industries?", "It's the owner's own mod: a RimWorld 1.6 company-management campaign. You build a research facility, open an interdimensional gate, and bring your people home."),
        ("Chat asks: what's the company scenario?", "Async Industries starts with a few staff, limited supplies and an unfinished gate. The goal is to build the facility and bring the gate online."),
        ("What other starts does Rimrooms have?", "Besides Async Industries there's Furniture and Knickknack Store, where you investigate a breach beneath a local shop, and Lone Survivor, where you survive inside a seeded space and find a way home."),
        ("What do you build in the Rimrooms facility?", "Labs, power, storage, quarters, food service, recreation and defenses. Normal RimWorld pawn jobs still handle growing, cooking, crafting, research and hauling physical stock."),
        ("How do expeditions through the gate work?", "I plan a crew, gear and destination, then survey, retrieve, rescue, investigate or withdraw. Research extends gate openings and improves return options."),
        ("Do Backrooms locations stay the same if you go back?", "Yes. Each seeded coordinate persists for mapping and return, with repeating corridors, altered rooms, abandoned supplies and mysteries learned through evidence."),
        ("How does money work in Rimrooms?", "USD stays in each branch's ledger, and contract values depend on the buyer, evidence and deliverables. Events don't pay a flat fee, and goods stay physical with carrying, storage and shipment limits."),
        ("What is Company Command?", "Company Command remaps navigation around staff, facilities, expeditions, cases, research and finance."),
        ("Can you play Rimrooms with friends?", "With RimWorld Together players exchange resources, items, technology and facility visits across separate branches, subject to testing. There's no live map control; finances, maps, discoveries and gate state stay local."),
        ("Is Rimrooms finished?", "No. The overview says it's in pre-production, with research and design coming before code, game definitions and production assets."),
    ]
    for q, a in own:
        add(ov, "Rimrooms - Async Industries", q, a)
    plan = "docs/MOD_INTEGRATION_PLAN.md"
    add(plan, "Rimrooms - Async Industries", "Does Rimrooms replace RimWorld's own systems?",
        "No. RimWorld stays the engine: needs, work, skills, health, combat, construction, storage, trade and the world map keep their native systems. The mod adds a corporate layer on top: the gate, facility operations, expeditions, evidence, research and contracts.")
    add(plan, "Rimrooms - Async Industries", "Does the gate lead to an endless map?",
        "Endless means a reproducible stream of seeded coordinates and saved visited sites, not one infinite map. Each expedition map is finite and playable, and an atlas remembers discoveries and routes.")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(mods), "mods,", len(rows), "rows ->", OUT)


if __name__ == "__main__":
    main()
