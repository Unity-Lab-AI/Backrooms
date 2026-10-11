"""Score the quantised brain on the held-out sets, pick the quant, and decide whether it may replace today's voice.

    python eval.py <gguf> [<gguf> ...]   -> /workspace/gguf/brain-eval.json

For each gguf: llama-server (CUDA) on 127.0.0.1:8081, then
  voice  every eval_voice.jsonl prompt, asked exactly as the stream asks (system + "ONE spoken line" user turn,
         temperature 0.9, no thinking), two fixed seeds -- scored by voice_score.py, the stream's own rules
  tools  every held-out play episode (eval_tools.jsonl), each of her first 6 tool steps: given everything before
         it, does the brain call the same tool with arguments that validate against the tool schema
Quant: the smaller IQ4_XS is kept unless it scores more than 0.02 under Q4_K_M on voice pass or tool accuracy.
Voice verdict: the brain replaces today's voice only when its voice pass >= today's (baseline_voice.json, made on
the rig by training/eval_baseline.py with the same scorer) and its distinct-line rate is no more than 0.02 lower.
No baseline -> no replacement (the brain still plays; the old voice stays).
"""
import json, os, subprocess, sys, time, urllib.request

W = "/workspace"
D = os.path.join(W, "data", "brain")
REPO = os.environ.get("BRAIN_REPO", os.path.join(W, "repo"))
os.environ["BRAIN_REPO"] = REPO
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_score  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "training"))
import check_player  # noqa: E402  (schema validation only)

PORT = 8081
SEEDS = (11, 22)
TOOLS = json.load(open(os.path.join(D, "tools.json"), encoding="utf-8"))
SCHEMA = {t["function"]["name"]: t["function"]["parameters"] for t in TOOLS}


def post(path, body, timeout=300):
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (PORT, path), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def serve(gguf):
    p = subprocess.Popen([os.path.join(W, "llama.cpp", "build", "bin", "llama-server"), "-m", gguf, "-ngl", "999",
                          "-c", "32768", "--jinja", "-fa", "on", "--port", str(PORT), "--host", "127.0.0.1"],
                         stdout=open(os.path.join(W, "eval-server.log"), "ab"), stderr=subprocess.STDOUT)
    for _ in range(300):
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/health" % PORT, timeout=2).read()
            return p
        except Exception:
            time.sleep(2)
    p.kill()
    raise SystemExit("llama-server never came up for %s" % gguf)


def chat(msgs, seed, tools=None, max_tokens=60, temperature=0.9):
    body = {"messages": msgs, "temperature": temperature, "max_tokens": max_tokens, "seed": seed,
            "chat_template_kwargs": {"enable_thinking": False}}
    if tools:
        body["tools"] = tools
    return post("/v1/chat/completions", body)["choices"][0]["message"]


def to_openai(msgs):
    """Our rows -> OpenAI chat messages (ids paired in order)."""
    out, ids, k = [], [], 0
    for m in msgs:
        if m["role"] == "assistant" and m.get("tool_calls"):
            calls = []
            for c in m["tool_calls"]:
                k += 1
                ids.append("call%d" % k)
                calls.append({"id": "call%d" % k, "type": "function", "function": {
                    "name": c["function"]["name"], "arguments": json.dumps(c["function"]["arguments"])}})
            out.append({"role": "assistant", "content": m.get("content") or "", "tool_calls": calls})
        elif m["role"] == "tool":
            out.append({"role": "tool", "tool_call_id": ids.pop(0) if ids else "call0", "content": str(m.get("content", ""))})
        else:
            out.append({"role": m["role"], "content": m.get("content") or ""})
    return out


def eval_voice():
    rows = [json.loads(l) for l in open(os.path.join(D, "eval_voice.jsonl"), encoding="utf-8") if l.strip()]
    all_rows, lines = [], []
    for s in SEEDS:
        for r in rows:
            lines.append(chat(r["messages"][:2], s).get("content") or "")
            all_rows.append(r)
    res = voice_score.score(all_rows, lines)
    res["sample"] = [voice_score.first_line(l) for l in lines[:12]]
    return res


def eval_tools():
    steps = ok = name_ok = 0
    for l in open(os.path.join(D, "eval_tools.jsonl"), encoding="utf-8"):
        msgs = json.loads(l)["messages"]
        seen = 0
        for i, m in enumerate(msgs):
            if m["role"] != "assistant" or not m.get("tool_calls") or m.get("weight") == 0:
                continue
            seen += 1
            if seen > 6:
                break
            want = m["tool_calls"][0]["function"]["name"]
            got = chat(to_openai(msgs[:i]), 7, tools=TOOLS, max_tokens=400, temperature=0.2).get("tool_calls") or []
            steps += 1
            if got:
                fn = got[0].get("function", {})
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except Exception:
                    args = None
                if fn.get("name") == want:
                    name_ok += 1
                    if isinstance(args, dict) and not check_player.validate(args, SCHEMA[want]):
                        ok += 1
    return {"steps": steps, "same_tool": name_ok / max(1, steps), "valid_same_tool": ok / max(1, steps)}


def main():
    res = {}
    for g in sys.argv[1:]:
        p = serve(g)
        try:
            res[os.path.basename(g)] = {"voice": eval_voice(), "tools": eval_tools(), "bytes": os.path.getsize(g)}
            print(os.path.basename(g), json.dumps({k: v for k, v in res[os.path.basename(g)]["voice"].items() if k != "sample"}),
                  json.dumps(res[os.path.basename(g)]["tools"]), flush=True)
        finally:
            p.kill(); p.wait()
    q4 = next((k for k in res if "Q4_K_M" in k), None)
    iq = next((k for k in res if "IQ4_XS" in k), None)
    pick = q4
    if iq and q4:
        a, b = res[iq], res[q4]
        if (a["voice"]["pass"] >= b["voice"]["pass"] - 0.02 and
                a["tools"]["valid_same_tool"] >= b["tools"]["valid_same_tool"] - 0.02):
            pick = iq
    elif iq:
        pick = iq
    base_p = os.path.join(D, "baseline_voice.json")
    v = res[pick]["voice"]
    if os.path.exists(base_p):
        base = json.load(open(base_p, encoding="utf-8"))
        replace = v["pass"] >= base["pass"] and v["distinct"] >= base["distinct"] - 0.02
        why = "brain voice pass %.3f distinct %.3f vs today's %.3f / %.3f" % (v["pass"], v["distinct"], base["pass"], base["distinct"])
    else:
        replace, why = False, "no baseline_voice.json -- today's voice was never scored, so it stays"
    out = {"results": res, "picked": pick, "voice_replaces_today": replace, "voice_why": why}
    json.dump(out, open(os.path.join(W, "gguf", "brain-eval.json"), "w"), indent=1)
    print("picked", pick, "| voice replaces today's:", replace, "|", why, flush=True)
    open(os.path.join(W, "out", "picked.txt"), "w").write(pick)


if __name__ == "__main__":
    main()
