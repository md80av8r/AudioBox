import pcbnew, json, sys, math
b=pcbnew.LoadBoard(sys.argv[1]); out=sys.argv[2]; netname=sys.argv[3] if len(sys.argv)>3 else "/AGND"
f=lambda v:v/1e6
conn=b.GetConnectivity(); conn.Build(b)
net=b.FindNet(netname).GetNetCode(); items=[]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetCode()==net: items.append((str(fp.GetReference())+"."+p.GetNumber(),p,["F","B"] if p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD else ["F"]))
for t in b.GetTracks():
    if t.GetNetCode()==net and t.GetClass()=="PCB_VIA": items.append(("via",t,["F","B"]))
cl=[]; seen=set()
for n,it,L in items:
    key=it.m_Uuid.AsString()
    if key in seen: continue
    ids={g.m_Uuid.AsString() for g in conn.GetConnectedItems(it)}|{key}
    mem=[(m,x,l) for m,x,l in items if x.m_Uuid.AsString() in ids]; cl.append(mem); seen|=ids
cl.sort(key=len,reverse=True)
print("clusters",[len(c) for c in cl])
pairs=[]
main=cl[0]
for small in cl[1:]:
    best=None
    for n1,a,l1 in small:
        for n2,c,l2 in main:
            d=math.hypot(f(a.GetPosition().x)-f(c.GetPosition().x),f(a.GetPosition().y)-f(c.GetPosition().y))
            if d>0.5 and (best is None or d<best[0]): best=(d,n1,a,l1,n2,c,l2)
    d,n1,a,l1,n2,c,l2=best
    pairs.append(dict(net=netname,a=dict(c=[f(a.GetPosition().x),f(a.GetPosition().y)],net=netname,layers=l1,desc=n1),b=dict(c=[f(c.GetPosition().x),f(c.GetPosition().y)],net=netname,layers=l2,desc=n2)))
    print("bridge",n1,"->",n2,round(d,1),"mm")
json.dump(pairs,open(out,"w")); print(len(pairs),"pairs")
