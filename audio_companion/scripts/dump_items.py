import pcbnew, json, sys
mm=1e6
b=pcbnew.LoadBoard(sys.argv[1]); out=sys.argv[2]
items=[]
for f in b.GetFootprints():
    for p in f.Pads():
        bb=p.GetBoundingBox()
        items.append(dict(k="pad",net=p.GetNetname(),r=[bb.GetX()/mm,bb.GetY()/mm,bb.GetRight()/mm,bb.GetBottom()/mm],
            F=p.IsOnLayer(pcbnew.F_Cu),B=p.IsOnLayer(pcbnew.B_Cu),ref=f.GetReference(),num=p.GetNumber(),
            c=[p.GetPosition().x/mm,p.GetPosition().y/mm]))
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        items.append(dict(k="via",net=t.GetNetname(),c=[t.GetPosition().x/mm,t.GetPosition().y/mm],d=t.GetWidth(pcbnew.F_Cu)/mm if hasattr(t,"GetWidth") else 0.6))
    else:
        items.append(dict(k="trk",net=t.GetNetname(),a=[t.GetStart().x/mm,t.GetStart().y/mm],b=[t.GetEnd().x/mm,t.GetEnd().y/mm],w=t.GetWidth()/mm,L="F" if t.GetLayer()==pcbnew.F_Cu else "B"))
json.dump(items,open(out,"w"))
print("items",len(items))
