import sys; sys.path.insert(0,"/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/scripts")
from pcb_tp import *
skip=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}   # ref -> list of "x,y" already rejected
b=base(); hdr=add_header(b,104.14,43.5)
print("hdr pads",[(p.GetNumber(),round(fmm(p.GetPosition().x),2),round(fmm(p.GetPosition().y),2),p.GetNetname()) for p in hdr.Pads()])
placed={}; placed_net={}
for ref,net,label in TPS:
    occ,X0,Y0=occ_bcu(b,net)
    tried={tuple(map(float,s.split(","))) for s in skip.get(ref,[])}
    extra=[(x,37.95) for x in range(86,106,2)] if net=="/+3V3_A" else None
    cs=cands(b,net,occ,X0,Y0,tried,extra)
    cs=[c for c in cs if all(math.hypot(c[1]-q[0],c[2]-q[1])>(25 if placed_net.get(r)==net else 5) for r,q in placed.items() for q in [q[:2]] if True) ]
    cs=[c for c in cs if not any(placed_net.get(r)==net and math.hypot(c[1]-q[0],c[2]-q[1])<25 for r,q in placed.items())]
    if not cs: print("NO CANDIDATE",ref,net); continue
    d,x,y,anc=cs[0]; 
    if extra:
        v=pcbnew.PCB_VIA(b); v.SetPosition(V(*anc)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(b.FindNet(net)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetWidth(pcbnew.F_Cu,mm(0.4)); v.SetDrill(mm(0.2)); b.Add(v)
    add_tp(b,ref,net,label,x,y,anc); placed_net[ref]=net; placed[ref]=(x,y,anc,label); print(ref,net,"at",x,y,"anchor",anc,"d",d)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(OUT)
json.dump(placed,open(S+"/tp_placed.json","w"))
