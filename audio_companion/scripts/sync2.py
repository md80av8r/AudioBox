import xml.etree.ElementTree as ET, pcbnew, os
S="/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad/"
t=ET.parse(S+"net3.xml").getroot()
b=pcbnew.LoadBoard(S+"pre_place.kicad_pcb")
std="/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
_cache={}
def load(fpid):
    if fpid not in _cache:
        lib,name=fpid.split(":")
        _cache[fpid]=pcbnew.FootprintLoad(std+lib+".pretty",name)
    return pcbnew.FOOTPRINT(_cache[fpid])
pf={f.GetReference():f for f in b.GetFootprints()}
for c in t.find("components"):
    r=c.get("ref"); fpid=c.findtext("footprint")
    if r in pf:
        cur=pf[r].GetFPID().GetLibItemName()
        if str(cur)!=fpid.split(":")[1] and r in ("C29","C31","C32","C46"):
            old=pf[r]; new=load(fpid); new.SetReference(r); new.SetValue(c.findtext("value"))
            new.SetPosition(old.GetPosition()); new.SetOrientation(old.GetOrientation()); b.Remove(old); b.Add(new); pf[r]=new; print("replaced",r)
        else: pf[r].SetValue(c.findtext("value"))
    else:
        new=load(fpid); new.SetReference(r); new.SetValue(c.findtext("value"))
        new.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(130),pcbnew.FromMM(60))); b.Add(new); pf[r]=new; print("added",r)
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
b.Save(S+"pre_place2.kicad_pcb"); print("saved")
