import pcbnew, json, sys
mm=pcbnew.FromMM
b=pcbnew.LoadBoard(sys.argv[1]); data=json.load(open(sys.argv[2]))
for r in data["routes"]:
    ni=b.FindNet(r["net"])
    for pl in r["polys"]:
        for i in range(len(pl)-1):
            t=pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(mm(pl[i][0]),mm(pl[i][1]))); t.SetEnd(pcbnew.VECTOR2I(mm(pl[i+1][0]),mm(pl[i+1][1])))
            t.SetWidth(mm(r["tw"])); t.SetLayer(pcbnew.F_Cu if pl[i][2]=="F" else pcbnew.B_Cu); t.SetNet(ni); b.Add(t)
    for v in r["vias"]:
        via=pcbnew.PCB_VIA(b); via.SetPosition(pcbnew.VECTOR2I(mm(v[0]),mm(v[1]))); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetNet(ni)
        via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
        try: via.SetWidth(mm(0.4))
        except Exception: via.SetWidth(pcbnew.F_Cu,mm(0.4))
        via.SetDrill(mm(0.2)); b.Add(via)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[3]); print("applied",len(data["routes"]))
