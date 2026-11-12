import pcbnew, math, re
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(W)
fp={f.GetReference():f for f in b.GetFootprints() if f.GetReference()!="REF**"}
holes=[f for f in b.GetFootprints() if f.GetReference()=="REF**"]
X0,Y0,X1,Y1=20,20,137,90
def court(f):
    bb=f.GetBoundingBox(False)  # no text
    return [bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
def setpos(r,x,y,rot=None):
    f=fp[r]
    if rot is not None: f.SetOrientationDegrees(rot)
    f.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y)))
# 1. anchors
setpos("D4",64,24,0);setpos("D5",69,24,0);setpos("D6",74,24,0);setpos("D7",79,24,0)
setpos("J-AIRCRAFT-1",27,38,90)
# power cluster top-right
setpos("U6",124,30,0); setpos("L2",117.7,30,0); setpos("D3",122.5,35,180); setpos("C46",128,34.5,90); setpos("C51",130.5,34.5,90)
setpos("J-BAT-1",131,24,0)
# haptic
setpos("U2",100,56,0)
# user controls right-middle
setpos("ENC1",126,65,0); setpos("SW-PWR-1",116.5,48,0); setpos("SW-BYPASS-1",130.5,47,0); setpos("U3",112,46,0)
fixed=set(["C46","C51","HDR-CP-L-1","HDR-CP-R-1","U1","U5","U8","Q1","MIC_BYPASS-1","HEADPHONE_BYPASS-1","J-LEMO-1","J-HAPTIC-1","D4","D5","D6","D7","J-AIRCRAFT-1","U6","L2","D3","J-BAT-1","U2","ENC1","SW-PWR-1","SW-BYPASS-1","U3"])
fixed|={r for r in fp if r.startswith("J-") or r.startswith("PTT")}
fixed|={"D1","D2"}
placed=[court(fp[r]) for r in fixed]
for h in holes:
    p=h.GetPosition(); x,y=p.x/1e6,p.y/1e6; placed.append([x-3.6,y-3.6,x+3.6,y+3.6])
u1=fp['U1'].GetPosition(); placed.append([u1.x/1e6-4.6,u1.y/1e6-4.6,u1.x/1e6+4.6,u1.y/1e6+4.6])
def free(c,skip=None):
    if c[0]<X0+1 or c[1]<Y0+1 or c[2]>X1-1 or c[3]>Y1-1: return False
    for p in placed:
        if not (c[2]+0.6<p[0] or c[0]-0.6>p[2] or c[3]+0.6<p[1] or c[1]-0.6>p[3]): return False
    return True
# anchors for passives: nearest non-passive pad on one of its non-ground nets
def isP(r): return re.match(r'^(C|R|FB|L)[\w-]*$',r) is not None and r not in fixed
pas=[r for r in fp if isP(r)]
ics=[f for r,f in fp.items() if r in fixed]
gnd={"GND","AGND"}
pads_by_net={}
for r,f in fp.items():
    if r in pas: continue
    for p in f.Pads():
        n=p.GetNetname()
        if n and n not in gnd: pads_by_net.setdefault(n,[]).append((r,p))
def anchor(r):
    f=fp[r]; cur=f.GetPosition(); best=None
    for p in f.Pads():
        n=p.GetNetname()
        if n in gnd or n not in pads_by_net: continue
        for rr,q in pads_by_net[n]:
            if not (rr.startswith("HDR") or rr.startswith("J-")) or True:
                d=math.hypot(q.GetPosition().x-cur.x,q.GetPosition().y-cur.y)
                # prefer ICs over connectors, small penalty
                if rr.startswith("J-") or rr.startswith("HDR"): d+=mm(25)
                if best is None or d<best[0]: best=(d,q.GetPosition(),rr)
    return best
order=sorted(pas,key=lambda r:(anchor(r) or (1e18,))[0])
fails=[]
for r in order:
    a=anchor(r)
    if a is None: fails.append(r); continue
    ax,ay=a[1].x/1e6,a[1].y/1e6
    f=fp[r]; w=court(f); hw=(w[2]-w[0])/2; hh=(w[3]-w[1])/2
    done=False
    minr=0
    for rad in [x*0.25 for x in range(4,160) if x*0.25>=minr]:
        n=max(8,int(rad*8))
        for k in range(n):
            ang=2*math.pi*k/n
            x=ax+rad*math.cos(ang); y=ay+rad*math.sin(ang)
            c=[x-hw,y-hh,x+hw,y+hh]
            if free(c):
                f.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y))); placed.append(c); done=True; break
        if done: break
    if not done: fails.append(r)
def place_near(r,ax,ay):
    f=fp[r]; w=court(f); hw=(w[2]-w[0])/2; hh=(w[3]-w[1])/2
    for rad in [x*0.25 for x in range(4,160)]:
        n=max(8,int(rad*8))
        for k in range(n):
            ang=2*math.pi*k/n; x=ax+rad*math.cos(ang); y=ay+rad*math.sin(ang)
            cc=[x-hw,y-hh,x+hw,y+hh]
            if free(cc): f.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y))); placed.append(cc); return True
    return False
rp=fp["R-ELEC-1"].FindPadByNumber("1").GetPosition()
print("JP placed",place_near("JP-MIC-BIAS",rp.x/1e6,rp.y/1e6))
print("unplaced",fails)
for r in ("U6","PTT_PASS/GND-1"):
    for p in fp[r].Pads(): p.SetOrientationDegrees(0)
for p in fp["J-AIRCRAFT-1"].Pads():
    p.SetOrientationDegrees(90)
n=0
for h in holes:
    n+=1; h.SetReference("H%d"%n)
if "C24" in fp and (fp["C24"].GetPosition().x/1e6<60): pass
b.Save(W)
