import pcbnew, sys, math
b=pcbnew.LoadBoard(sys.argv[1]); h=float(sys.argv[3])
u=[f for f in b.GetFootprints() if f.GetReference()=="U1"][0]; c=u.GetPosition(); cx,cy=c.x/1e6,c.y/1e6
n=0
for t in list(b.GetTracks()):
    if t.GetClass()=="PCB_VIA":
        p=t.GetPosition(); pts=[(p.x/1e6,p.y/1e6)]
        if math.hypot(pts[0][0]-cx,pts[0][1]-cy)<1.2: continue
    else: pts=[(t.GetStart().x/1e6,t.GetStart().y/1e6),(t.GetEnd().x/1e6,t.GetEnd().y/1e6)]
    if any(abs(x-cx)<=h and abs(y-cy)<=h for x,y in pts): b.RemoveNative(t); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("stripped2",n)
