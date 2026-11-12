import pcbnew, math
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(W)
# remove previously added labels (idempotent)
_old=[d for d in b.GetDrawings() if d.GetClass()=="PCB_TEXT" and str(d.GetText()).startswith("​")]
for d in _old: b.RemoveNative(d)
b.Save(W); b=pcbnew.LoadBoard(W)
fp={str(f.GetReference()):f for f in b.GetFootprints()}
def R(bb): return [bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
obst=[]
for f in fp.values():
    for p in f.Pads(): obst.append(R(p.GetBoundingBox()))
    for g in f.GraphicalItems():
        if g.GetLayer()==pcbnew.F_SilkS: obst.append(R(g.GetBoundingBox()))
    if f.Reference().IsVisible(): obst.append(R(f.Reference().GetBoundingBox()))
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        p=t.GetPosition(); d=t.GetWidth(pcbnew.F_Cu)/2e6; obst.append([p.x/1e6-d,p.y/1e6-d,p.x/1e6+d,p.y/1e6+d])
placed=[]
def hit(bx):
    for o in obst:
        if not (bx[2]+0.2<o[0] or bx[0]-0.2>o[2] or bx[3]+0.2<o[1] or bx[1]-0.2>o[3]): return True
    for o in placed:
        if not (bx[2]+0.3<o[0] or bx[0]-0.3>o[2] or bx[3]+0.3<o[1] or bx[1]-0.3>o[3]): return True
    return bx[0]<21 or bx[1]<21 or bx[2]>136 or bx[3]>89
def add(text,ref,size=1.0,rot=0,prefer="below",layer=pcbnew.F_SilkS):
    f=fp[ref]; x0,y0,x1,y1=R(f.GetBoundingBox(False)); cx,cy=(x0+x1)/2,(y0+y1)/2
    w=len(text)*size*1.05+0.4; h=size*1.4
    if rot in (90,270): w,h=h,w
    order={"below":[(0,1),(0,-1),(1,0),(-1,0)],"above":[(0,-1),(0,1),(1,0),(-1,0)],"right":[(1,0),(-1,0),(0,1),(0,-1)],"left":[(-1,0),(1,0),(0,1),(0,-1)]}[prefer]
    for gap in (0.4,0.9,1.6,2.6,3.8):
        for dx,dy in order:
            px=cx+dx*((x1-x0)/2+gap+w/2) if dx else cx
            py=cy+dy*((y1-y0)/2+gap+h/2) if dy else cy
            bx=[px-w/2,py-h/2,px+w/2,py+h/2]
            if not hit(bx):
                t=pcbnew.PCB_TEXT(b); t.SetText("​"+text); t.SetLayer(layer)
                t.SetTextSize(pcbnew.VECTOR2I(mm(size),mm(size))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(rot)
                t.SetPosition(pcbnew.VECTOR2I(mm(px),mm(py))); b.Add(t); placed.append(bx); return True
    print("NO SPOT for",text); return False
labels=[("ATC BTN","J-BTN-1","below",0),("PTT","PTT_PASS/GND-1","below",0),("MIC","J-MIC-IN-1","below",0),("LINE IN","J-35-1","below",0),("LINE OUT","J-35-2","below",0),
 ("CP J13","J-BTN-IN-1","below",0),("PHONES","J-635-IN-1","below",0),("OUT 2","J-35-3","below",0),("LEMO","J-LEMO-1","left",90),("AIRCRAFT","J-AIRCRAFT-1","above",0),
 ("HAPTIC","J-HAPTIC-1","below",0),("BATT","J-BAT-1","below",0),("PWR","D4","above",0),("ACT","D5","above",0),("ANR","D6","above",0),("BYP","D7","above",0),
 ("PWR","SW-PWR-1","below",0),("BYPASS","SW-BYPASS-1","below",0),("ENC","ENC1","above",0),("BIAS","JP-MIC-BIAS-1","below",0),("CP-L","HDR-CP-L-1","above",0),("CP-R","HDR-CP-R-1","above",0),
 ("HP RELAY","HEADPHONE_BYPASS-1","below",0),("MIC RELAY","MIC_BYPASS-1","above",0)]
for t,r,p,rot in labels: add(t,r,1.0,rot,p)
# board ID on front in a free area
def free_area(w,h):
    for y in [v*1.0 for v in range(22,86)]:
        for x in [v*1.0 for v in range(24,132)]:
            bx=[x,y,x+w,y+h]
            if not hit(bx): return bx
    return None
bx=free_area(23,4.6)
if bx:
    for i,s in enumerate(("MD-88 AUDIO COMPANION","REV D 2026")):
        t=pcbnew.PCB_TEXT(b); t.SetText("​"+s); t.SetLayer(pcbnew.F_SilkS); t.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); t.SetTextThickness(mm(0.15))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT); t.SetPosition(pcbnew.VECTOR2I(mm(bx[0]),mm(bx[1]+0.8+i*1.6))); b.Add(t)
    placed.append(bx); print("board ID at",[round(v,1) for v in bx])
# back side: aircraft pinout key + id (mirrored)
back=[("AIRCRAFT CONNECTOR J-AIRCRAFT-1",80,60),("1 HP-L  2 HP-R  3 GND",80,62),("4 MIC  5 PTT",80,64),("PIN 1 = TOP (NEAR HEADERS)",80,66),("BATT J-BAT-1: PIN 1 (+)",80,70),("MD-88 AUDIO COMPANION REV D",80,74)]
for s,x,y in back:
    t=pcbnew.PCB_TEXT(b); t.SetText("​"+s); t.SetLayer(pcbnew.B_SilkS); t.SetMirrored(True)
    t.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); t.SetTextThickness(mm(0.15)); t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    t.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y))); b.Add(t)
b.Save(W); print("labels placed:",len(placed))
