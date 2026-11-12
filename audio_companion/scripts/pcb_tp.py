import pcbnew, math, re, subprocess, json, sys
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work"
S="/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad"
K="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
SRC=W+"/audio_companion_before_v18.kicad_pcb"; OUT=W+"/audio_companion.kicad_pcb"
sch=open(W+"/audio_companion.kicad_sch").read()
def symuuid(ref):
    m=re.search(r'\(uuid "([0-9a-f-]{36})"\)\s*\(property "Reference" "'+re.escape(ref)+'"',sch); assert m,ref; return m.group(1)
mm=pcbnew.FromMM; V=lambda x,y: pcbnew.VECTOR2I(mm(x),mm(y))
def fmm(v): return v/1e6
TPS=[("TP1","GND","GND"),("TP2","GND","GND"),("TP3","/+3V3","3V3"),("TP4","/+3V3_A","3V3A"),("TP5","/+12V","12V"),("TP6","/AGND","AGND"),("TP7","/I2C_SDA","SDA")]
HDR_FP="/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_PinHeader_2.54mm.pretty"
def base():
    b=pcbnew.LoadBoard(SRC)
    # ENC1 pad 4 -> EXP_SPARE1
    enc=b.FindFootprintByReference("ENC1"); n1=b.FindNet("/EXP_SPARE1"); assert n1
    for p in enc.Pads():
        if p.GetNumber()=="4": p.SetNet(n1)
    return b
def add_header(b,hx,hy):
    fp=pcbnew.FootprintLoad(HDR_FP,"PinHeader_1x07_P2.54mm_Vertical"); fp.SetReference("J-SPARE-1"); fp.SetValue("SPARE-IO")
    fp.SetOrientationDegrees(270); fp.SetPosition(V(hx,hy)); b.Add(fp)
    nets=["/EXP_SPARE1","/EXP_SPARE2","/EXP_SPARE3","/EXP_SPARE4","/EXP_SPARE5","GND","/+3V3"]
    for p in fp.Pads(): p.SetNet(b.FindNet(nets[int(p.GetNumber())-1]))
    fp.SetPath(pcbnew.KIID_PATH("/"+symuuid("J-SPARE-1")))
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    # silk labels above the row
    labs=["1","2","3","4","5","G","3V"]
    for p in fp.Pads():
        x,y=fmm(p.GetPosition().x),fmm(p.GetPosition().y)
        t=pcbnew.PCB_TEXT(b); t.SetText(labs[int(p.GetNumber())-1]); t.SetLayer(pcbnew.F_SilkS); t.SetPosition(V(x,y-2.3))
        t.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); t.SetTextThickness(mm(0.15)); b.Add(t)
    t=pcbnew.PCB_TEXT(b); t.SetText("SPARE IO"); t.SetLayer(pcbnew.F_SilkS); t.SetPosition(V(hx-8.0,hy+2.4))
    t.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); t.SetTextThickness(mm(0.15)); b.Add(t)
    return fp
def add_tp(b,ref,net,label,px,py,anchor):
    fp=pcbnew.FOOTPRINT(b); fp.SetReference(ref); fp.SetValue("TestPoint")
    fp.SetFPID(pcbnew.LIB_ID("TestPoint","TestPoint_Pad_D1.5mm"))
    p=pcbnew.PAD(fp); p.SetShape(pcbnew.PAD_SHAPE_CIRCLE); p.SetSize(pcbnew.VECTOR2I(mm(1.5),mm(1.5))); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    ls=pcbnew.LSET(); ls.AddLayer(pcbnew.B_Cu); ls.AddLayer(pcbnew.B_Mask); p.SetLayerSet(ls)
    fp.SetLayer(pcbnew.B_Cu); fp.SetPosition(V(px,py))
    p.SetNumber("1"); p.SetNet(b.FindNet(net)); fp.Add(p); p.SetPosition(V(px,py))
    fp.SetAttributes(pcbnew.FP_SMD|pcbnew.FP_EXCLUDE_FROM_POS_FILES|pcbnew.FP_EXCLUDE_FROM_BOM)
    fp.SetPath(pcbnew.KIID_PATH("/"+symuuid(ref))); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    b.Add(fp)
    tr=pcbnew.PCB_TRACK(b); tr.SetStart(V(*anchor)); tr.SetEnd(V(px,py)); tr.SetWidth(mm(0.3)); tr.SetLayer(pcbnew.B_Cu); tr.SetNet(b.FindNet(net)); b.Add(tr)
    return fp

G=0.1
def occ_bcu(b,net):
    import numpy as np
    X0,Y0=20,20; nx=int(118/G); ny=int(71/G); occ=np.zeros((ny,nx),bool)
    def disc(x,y,r):
        a=max(0,int((x-r-X0)/G)); c=max(0,int((x+r-X0)/G)+1); d=max(0,int((y-r-Y0)/G)); e=int((y+r-Y0)/G)+1
        occ[d:e,a:c]=True
    def seg(p,q,r):
        n=max(1,int(math.hypot(q[0]-p[0],q[1]-p[1])/(G/2)))
        for i in range(n+1): disc(p[0]+(q[0]-p[0])*i/n,p[1]+(q[1]-p[1])*i/n,r)
    CL=0.35
    for t in b.GetTracks():
        if t.GetNetname()==net: continue
        if t.GetClass()=="PCB_VIA": disc(fmm(t.GetPosition().x),fmm(t.GetPosition().y),fmm(t.GetWidth(pcbnew.F_Cu))/2+CL)
        elif t.GetLayer()==pcbnew.B_Cu: seg((fmm(t.GetStart().x),fmm(t.GetStart().y)),(fmm(t.GetEnd().x),fmm(t.GetEnd().y)),fmm(t.GetWidth())/2+CL)
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname()==net and p.GetNetname()!="": continue
            if p.GetAttribute()==pcbnew.PAD_ATTRIB_SMD and not p.IsOnLayer(pcbnew.B_Cu): continue
            bb=p.GetBoundingBox(); 
            x0,y0,x1,y1=fmm(bb.GetX())-CL,fmm(bb.GetY())-CL,fmm(bb.GetRight())+CL,fmm(bb.GetBottom())+CL
            occ[max(0,int((y0-Y0)/G)):int((y1-Y0)/G)+1,max(0,int((x0-X0)/G)):int((x1-X0)/G)+1]=True
    for d in b.GetDrawings():
        if d.GetLayerName() in ("B.SilkS","B.Cu"):
            bb=d.GetBoundingBox(); occ[max(0,int((fmm(bb.GetY())-0.3-Y0)/G)):int((fmm(bb.GetBottom())+0.3-Y0)/G)+1,max(0,int((fmm(bb.GetX())-0.3-X0)/G)):int((fmm(bb.GetRight())+0.3-X0)/G)+1]=True
    occ[:int(1.6/G),:]=True; occ[-int(1.6/G):,:]=True; occ[:,:int(1.6/G)]=True; occ[:,-int(1.6/G):]=True
    return occ,X0,Y0
def cands(b,net,occ,X0,Y0,tried,extra=None):
    import numpy as np
    anchors=[]
    for t in b.GetTracks():
        if t.GetClass()=="PCB_VIA" and t.GetNetname()==net: anchors.append((fmm(t.GetPosition().x),fmm(t.GetPosition().y)))
    anchors=anchors or (extra or [])
    out=[]
    for ax,ay in anchors:
        for d in (1.4,1.8,2.3,3.0,4.0):
            for k in range(0,360,15):
                x=ax+d*math.cos(math.radians(k)); y=ay+d*math.sin(math.radians(k))
                x=round(x*10)/10; y=round(y*10)/10
                ix=int((x-X0)/G); iy=int((y-Y0)/G); r=int(1.15/G)
                if iy-r<0 or ix-r<0 or occ[iy-r:iy+r+1,ix-r:ix+r+1].any(): continue
                # stub corridor
                ok=True
                for i in range(1,11):
                    cx=ax+(x-ax)*i/10; cy=ay+(y-ay)*i/10
                    if i>3 and occ[int((cy-Y0)/G),int((cx-X0)/G)]: ok=False;break
                if ok and (x,y) not in tried: out.append((d,x,y,(ax,ay)))
    out.sort(key=lambda c:c[0]); return out
