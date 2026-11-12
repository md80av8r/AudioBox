import pcbnew, math, re
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(W)
fps=[f for f in b.GetFootprints()]
def R(bb): return [bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
KEEP_PREFIX=("U","Q","J-","PTT","HDR","SW","ENC","D3","L2","C-BULK","C-HP","JP-")
vis=[];hidden=0
for f in fps:
    r=str(f.GetReference())
    f.Value().SetVisible(False)
    if r.startswith("H") and len(r)<=2: f.Reference().SetVisible(False); continue
    if r.startswith(KEEP_PREFIX): vis.append(f)
    else: f.Reference().SetVisible(False); hidden+=1
print("hidden refs",hidden,"kept",len(vis))
# obstacles: pads, vias, other visible text, courtyards of all footprints
obst=[]
for f in fps:
    for p in f.Pads(): obst.append(R(p.GetBoundingBox()))
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        p=t.GetPosition(); d=t.GetWidth(pcbnew.F_Cu)/2e6; obst.append([p.x/1e6-d,p.y/1e6-d,p.x/1e6+d,p.y/1e6+d])
for f in fps:
    for g in f.GraphicalItems():
        if g.GetLayer()==pcbnew.F_SilkS:
            bb=g.GetBoundingBox(); obst.append(R(bb))
placed_text=[]
def textbox(cx,cy,s,size=1.0):
    w=len(s)*size*1.05+0.4; h=size+0.3
    return [cx-w/2,cy-h/2,cx+w/2,cy+h/2]
def hit(bx,extra=0.15):
    for o in obst:
        if not (bx[2]+extra<o[0] or bx[0]-extra>o[2] or bx[3]+extra<o[1] or bx[1]-extra>o[3]): return True
    for o in placed_text:
        if not (bx[2]+0.2<o[0] or bx[0]-0.2>o[2] or bx[3]+0.2<o[1] or bx[1]-0.2>o[3]): return True
    return bx[0]<21 or bx[1]<21 or bx[2]>136 or bx[3]>89
unplaced=[]
for f in sorted(vis,key=lambda f:-(f.GetBoundingBox(False).GetWidth()*f.GetBoundingBox(False).GetHeight())):
    t=f.Reference(); s=str(f.GetReference())
    t.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(0); t.SetVisible(True)
    bb=f.GetBoundingBox(False); x0,y0,x1,y1=R(bb); cx,cy=(x0+x1)/2,(y0+y1)/2
    w=len(s)*1.0*1.05+0.4; h=1.4
    cands=[]
    for gap in (0.5,1.0,1.8,2.8):
        cands+=[(cx,y0-gap-h/2),(cx,y1+gap+h/2),(x0-gap-w/2,cy),(x1+gap+w/2,cy),(x0-gap-w/2,y0-gap-h/2),(x1+gap+w/2,y1+gap+h/2),(x0-gap-w/2,y1+gap+h/2),(x1+gap+w/2,y0-gap-h/2)]
    ok=False
    for px,py in cands:
        bx=[px-w/2,py-h/2,px+w/2,py+h/2]
        if not hit(bx):
            t.SetPosition(pcbnew.VECTOR2I(mm(px),mm(py))); placed_text.append(bx); ok=True; break
    if not ok: unplaced.append(s); t.SetVisible(False)
print("refs without a clear spot (hidden):",unplaced)
b.Save(W)
