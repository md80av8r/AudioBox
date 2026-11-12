import pcbnew, math
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(W)
CL=0.127
def net(x): return str(x.GetNetname())
def rect(bb): return [bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
def prect(p): return rect(p.GetBoundingBox())
def dist_pt_rect(x,y,r):
    dx=max(r[0]-x,0,x-r[2]); dy=max(r[1]-y,0,y-r[3]); return math.hypot(dx,dy)
def dist_pt_seg(px,py,a,c):
    dx,dy=c[0]-a[0],c[1]-a[1]; L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-a[0])*dx+(py-a[1])*dy)/L)); return math.hypot(px-(a[0]+t*dx),py-(a[1]+t*dy))
allpads=[(str(f.GetReference()),p,prect(p),net(p),p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD) for f in b.GetFootprints() for p in f.Pads()]
def tracks_vias():
    T=[];V=[]
    for t in b.GetTracks():
        if t.GetClass()=="PCB_VIA": V.append(t)
        else: T.append(t)
    return T,V
def free_point(x,y,r,n,skipvia=None):
    if x<20.8 or y<20.8 or x>136.2 or y>89.2: return False
    for ref,p,rc,pn,tht in allpads:
        if dist_pt_rect(x,y,rc)<r+0.15: return False
    T,V=tracks_vias()
    for v in V:
        if v is skipvia: continue
        vp=v.GetPosition(); rv=v.GetWidth(pcbnew.F_Cu)/2e6
        if net(v)!=n and math.hypot(vp.x/1e6-x,vp.y/1e6-y)<r+rv+CL+0.05: return False
        if net(v)==n and math.hypot(vp.x/1e6-x,vp.y/1e6-y)<r+rv+0.1: return False
    for t in T:
        if net(t)==n: continue
        a=(t.GetStart().x/1e6,t.GetStart().y/1e6); c=(t.GetEnd().x/1e6,t.GetEnd().y/1e6)
        if dist_pt_seg(x,y,a,c)<r+t.GetWidth()/2e6+CL+0.05: return False
    return True
def seg_free(a,c,tw,n,layer,hostpads):
    T,V=tracks_vias()
    steps=max(2,int(math.hypot(c[0]-a[0],c[1]-a[1])/0.1))
    for i in range(steps+1):
        x=a[0]+(c[0]-a[0])*i/steps; y=a[1]+(c[1]-a[1])*i/steps
        if layer=="F":
            for ref,p,rc,pn,tht in allpads:
                if pn==n: continue
                if dist_pt_rect(x,y,rc)<tw/2+CL: return False
        for v in V:
            if net(v)==n: continue
            vp=v.GetPosition(); rv=v.GetWidth(pcbnew.F_Cu)/2e6
            if math.hypot(vp.x/1e6-x,vp.y/1e6-y)<rv+tw/2+CL: return False
        for t in T:
            if net(t)==n: continue
            if (t.GetLayer()==pcbnew.F_Cu)!=(layer=="F"): continue
            tc=(t.GetStart().x/1e6,t.GetStart().y/1e6); te=(t.GetEnd().x/1e6,t.GetEnd().y/1e6)
            if dist_pt_seg(x,y,tc,te)<tw/2+t.GetWidth()/2e6+CL: return False
    return True
def attached_layers(p,n):
    L=set()
    for t in b.GetTracks():
        if t.GetClass()=="PCB_VIA" or net(t)!=n: continue
        for e in (t.GetStart(),t.GetEnd()):
            if math.hypot(e.x/1e6-p[0],e.y/1e6-p[1])<0.06: L.add("F" if t.GetLayer()==pcbnew.F_Cu else "B")
    return L
def add_track(a,c,w,layer,n):
    t=pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(mm(a[0]),mm(a[1]))); t.SetEnd(pcbnew.VECTOR2I(mm(c[0]),mm(c[1])))
    t.SetWidth(mm(w)); t.SetLayer(pcbnew.F_Cu if layer=="F" else pcbnew.B_Cu); t.SetNet(b.FindNet(n)); b.Add(t)
def move_via(v,need_front_stub=True):
    p=(v.GetPosition().x/1e6,v.GetPosition().y/1e6); n=net(v); r=v.GetWidth(pcbnew.F_Cu)/2e6
    tw=0.4 if n in ("/+12V","/+BATT") else 0.2
    layers=attached_layers(p,n)
    for dist in [0.8+0.15*k for k in range(14)]:
        for k in range(24):
            ang=2*math.pi*k/24; q=(p[0]+dist*math.cos(ang),p[1]+dist*math.sin(ang))
            if not free_point(q[0],q[1],r,n,skipvia=v): continue
            if need_front_stub and not seg_free(p,q,tw,n,"F",None): continue
            if "B" in layers and not seg_free(p,q,tw,n,"B",None): continue
            v.SetPosition(pcbnew.VECTOR2I(mm(q[0]),mm(q[1])))
            if need_front_stub: add_track(p,q,tw,"F",n)
            if "B" in layers: add_track(p,q,tw,"B",n)
            return q
    return None
T,V=tracks_vias()
def find_via(x,y,n):
    for v in V:
        vp=v.GetPosition()
        if abs(vp.x/1e6-x)<0.06 and abs(vp.y/1e6-y)<0.06 and net(v)==n: return v
# 1. single vias in small passive pads + edge-overlap vias
todo=[(130.45,35.45,"/+12V"),(55.64,70.17,"/AGND"),(66.24,41.96,"Net-(J-35-3-Pin_2)"),(71.45,31.62,"/ADCVREF"),(63.37,29.45,"/AGND"),(67.49,28.74,"Net-(J-35-1-Pin_1)"),(129.62,33.55,"GND")]
for x,y,n in todo:
    v=find_via(x,y,n)
    if v is None: print("not found",x,y,n); continue
    q=move_via(v); print("via",n,(x,y),"->",None if q is None else (round(q[0],2),round(q[1],2)))
# 2. tantalum C-BULK-3V3: remove in-pad vias, add 2 outside per pad with stubs
T,V=tracks_vias()
cb=[f for f in b.GetFootprints() if str(f.GetReference())=="C-BULK-3V3"][0]
rem=0
for v in list(V):
    vp=v.GetPosition(); x,y=vp.x/1e6,vp.y/1e6
    for p in cb.Pads():
        if dist_pt_rect(x,y,prect(p))==0 and net(v)==net(p): b.RemoveNative(v); rem+=1; break
print("removed",rem,"vias from C-BULK-3V3 pads")
for p in cb.Pads():
    n=net(p); c=p.GetPosition(); c=(c.x/1e6,c.y/1e6); added=0
    for dist in [1.9+0.2*k for k in range(10)]:
        for k in range(24):
            ang=2*math.pi*k/24; q=(c[0]+dist*math.cos(ang),c[1]+dist*math.sin(ang))
            if added>=2: break
            if not free_point(q[0],q[1],0.2,n): continue
            if not seg_free(c,q,0.4,n,"F",None): continue
            v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(q[0]),mm(q[1]))); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(b.FindNet(n)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
            try: v.SetWidth(mm(0.4))
            except Exception: v.SetWidth(pcbnew.F_Cu,mm(0.4))
            v.SetDrill(mm(0.2)); b.Add(v); add_track(c,q,0.4,"F",n); added+=1
        if added>=2: break
    print("C-BULK pad",p.GetNumber(),n,"vias added",added)
# 3. U1 exposed-pad vias: shrink to 0.4/0.2
T,V=tracks_vias(); u1=[f for f in b.GetFootprints() if str(f.GetReference())=="U1"][0]; ep=[p for p in u1.Pads() if str(p.GetNumber())=="29"][0]; cnt=0
for v in V:
    vp=v.GetPosition()
    if dist_pt_rect(vp.x/1e6,vp.y/1e6,prect(ep))==0:
        try: v.SetWidth(mm(0.4))
        except Exception: v.SetWidth(pcbnew.F_Cu,mm(0.4))
        v.SetDrill(mm(0.2)); cnt+=1
print("U1 EP vias resized to 0.4/0.2:",cnt)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(W)
