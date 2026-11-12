import xml.etree.ElementTree as ET, pcbnew, os, re
S="/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad/"
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/"
t=ET.parse(S+"net2.xml").getroot()
b=pcbnew.LoadBoard(W+"audio_companion.kicad_pcb")
pf={f.GetReference():f for f in b.GetFootprints()}
# lib paths
std="/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
def load(fpid):
    lib,name=fpid.split(":")
    cand=[std+lib+".pretty", std+"Capacitor_Tantalum_SMD.pretty", W+"easyeda_lib/"+lib+".pretty"]
    for c in cand:
        if os.path.isdir(c):
            fp=pcbnew.FootprintLoad(c,name)
            if fp: return fp
    # lib may be named differently; search all pretty dirs in easyeda_lib
    for d in os.listdir(W+"easyeda_lib"):
        if d.endswith(".pretty"):
            fp=pcbnew.FootprintLoad(W+"easyeda_lib/"+d,name)
            if fp: return fp
    return None
added=[]
for c in t.find("components"):
    r=c.get("ref")
    if r in pf: continue
    fpid=c.findtext("footprint")
    fp=load(fpid)
    if fp is None: print("!! cannot load",r,fpid); continue
    fp.SetReference(r); fp.SetValue(c.findtext("value") or "")
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(130),pcbnew.FromMM(35)))  # parked in empty right area
    b.Add(fp); pf[r]=fp; added.append(r)
print("added",added)
# nets
ni=b.GetNetInfo()
for n in t.find("nets"):
    name=n.get("name")
    ni_item=b.FindNet(name)
    if ni_item is None:
        ni_item=pcbnew.NETINFO_ITEM(b,name); b.Add(ni_item)
    for x in n:
        r,p=x.get("ref"),x.get("pin")
        if r not in pf: continue
        pad=pf[r].FindPadByNumber(p)
        if pad is None and p=="SH":
            for q in pf[r].Pads():
                if q.GetNumber()=="MP": q.SetNumber("SH")
            pad=pf[r].FindPadByNumber("SH")
        if pad is None: print("no pad",r,p); continue
        for q in pf[r].Pads():
            if q.GetNumber()==p: q.SetNet(ni_item)
# header spacing: R = L + 15.494
L=pf["HDR-CP-L-1"].GetPosition(); R=pf["HDR-CP-R-1"]
R.SetPosition(pcbnew.VECTOR2I(L.x+pcbnew.FromMM(15.494),L.y))
b.Save(W+"audio_companion.kicad_pcb")
print("saved")
