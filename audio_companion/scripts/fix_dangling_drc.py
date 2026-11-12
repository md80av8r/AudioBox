import pcbnew, sys, re, math
b=pcbnew.LoadBoard(sys.argv[1]); rpt=open(sys.argv[2]).read(); out=sys.argv[3]
f=lambda v:v/1e6
items=re.findall(r"\[(track_dangling|via_dangling)\]:.*?\n.*?\n\s+@\(([\d.\-]+) mm, ([\d.\-]+) mm\): (Track|Via) \[([^\]]*)\] on ([\w.]+)",rpt)
rm=0
for kind,x,y,what,net,layer in items:
    x,y=float(x),float(y)
    for t in list(b.GetTracks()):
        if str(t.GetNetname())!=net: continue
        if what=="Via":
            if t.GetClass()=="PCB_VIA" and math.hypot(f(t.GetPosition().x)-x,f(t.GetPosition().y)-y)<0.05: b.RemoveNative(t); rm+=1; break
        elif t.GetClass()!="PCB_VIA" and t.GetLayerName()==layer:
            for e in (t.GetStart(),t.GetEnd()):
                if math.hypot(f(e.x)-x,f(e.y)-y)<0.05: b.RemoveNative(t); rm+=1; break
            else: continue
            break
# duplicate vias (same net, centres within 0.3 mm): keep one
vias=[t for t in b.GetTracks() if t.GetClass()=="PCB_VIA"]; dead=set()
for i,a in enumerate(vias):
    for c in vias[i+1:]:
        if c.m_Uuid.AsString() in dead: continue
        if str(a.GetNetname())==str(c.GetNetname()) and math.hypot(f(a.GetPosition().x)-f(c.GetPosition().x),f(a.GetPosition().y)-f(c.GetPosition().y))<0.3: dead.add(c.m_Uuid.AsString())
for v in vias:
    if v.m_Uuid.AsString() in dead: b.RemoveNative(v); rm+=1
print("removed:",rm)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(out)
