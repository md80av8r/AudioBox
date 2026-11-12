import pcbnew, xml.etree.ElementTree as ET, sys
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work"
mm=pcbnew.FromMM; V=lambda x,y: pcbnew.VECTOR2I(mm(x),mm(y)); f=lambda v:v/1e6
b=pcbnew.LoadBoard(W+"/audio_companion_before_v19.kicad_pcb")
net=ET.parse(W+"/ref/net19.xml").getroot()
pinnet={}
for n in net.find("nets"):
    for x in n: pinnet[(x.get("ref"),x.get("pin"))]=n.get("name")
comps={c.get("ref") for c in net.find("components")}
REMOVE=["ENC1","R2","R3","J-SPARE-1","SW-BYPASS-1","SW-PWR-1","H1","H2","H3","H4"]
CHANGED_FP=["HEADPHONE_BYPASS-1","MIC_BYPASS-1","J-BTN-1"]   # will move/replace; rip their nets
PLANE=("GND","/+3V3","/AGND","/+3V3_A")
rip=set()
for ref in REMOVE+CHANGED_FP:
    fp=b.FindFootprintByReference(ref)
    if fp:
        for p in fp.Pads():
            n=str(p.GetNetname())
            if n and n not in PLANE and not n.startswith("unconnected"): rip.add(n)
for ref in REMOVE:
    fp=b.FindFootprintByReference(ref)
    if fp: b.RemoveNative(fp)
removed=0
for t in list(b.GetTracks()):
    if str(t.GetNetname()) in rip: b.RemoveNative(t); removed+=1
print("ripped nets:",len(rip),"tracks/vias removed:",removed)
# outline: replace Edge.Cuts with the new rectangle
for d in list(b.GetDrawings()):
    if d.GetLayerName()=="Edge.Cuts": b.RemoveNative(d)
X0,X1,Y0,Y1=19.241,150.741,19.925,92.335   # 117.5 mm CrowPanel width + 14 mm ear on the right for the two cover connectors
for (a,c,d,e) in ((X0,Y0,X1,Y0),(X1,Y0,X1,Y1),(X1,Y1,X0,Y1),(X0,Y1,X0,Y0)):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetStart(V(a,c)); s.SetEnd(V(d,e)); s.SetWidth(mm(0.1)); b.Add(s)
# zones follow the new outline (inset 0.3 mm)
for z in b.Zones():
    ch=z.Outline().Outline(0)
    pts=[V(X0+0.3,Y0+0.3),V(X1-0.3,Y0+0.3),V(X1-0.3,Y1-0.3),V(X0+0.3,Y1-0.3)]
    for i in range(4): ch.SetPoint(i,pts[i])
# CrowPanel-pattern mounting holes (NPTH 3.2 mm)
for i,(x,y) in enumerate(((22.241,24.135),(133.741,24.135),(22.241,89.335),(133.741,89.335)),1):
    fp=pcbnew.FOOTPRINT(b); fp.SetReference("H%d"%i); fp.SetValue("MountingHole_3.2mm_M3_NPTH"); fp.SetFPID(pcbnew.LIB_ID("MountingHole","MountingHole_3.2mm_M3"))
    fp.SetPosition(V(x,y)); p=pcbnew.PAD(fp); p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(mm(3.2),mm(3.2))); p.SetDrillSize(pcbnew.VECTOR2I(mm(3.2),mm(3.2)))
    ls=pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); ls.AddLayer(pcbnew.F_Mask); ls.AddLayer(pcbnew.B_Mask); p.SetLayerSet(ls)
    p.SetPosition(V(x,y)); fp.Add(p); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); b.Add(fp)
# nets for existing footprints
def getnet(name):
    ni=b.FindNet(name)
    if ni is None:
        ni=pcbnew.NETINFO_ITEM(b,name); b.Add(ni); ni=b.FindNet(name)
    return ni
changes=0
for fp in b.GetFootprints():
    ref=str(fp.GetReference())
    if ref not in comps: continue
    for p in fp.Pads():
        want=pinnet.get((ref,str(p.GetNumber())))
        if want is None: continue
        if want.startswith("unconnected"): 
            if str(p.GetNetname())!="": p.SetNetCode(0); changes+=1
            continue
        if str(p.GetNetname())!=want: p.SetNet(getnet(want)); changes+=1
print("pad net changes:",changes)
missing=sorted(c for c in comps if b.FindFootprintByReference(c) is None); print("not yet on board:",missing)
b.Save(W+"/audio_companion_v19_s1.kicad_pcb")
