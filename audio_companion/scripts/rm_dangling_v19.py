import pcbnew, sys, math
b=pcbnew.LoadBoard(sys.argv[1]); out=sys.argv[2]
f=lambda v:v/1e6
def ends(t): return (t.GetStart(),t.GetEnd())
removed=0
for it in range(8):
    tr=[t for t in b.GetTracks() if t.GetClass()!="PCB_VIA"]; vias=[t for t in b.GetTracks() if t.GetClass()=="PCB_VIA"]
    pads=[(p,str(p.GetNetname())) for fp in b.GetFootprints() for p in fp.Pads()]
    gone=[]
    for t in tr:
        n=str(t.GetNetname()); lay=t.GetLayer()
        for e in ends(t):
            x,y=f(e.x),f(e.y); ok=False
            for o in tr:
                if o is t or o.GetLayer()!=lay or str(o.GetNetname())!=n: continue
                for oe in ends(o):
                    if abs(f(oe.x)-x)<0.012 and abs(f(oe.y)-y)<0.012: ok=True
            if not ok:
                for v in vias:
                    if str(v.GetNetname())==n and math.hypot(f(v.GetPosition().x)-x,f(v.GetPosition().y)-y)<f(v.GetWidth(pcbnew.F_Cu))/2+0.01: ok=True
            if not ok:
                for p,pn in pads:
                    if pn==n and p.IsOnLayer(lay) and p.HitTest(e): ok=True
            if not ok: gone.append(t); break
    if not gone: break
    for t in gone: b.RemoveNative(t); removed+=1
# vias with nothing attached on either layer
print("dangling tracks removed:",removed)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(out)
