import pcbnew, math
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(W)
# idempotent: remove earlier pin letters (marked by a trailing "." in a private user-text)
old=[d for d in b.GetDrawings() if d.GetClass()=="PCB_TEXT" and str(d.GetText()).startswith("⁠")]
for d in old: b.RemoveNative(d)
b.Save(W); b=pcbnew.LoadBoard(W)
fp={str(f.GetReference()):f for f in b.GetFootprints()}
def R(bb): return [bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
obst=[]
for f in fp.values():
    for p in f.Pads(): obst.append(R(p.GetBoundingBox()))
    for g in f.GraphicalItems():
        if g.GetLayer()==pcbnew.F_SilkS: obst.append(R(g.GetBoundingBox()))
    if f.Reference().IsVisible(): obst.append(R(f.Reference().GetBoundingBox()))
for d in b.GetDrawings():
    if d.GetClass()=="PCB_TEXT" and d.GetLayer()==pcbnew.F_SilkS: obst.append(R(d.GetBoundingBox()))
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        p=t.GetPosition(); d=t.GetWidth(pcbnew.F_Cu)/2e6; obst.append([p.x/1e6-d,p.y/1e6-d,p.x/1e6+d,p.y/1e6+d])
placed=[]
def hit(bx):
    for o in obst:
        if not (bx[2]+0.15<o[0] or bx[0]-0.15>o[2] or bx[3]+0.15<o[1] or bx[1]-0.15>o[3]): return True
    for o in placed:
        if not (bx[2]+0.1<o[0] or bx[0]-0.1>o[2] or bx[3]+0.1<o[1] or bx[1]-0.1>o[3]): return True
    return bx[0]<21 or bx[1]<21 or bx[2]>136 or bx[3]>89
M={ "J-35-1":"LRG","J-35-2":"LRG","J-35-3":"LRG","J-635-IN-1":"LRG","J-AIRCRAFT-1":"LRGMP","J-BAT-1":"+-","J-BTN-1":"SG","J-BTN-IN-1":"+S.G","J-HAPTIC-1":"+-","J-LEMO-1":"LGRMG+","J-MIC-IN-1":"MG","PTT_PASS/GND-1":"PG" }
miss=[]
for ref,letters in M.items():
    f=fp[ref]; pads=sorted([p for p in f.Pads() if str(p.GetNumber()).isdigit()],key=lambda p:int(str(p.GetNumber())))
    ang=round(f.GetOrientationDegrees())%360
    if ref=="J-LEMO-1": dirs=[(1,0),(-1,0)]            # vertical header: letters to the side
    elif ang==270: dirs=[(1,0),(0,-1),(0,1)]          # aircraft: body to the left, letters behind (right)
    elif ref=="J-BAT-1": dirs=[(0,1),(0,-1),(1,0)]
    else: dirs=[(0,-1),(0,1)]                          # body in front (below): letters behind (above)
    for p,ch in zip(pads,letters):
        if ch==".": continue
        px,py=p.GetPosition().x/1e6,p.GetPosition().y/1e6; ok=False
        for dx,dy in dirs:
            for dist in (3.0,3.5,4.0,2.4,2.0):
                cx,cy=px+dx*dist,py+dy*dist; bx=[cx-0.55,cy-0.75,cx+0.55,cy+0.75]
                if not hit(bx):
                    t=pcbnew.PCB_TEXT(b); t.SetText("⁠"+ch); t.SetLayer(pcbnew.F_SilkS); t.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); t.SetTextThickness(mm(0.15))
                    t.SetPosition(pcbnew.VECTOR2I(mm(cx),mm(cy))); b.Add(t); placed.append(bx); ok=True; break
            if ok: break
        if not ok: miss.append((ref,str(p.GetNumber()),ch))
print("pin letters placed:",len(placed),"| no clear spot:",miss)
b.Save(W)
