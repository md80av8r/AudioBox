import pcbnew, sys
mm=pcbnew.FromMM
b=pcbnew.LoadBoard(sys.argv[1]); x0,y0,x1,y1=[float(v) for v in sys.argv[3:7]]
keep={"GND","/+3V3"}
n=0
for t in list(b.GetTracks()):
    if t.GetNetname() in keep: continue
    pts=[t.GetStart(),t.GetEnd()] if t.GetClass()!="PCB_VIA" else [t.GetPosition()]
    if any(x0<=p.x/1e6<=x1 and y0<=p.y/1e6<=y1 for p in pts):
        b.RemoveNative(t); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("stripped",n)
