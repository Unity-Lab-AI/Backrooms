import json,re,random,collections
R='.local/plc-rebuild/'
d=json.load(open(R+'playbook.candidate.json',encoding='utf-8'))
P=json.load(open(R+'prompts.candidate.json',encoding='utf-8'))
cs=open('RimPLC/Source/RimPLC/Sensors.cs',encoding='utf-8').read()
gp=open('.local/autopilot/gates.py',encoding='utf-8').read()
meas=set(re.findall(r'"([a-z_0-9]+)"',cs))|set(re.findall(r'st\["([a-z_0-9]+)"\]',gp))|set(re.findall(r'setdefault\("([a-z_0-9]+)"',gp))
pref=('count_','alert_','research_','condition_','mark_')
def latch(i): return re.sub(r"[^a-z0-9]+","_",i.lower()).strip("_")[:35]+"_done"
INSTR={'ton','tof','ctu','ons','not','any','all','preset','reset','for','and','or'}
def keys(w,out):
    if isinstance(w,dict):
        for k,v in w.items():
            if k in INSTR: keys(v,out); continue
            if isinstance(v,dict) and (set(v)&INSTR) and not k.startswith(('mark_',)) and k not in meas and not k.startswith(pref):
                # label key for nested instruction
                keys(v,out); continue
            out.add(k); keys(v,out) if isinstance(v,(dict,list)) else None
    elif isinstance(w,list):
        for x in w: keys(x,out)
    return out
G=d['gates']
txt=json.dumps(G)+json.dumps(P)
setm=set(re.findall(r'ladder_set mark ([a-z0-9_]+)',txt))
for g in G:
    if g.get('latch'): setm.add(latch(g['id']))
defaults=set((d.get('marks') or {}).get('defaults',{}))
rows=[]
for g in sorted(G,key=lambda g:g['priority']):
    ks=keys(g.get('when',{}),set())
    if g.get('latch'): ks.add('mark_'+latch(g['id']))
    unm=sorted(k for k in ks if not k.startswith(pref) and k not in meas)
    nevs=sorted(k for k in ks if k.startswith('mark_') and k[5:] not in setm and k[5:] not in defaults and k not in meas)
    rows.append((g['priority'],g['id'],g.get('family'),g.get('latch'),unm,nevs))
for r in rows: print(r)
# quotes
qs=[]
for f in 'abc':
    for l in open(R+f'owner-rules-{f}.jsonl',encoding='utf-8'):
        l=l.strip()
        if l: qs.append(json.loads(l))
print('QKEYS',list(qs[0]))
random.seed(13); s=random.sample(qs,25)
full=json.dumps(d,ensure_ascii=False)+json.dumps(P,ensure_ascii=False)
try: full+=open(R+'rung-extras.candidate.json',encoding='utf-8').read()
except: pass
fulle=json.dumps(d)+json.dumps(P)
miss=[]
for q in s:
    t=q.get('quote') or q.get('owner_quote') or q.get('text')
    if t is None: t=str(q)
    ok=(t in full) or (json.dumps(t,ensure_ascii=False)[1:-1] in full) or (json.dumps(t)[1:-1] in fulle)
    if not ok: miss.append(t)
print('MISS',len(miss)); [print('  ',repr(m[:150])) for m in miss]
