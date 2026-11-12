import pcbnew, math
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(W)
for t in list(b.GetTracks()): b.RemoveNative(t)
NETS={"GND","/+3V3","/AGND"}
CLR=0.2; VD=0.6; VDR=0.3; TW=0.25
EX0,EY0,EX1,EY1=20.0,20.0,137.0,90.0
def rect(bb): return [bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
obst=[]  # (rect,net)
for f in b.GetFootprints():
    for p in f.Pads(): obst.append((rect(p.GetBoundingBox()),p.GetNetname(),p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD))
    if f.GetReference()=="REF**": pass
def hit(c,net,clr=CLR):
    if c[0]<EX0+0.6 or c[1]<EY0+0.6 or c[2]>EX1-0.6 or c[3]>EY1-0.6: return True
    for r,n,_ in obst:
        if n==net and n!="": continue
        if not (c[2]+clr<r[0] or c[0]-clr>r[2] or c[3]+clr<r[1] or c[1]-clr>r[3]): return True
    return False
def segfree(a,c,net):
    n=12
    for i in range(n+1):
        x=a[0]+(c[0]-a[0])*i/n; y=a[1]+(c[1]-a[1])*i/n
        if hit([x-TW/2,y-TW/2,x+TW/2,y+TW/2],net,0.15): return False
    return True
def addvia(x,y,net):
    v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y))); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetNet(b.FindNet(net)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
    try: v.SetWidth(mm(VD))
    except Exception: v.SetWidth(pcbnew.F_Cu,mm(VD))
    v.SetDrill(mm(VDR)); b.Add(v)
    obst.append(([x-VD/2,y-VD/2,x+VD/2,y+VD/2],'__via__',False))
def addtrack(a,c,net):
    t=pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(mm(a[0]),mm(a[1]))); t.SetEnd(pcbnew.VECTOR2I(mm(c[0]),mm(c[1])))
    t.SetWidth(mm(TW)); t.SetLayer(pcbnew.F_Cu); t.SetNet(b.FindNet(net)); b.Add(t)
    x0,x1=sorted((a[0],c[0])); y0,y1=sorted((a[1],c[1]))
    obst.append(([x0-TW/2,y0-TW/2,x1+TW/2,y1+TW/2],net,False))
n_ok=n_fail=0; fails=[]
for f in b.GetFootprints():
    for p in f.Pads():
        net=p.GetNetname()
        if net not in NETS or p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD: continue
        if p.GetLayerSet().Contains(pcbnew.F_Cu)==False: continue
        c=p.GetPosition(); cx,cy=c.x/1e6,c.y/1e6; r=rect(p.GetBoundingBox()); w=r[2]-r[0]; h=r[3]-r[1]
        if w>2 and h>2:  # exposed pad: via grid inside
            for dx in (-0.7,0.7):
                for dy in (-0.7,0.7): addvia(cx+dx,cy+dy,net)
            n_ok+=1; continue
        done=False
        for dist in [0.9+0.15*k for k in range(10)]:
            for k in range(16):
                ang=2*math.pi*k/16
                # offset from pad edge in direction ang
                ex=max(w/2,0.0)*math.cos(ang)/max(abs(math.cos(ang)),1e-9) if abs(math.cos(ang))>abs(math.sin(ang)) else 0
                vx=cx+math.cos(ang)*(dist+ (w/2 if abs(math.cos(ang))>0.7 else 0.0))
                vy=cy+math.sin(ang)*(dist+ (h/2 if abs(math.sin(ang))>0.7 else 0.0))
                vc=[vx-VD/2,vy-VD/2,vx+VD/2,vy+VD/2]
                if hit(vc,net): continue
                if not segfree((cx,cy),(vx,vy),net): continue
                addtrack((cx,cy),(vx,vy),net); addvia(vx,vy,net); done=True; break
            if done: break
        if done: n_ok+=1
        else: n_fail+=1; fails.append((f.GetReference(),p.GetNumber(),net))
print("fanned",n_ok,"failed",n_fail,fails)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(W)
