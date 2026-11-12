import pcbnew, sys, math
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work"
mm=pcbnew.FromMM; V=lambda x,y: pcbnew.VECTOR2I(mm(float(x)),mm(float(y))); f=lambda v:v/1e6
b=pcbnew.LoadBoard(sys.argv[1]); OUT=sys.argv[2]
def shift(ref,dx,dy):
    fp=b.FindFootprintByReference(ref); p=fp.GetPosition(); fp.SetPosition(V(f(p.x)+dx,f(p.y)+dy)); print("moved",ref,dx,dy)
shift("J-BAT-1",0,5.5); shift("MIC_BYPASS-1",0,-1.6); shift("HEADPHONE_BYPASS-1",-3.3,0)
for t in list(b.GetTracks()):
    if str(t.GetNetname())=="/ANR_POWER_EN": b.RemoveNative(t)
def touching(refs,extra=0.1):
    pads=[]
    for r in refs:
        fp=b.FindFootprintByReference(r)
        for p in fp.Pads():
            bb=p.GetBoundingBox(); pads.append((f(bb.GetX())-extra,f(bb.GetY())-extra,f(bb.GetRight())+extra,f(bb.GetBottom())+extra,p.GetNetname()))
    return pads
def on(pt,pads,anynet=True,net=None):
    x,y=f(pt.x),f(pt.y)
    return any(a<=x<=c and d<=y<=e and (anynet or str(n)!=net) for a,d,c,e,n in pads)
pads=touching(["J-BAT-1","MIC_BYPASS-1","HEADPHONE_BYPASS-1","D1","D2"])
rm=0
for t in list(b.GetTracks()):
    if t.GetClass()=="PCB_VIA":
        if on(t.GetPosition(),pads): b.RemoveNative(t); rm+=1
    elif on(t.GetStart(),pads) or on(t.GetEnd(),pads): b.RemoveNative(t); rm+=1
print("removed tracks touching moved parts:",rm)
# mismatched-net tracks touching changed pads (R15, D7, U3 spares, etc.)
chk=[]
for fp in b.GetFootprints():
    for p in fp.Pads():
        bb=p.GetBoundingBox(); chk.append((f(bb.GetX())-0.05,f(bb.GetY())-0.05,f(bb.GetRight())+0.05,f(bb.GetBottom())+0.05,str(p.GetNetname())))
rm2=0
for t in list(b.GetTracks()):
    if t.GetClass()=="PCB_VIA": continue
    n=str(t.GetNetname())
    for pt in (t.GetStart(),t.GetEnd()):
        x,y=f(pt.x),f(pt.y)
        bad=[c for c in chk if c[0]<=x<=c[2] and c[1]<=y<=c[3] and c[4]!=n and c[4]!=""]
        if bad: 
            try: b.RemoveNative(t); rm2+=1
            except Exception: pass
            break
print("removed mismatched-net tracks on pads:",rm2)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(OUT)
