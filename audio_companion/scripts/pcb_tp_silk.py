import pcbnew, math, json
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work"; P=W+"/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(P); mm=pcbnew.FromMM; V=lambda x,y: pcbnew.VECTOR2I(mm(x),mm(y)); f=lambda v:v/1e6
LAB={"TP1":"GND","TP2":"GND","TP3":"3V3","TP4":"3V3A","TP5":"12V","TP6":"AGND","TP7":"SDA"}
obst=[]  # exposed copper / silk rects on bottom
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD or p.IsOnLayer(pcbnew.B_Cu):
            bb=p.GetBoundingBox(); obst.append((f(bb.GetX()),f(bb.GetY()),f(bb.GetRight()),f(bb.GetBottom())))
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        x,y=f(t.GetPosition().x),f(t.GetPosition().y); obst.append((x-0.3,y-0.3,x+0.3,y+0.3))
for d in b.GetDrawings():
    if d.GetLayerName()=="B.SilkS":
        bb=d.GetBoundingBox(); obst.append((f(bb.GetX()),f(bb.GetY()),f(bb.GetRight()),f(bb.GetBottom())))
def hit(r,m=0.25): return any(not(r[2]+m<o[0] or r[0]-m>o[2] or r[3]+m<o[1] or r[1]-m>o[3]) for o in obst)
have={t.GetText() for t in b.GetDrawings() if t.GetLayerName()=="B.SilkS"}
for ref,txt in LAB.items():
    if ref in ("TP2","TP3","TP4","TP5","TP7"): continue
    fp=b.FindFootprintByReference(ref); px,py=f(fp.GetPosition().x),f(fp.GetPosition().y)
    w=len(txt)*0.95; h=1.2
    opts=[]
    cl=[(0,-1.9),(0,1.9),(w/2+1.2,0),(-(w/2+1.2),0),(w/2+1.0,-1.5),(-(w/2+1.0),-1.5),(w/2+1.0,1.5),(-(w/2+1.0),1.5)]
    for rr in (2.6,3.4,4.2):
        for k in range(0,360,30): cl.append((rr*math.cos(math.radians(k)),rr*math.sin(math.radians(k))))
    for dx,dy in cl:
        cx,cy=px+dx,py+dy; r=(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
        # is an obstacle only via others; exclude own pad
        if not hit(r) and 21.5<cx<135.5 and 21.5<cy<88.5: opts.append((cx,cy)); break
    if not opts: print("NO SPOT",ref); continue
    cx,cy=opts[0]
    t=pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetLayer(pcbnew.B_SilkS); t.SetMirrored(True); t.SetPosition(V(cx,cy))
    t.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); t.SetTextThickness(mm(0.15)); b.Add(t)
    bb=t.GetBoundingBox(); obst.append((f(bb.GetX()),f(bb.GetY()),f(bb.GetRight()),f(bb.GetBottom()))); print(ref,txt,round(cx,1),round(cy,1))
b.Save(P)
