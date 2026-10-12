import json,re,sys,pathlib
D=pathlib.Path("/Users/admin/repos/AbsaOSS/living-doc/agentic-evals-workspace/trigger-evals-2")
ENT=re.compile(r'\b(US|FEAT|FUNC)-\d+|AC:US-\d+'); PR=re.compile(r'PR #?\d+')
rows=[];tp=tn=fp=fn=0; idh=idt=ph=pt=0; fails=[]; fires=[]
for f in sorted(D.glob("*.json")):
    if f.stat().st_size==0: continue
    d=json.loads(f.read_text()); res=d["results"] if isinstance(d,dict) else d
    s=f.stem; P=[r for r in res if r["should_trigger"]]; N=[r for r in res if not r["should_trigger"]]
    ff=[r for r in N if r["triggers"]>0]; fires+= [(s,r) for r in ff]
    i=[r for r in P if ENT.search(r["query"]) or PR.search(r["query"])]; pa=[r for r in P if r not in i]
    ih=sum(1 for r in i if r["pass"]); ph_=sum(1 for r in pa if r["pass"])
    idh+=ih; idt+=len(i); ph+=ph_; pt+=len(pa)
    tp+=sum(1 for r in P if r["pass"]); fn+=sum(1 for r in P if not r["pass"])
    tn+=len(N)-len(ff); fp+=len(ff)
    fails+=[(s,r) for r in P if not r["pass"]]
    rows.append((s,d["summary"]["passed"],d["summary"]["total"],
                 f"{ih}/{len(i)}" if i else "—", f"{ph_}/{len(pa)}" if pa else "—",
                 f"{len(N)-len(ff)}/{len(N)}"))
print(f"{'skill':34} {'overall':>9} {'id-bearing':>11} {'paraphrase':>11} {'negatives':>10}")
for r in rows: print(f"{r[0]:34} {str(r[1])+'/'+str(r[2]):>9} {r[3]:>11} {r[4]:>11} {r[5]:>10}")
print(f"\nTOTALS passed={tp+tn}/{tp+fn+tn+fp}  recall id={idh}/{idt}"
      f"{' = %.2f'%(idh/idt) if idt else ''}  paraphrase={ph}/{pt}{' = %.2f'%(ph/pt) if pt else ''}")
print(f"PRECISION: {tp}/{tp+fp} = {tp/(tp+fp):.2f}  (false fires across {tp+0+tn+fp-tp} negatives: {fp})" if (tp+fp) else "")
if fires:
    print("\n!! FALSE FIRES (precision break) !!")
    for s,r in fires: print(f"  {s}: rate={r['trigger_rate']:.2f} {r['query']}")
print(f"\nFAILING POSITIVES ({len(fails)}):")
for s,r in fails:
    k="ID" if (ENT.search(r["query"]) or PR.search(r["query"])) else "para"
    print(f"  {s:32} [{k:4}] rate={r['trigger_rate']:.2f} {r['query'][:78]}")
