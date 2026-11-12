import pcbnew, math, xml.etree.ElementTree as ET
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
S="/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad/"
b=pcbnew.LoadBoard(W); t=ET.parse(S+"net7.xml").getroot()
fp={str(f.GetReference()):f for f in b.GetFootprints()}
# nets for the new names
nets={}
for n in t.find("nets"):
    name=n.get("name"); item=b.FindNet(name)
    if item is None: item=pcbnew.NETINFO_ITEM(b,name); b.Add(item)
    nets[name]=item
# 1. reassign preamp-output copper BEFORE touching pads
old=b.FindNet("Net-(C26-Pad2)"); new=nets["/MIC_PREAMP_OUT"]
n_re=0
for tr in b.GetTracks():
    if str(tr.GetNetname())=="Net-(C26-Pad2)": tr.SetNet(new); n_re+=1
print("reassigned",n_re)
# 2. pad nets
for n in t.find("nets"):
    for x in n:
        r,p=x.get("ref"),x.get("pin")
        for q in fp[r].Pads():
            if str(q.GetNumber())==p or (p=="SH" and str(q.GetNumber())=="SH"): q.SetNet(nets[n.get("name")])
# 3. strip old MIC_AMPLIFIED copper except at U1 escape
u=fp["U1"].GetPosition(); ux,uy=u.x/1e6,u.y/1e6
rm=0
for tr in list(b.GetTracks()):
    if str(tr.GetNetname())!="/MIC_AMPLIFIED": continue
    pts=[tr.GetPosition()] if tr.GetClass()=="PCB_VIA" else [tr.GetStart(),tr.GetEnd()]
    if not any(math.hypot(p.x/1e6-ux,p.y/1e6-uy)<4.6 for p in pts): b.RemoveNative(tr); rm+=1
print("removed",rm)
# 4. copper-aware placement near C26
obst=[]  # rects
def R(bb): return [bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
c=fp["C-MIC-AIR-1"]
for r,f in fp.items():
    if r=="C-MIC-AIR-1": continue
    for q in f.Pads(): obst.append(R(q.GetBoundingBox()))
    if r.startswith("H"):
        p=f.GetPosition(); obst.append([p.x/1e6-3.6,p.y/1e6-3.6,p.x/1e6+3.6,p.y/1e6+3.6])
for tr in b.GetTracks():
    if tr.GetClass()=="PCB_VIA":
        p=tr.GetPosition(); d=tr.GetWidth(pcbnew.F_Cu)/2e6 if hasattr(tr,'GetWidth') else 0.3; obst.append([p.x/1e6-d,p.y/1e6-d,p.x/1e6+d,p.y/1e6+d])
    else:
        a,e=tr.GetStart(),tr.GetEnd(); w=tr.GetWidth()/2e6
        obst.append([min(a.x,e.x)/1e6-w,min(a.y,e.y)/1e6-w,max(a.x,e.x)/1e6+w,max(a.y,e.y)/1e6+w])
bb=c.GetBoundingBox(False); hw=bb.GetWidth()/2e6; hh=bb.GetHeight()/2e6
a=fp["C26"].GetPosition(); ax,ay=a.x/1e6,a.y/1e6
def hit(cc):
    for o in obst:
        if not (cc[2]+0.35<o[0] or cc[0]-0.35>o[2] or cc[3]+0.35<o[1] or cc[1]-0.35>o[3]): return True
    # U1 keepout box
    if not (cc[2]<ux-4.6 or cc[0]>ux+4.6 or cc[3]<uy-4.6 or cc[1]>uy+4.6): return True
    return cc[0]<21 or cc[1]<21 or cc[2]>136 or cc[3]>89
placed=False
for rad in [x*0.25 for x in range(8,160)]:
    n=max(8,int(rad*8))
    for k in range(n):
        ang=2*math.pi*k/n; x=ax+rad*math.cos(ang); y=ay+rad*math.sin(ang)
        cc=[x-hw,y-hh,x+hw,y+hh]
        if not hit(cc): c.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y))); placed=True; print("placed",round(x,2),round(y,2),"C26 at",round(ax,1),round(ay,1)); break
    if placed: break
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(W)
