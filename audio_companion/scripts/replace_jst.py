import pcbnew, sys, math, json
path,ref,n=sys.argv[1],sys.argv[2],int(sys.argv[3])
mm=pcbnew.FromMM
b=pcbnew.LoadBoard(path)
old=[f for f in b.GetFootprints() if str(f.GetReference())==ref][0]
digit=[p for p in old.Pads() if str(p.GetNumber()).isdigit()]
cx=sum(p.GetPosition().x for p in digit)/len(digit); cy=sum(p.GetPosition().y for p in digit)/len(digit)
ox,oy=old.GetPosition().x,old.GetPosition().y
nets={str(p.GetNumber()):p.GetNet() for p in digit}
val=str(old.GetValue()); ang=old.GetOrientationDegrees()
b.Remove(old)
new=pcbnew.FootprintLoad("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_JST.pretty","JST_PH_S%dB-PH-K_1x%02d_P2.00mm_Horizontal"%(n,n))
new.SetReference(ref); new.SetValue("S%dB-PH-K-S"%n)
theta=ang
tx,ty=cx,cy
if ref=="J-AIRCRAFT-1":
    theta=270; tx=2*ox-cx   # mirror pin row to the interior side so the mating opening faces the left board edge
new.SetOrientationDegrees(theta); new.SetPosition(pcbnew.VECTOR2I(0,0))
lc=[(p.GetPosition().x,p.GetPosition().y) for p in new.Pads() if str(p.GetNumber()).isdigit()]
lx=sum(a for a,_ in lc)/len(lc); ly=sum(c for _,c in lc)/len(lc)
new.SetPosition(pcbnew.VECTOR2I(int(tx-lx),int(ty-ly)))
b.Add(new)
for p in new.Pads():
    if str(p.GetNumber()) in nets: p.SetNet(nets[str(p.GetNumber())])
bb=new.GetBoundingBox(False)
box=[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
b.Save(path); print(ref,"theta",theta,"pads at",[(str(p.GetNumber()),round(p.GetPosition().x/1e6,2),round(p.GetPosition().y/1e6,2)) for p in new.Pads()][:5],"bbox",[round(v,1) for v in box])
