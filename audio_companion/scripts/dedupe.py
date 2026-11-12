import pcbnew, sys, math
b=pcbnew.LoadBoard(sys.argv[1]); thr=float(sys.argv[3])
vs=[t for t in b.GetTracks() if t.GetClass()=="PCB_VIA"]
rm=set()
for i,a in enumerate(vs):
    if i in rm: continue
    for j in range(i+1,len(vs)):
        if j in rm: continue
        c=vs[j]
        d=math.hypot(a.GetPosition().x-c.GetPosition().x,a.GetPosition().y-c.GetPosition().y)/1e6
        if d<thr and a.GetNetname()==c.GetNetname(): rm.add(j)
for j in sorted(rm,reverse=True): b.RemoveNative(vs[j])
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("removed",len(rm))
