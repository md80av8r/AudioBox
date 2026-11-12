import xml.etree.ElementTree as ET, pcbnew, sys
t=ET.parse(sys.argv[2]).getroot()
b=pcbnew.LoadBoard(sys.argv[1])
pf={str(f.GetReference()):f for f in b.GetFootprints()}
missing=[c.get("ref") for c in t.find("components") if c.get("ref") not in pf]
print("missing parts:",missing)
for c in t.find("components"):
    r=c.get("ref")
    if r in pf: pf[r].SetValue(c.findtext("value") or "")
for p in [p for f in b.GetFootprints() for p in f.Pads()]: pass
for n in t.find("nets"):
    name=n.get("name"); item=b.FindNet(name)
    if item is None: item=pcbnew.NETINFO_ITEM(b,name); b.Add(item)
    for x in n:
        r,p=x.get("ref"),x.get("pin")
        if r not in pf: continue
        for q in pf[r].Pads():
            if q.GetNumber()==p or (p=="SH" and q.GetNumber() in ("MP","SH")):
                if p=="SH" and q.GetNumber()=="MP": q.SetNumber("SH")
                q.SetNet(item)
# pads whose net no longer exists in schematic (cleared)
valid={x.get("ref")+"|"+x.get("pin") for n in t.find("nets") for x in n}
cleared=0
for r,f in pf.items():
    for q in f.Pads():
        if q.GetNetname() and (r+"|"+q.GetNumber()) not in valid and q.GetNumber()!="MP" and not str(q.GetNetname()).startswith("unconnected"):
            pass
b.Save(sys.argv[1]); print("nets set, parts",len(pf))
