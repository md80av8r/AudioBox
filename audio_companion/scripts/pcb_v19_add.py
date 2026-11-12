import pcbnew, sys, json
# usage: pcb_v19_add.py in.kicad_pcb out.kicad_pcb libdir fpname side spec.json
# spec: list of {"ref":..,"x":..,"y":..,"rot":..,"value":..,"replace":bool}
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work"
inp,outp,libdir,name=sys.argv[1:5]; spec=json.load(open(sys.argv[5]))
mm=pcbnew.FromMM; V=lambda x,y: pcbnew.VECTOR2I(mm(x),mm(y))
import xml.etree.ElementTree as ET
net=ET.parse(W+"/ref/net19.xml").getroot(); pinnet={}
for n in net.find("nets"):
    for x in n: pinnet[(x.get("ref"),x.get("pin"))]=n.get("name")
comp={c.get("ref"):c for c in net.find("components")}
b=pcbnew.LoadBoard(inp)
def getnet(nm):
    ni=b.FindNet(nm)
    if ni is None: b.Add(pcbnew.NETINFO_ITEM(b,nm)); ni=b.FindNet(nm)
    return ni
base=pcbnew.FootprintLoad(libdir,name)
assert base is not None,(libdir,name)
for i,sp in enumerate(spec):
    fp=base if i==0 else pcbnew.Cast_to_FOOTPRINT(base.Duplicate(False))
    old=b.FindFootprintByReference(sp["ref"])
    if old is not None: b.RemoveNative(old)
    fp.SetReference(sp["ref"]); fp.SetValue(sp.get("value",name)); fp.SetPosition(V(sp["x"],sp["y"])); fp.SetOrientationDegrees(sp.get("rot",0))
    for p in fp.Pads():
        want=pinnet.get((sp["ref"],str(p.GetNumber())))
        if want and not want.startswith("unconnected"): p.SetNet(getnet(want))
    # keep the schematic link
    ref_el=comp[sp["ref"]]
    sheet=ref_el.find("sheetpath"); 
    try:
        tstamp=ref_el.find("tstamps").text.strip(); fp.SetPath(pcbnew.KIID_PATH("/"+tstamp))
    except Exception as e: pass
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    b.Add(fp)
b.Save(outp); print("added",len(spec),name)
