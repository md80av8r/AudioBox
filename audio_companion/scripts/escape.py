import pcbnew, sys, math
mm=pcbnew.FromMM
b=pcbnew.LoadBoard(sys.argv[1])
u=[f for f in b.GetFootprints() if f.GetReference()=="U1"][0]
c=u.GetPosition()
skip={""}
side_idx={}
n=0
for p in sorted(u.Pads(),key=lambda p:int(p.GetNumber()) if p.GetNumber().isdigit() else 99):
    num=p.GetNumber()
    if not num.isdigit() or int(num)>28: continue
    net=p.GetNetname()
    if net in skip or net.startswith("unconnected"): continue
    px,py=p.GetPosition().x,p.GetPosition().y
    dx,dy=px-c.x,py-c.y
    if abs(dx)>abs(dy): ux,uy=(1 if dx>0 else -1),0; side="L" if dx<0 else "R"
    else: ux,uy=0,(1 if dy>0 else -1); side="T" if dy<0 else "B"
    k=side_idx.get(side,0); side_idx[side]=k+1
    L=1.0 if int(num)%2==0 else 1.8
    vx,vy=px+ux*mm(L),py+uy*mm(L)
    ni=b.FindNet(net)
    t=pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(px,py)); t.SetEnd(pcbnew.VECTOR2I(int(vx),int(vy))); t.SetWidth(mm(0.15)); t.SetLayer(pcbnew.F_Cu); t.SetNet(ni); b.Add(t)
    v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(int(vx),int(vy))); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(ni); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
    try: v.SetWidth(mm(0.4))
    except Exception: v.SetWidth(pcbnew.F_Cu,mm(0.4))
    v.SetDrill(mm(0.2)); b.Add(v); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("escapes",n)
