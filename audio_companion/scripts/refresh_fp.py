import pcbnew, sys
path,ref=sys.argv[1],sys.argv[2]
b=pcbnew.LoadBoard(path)
old=[f for f in b.GetFootprints() if f.GetReference()==ref][0]
pos,ori,val=old.GetPosition(),old.GetOrientation(),old.GetValue()
nets={p.GetNumber():p.GetNet() for p in old.Pads()}
b.Remove(old)
new=pcbnew.FootprintLoad("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Capacitor_SMD.pretty","C_0805_2012Metric")
new.SetReference(ref); new.SetValue(val); new.SetPosition(pos); new.SetOrientation(ori); b.Add(new)
for p in new.Pads(): p.SetNet(nets[p.GetNumber()])
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(path); print("refreshed",ref)
