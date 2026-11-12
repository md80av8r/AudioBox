import sys, json, re, math
sys.path.insert(0,"/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/scripts")
import pcbnew, xml.etree.ElementTree as ET
from mech_heights import resolve, step_bbox
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D"
PCB=sys.argv[1] if len(sys.argv)>1 else W+"/audio_companion_work/audio_companion.kicad_pcb"
f=lambda v:v/1e6
b=pcbnew.LoadBoard(PCB)
bb=b.GetBoardEdgesBoundingBox(); BOARD=[f(bb.GetX()),f(bb.GetY()),f(bb.GetRight()),f(bb.GetBottom())]
db=[]; seen={}; lowest=0
for fp in b.GetFootprints():
    ref=str(fp.GetReference()); n=str(fp.GetFPID().GetLibItemName())
    if ref.startswith(("TP","H")) and not ref.startswith(("HDR","HEADPHONE")): continue
    if n not in seen:
        z=None; ms=list(fp.Models())
        if ms:
            s=resolve(ms[0].m_Filename)
            if s:
                bx=step_bbox(s)
                if bx: z=(bx[2][0],bx[2][1])
        seen[n]=z
    z=seen[n]
    h=round(z[1],2) if z else 1.0
    zmin=round(z[0],2) if z else 0
    if ref in ("HDR-CP-L-1","HDR-CP-R-1"): h=2.5
    if ref=="ENC1": h=max(h,13.69)
    bx=fp.GetBoundingBox(False)
    if h<=0.6 and (bx.GetWidth()*bx.GetHeight())/1e12<4: continue
    db.append(dict(ref=ref,fp=n,x0=round(f(bx.GetX()),2),y0=round(f(bx.GetY()),2),x1=round(f(bx.GetRight()),2),y1=round(f(bx.GetBottom()),2),h=h,zmin=zmin,src="3D model" if z else "estimate",mate=ref in ("HDR-CP-L-1","HDR-CP-R-1")))
    lowest=min(lowest,zmin)
# CrowPanel from Eagle brd, mapped onto the daughterboard (x mirrored, header-derived)
A=137.18; B=92.5
t=ET.parse(W+"/crowpanel_ref/adv43_v13/brd.brd").getroot(); pk={}
for p in t.iter("package"):
    xs=[];ys=[]
    for tag in ("smd","pad"):
        for s in p.iter(tag):
            x,y=float(s.get("x")),float(s.get("y")); dx=float(s.get("dx") or s.get("diameter") or 1.5); dy=float(s.get("dy") or dx)
            xs+=[x-dx/2,x+dx/2]; ys+=[y-dy/2,y+dy/2]
    for w in p.iter("wire"):
        if w.get("layer") in ("21","51"): xs+=[float(w.get("x1")),float(w.get("x2"))]; ys+=[float(w.get("y1")),float(w.get("y2"))]
    for r in p.iter("rectangle"):
        if r.get("layer") in ("21","51"): xs+=[float(r.get("x1")),float(r.get("x2"))]; ys+=[float(r.get("y1")),float(r.get("y2"))]
    if xs: pk[p.get("name")]=(min(xs),min(ys),max(xs),max(ys))
H={"J2":(8.9,"measured"),"J12":(8.9,"measured"),"J13":(8.9,"measured"),"J9":(4.3,"measured"),"J11":(4.3,"measured"),
"J10":(8.0,"measured"),"J15":(6.0,"estimate - measure"),"J3":(6.35,"measured"),"J1":(3.2,"estimate (USB-C)"),
"BT1":(5.08,"measured"),"B2":(5.0,"estimate - measure"),"K3":(9.14,"measured"),"K4":(9.14,"measured"),
"K1":(2.0,"estimate"),"U5":(3.2,"datasheet"),"JP1":(2.0,"estimate"),"J5":(2.0,"estimate"),"J14":(8.7,"estimate (pin length in name)")}
NAMES={"J2":"UART0-OUT conn","J12":"UART1-OUT conn","J13":"I2C-OUT conn","J9":"header socket R","J11":"header socket L","J10":"UART0-IN conn","J15":"SPK conn","J3":"battery conn","J1":"USB-C","BT1":"coin cell","B2":"buzzer","K3":"RESET button","K4":"BOOT button","K1":"DIP switch","U5":"ESP32 module","JP1":"LCD FPC","J5":"touch FPC","J14":"test pins"}
cp=[]
for e in t.iter("element"):
    n=e.get("name"); rot=e.get("rot") or "R0"
    if n[0]=="P" or rot.startswith("M") or e.get("package") not in pk: continue
    ang=int(re.sub(r"[^0-9]","",rot) or 0); x0,y0,x1,y1=pk[e.get("package")]
    ex,ey=float(e.get("x")),float(e.get("y")); pts=[]
    for (px,py) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):
        c,s=math.cos(math.radians(ang)),math.sin(math.radians(ang)); rx,ry=px*c-py*s,px*s+py*c
        pts.append((A-(ex+rx),B-(ey+ry)))
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    if (max(xs)-min(xs))*(max(ys)-min(ys))<9 and n not in H: continue
    h,src=H.get(n,(1.5,"estimate"))
    cp.append(dict(ref=n,name=NAMES.get(n,e.get("value") or n),x0=round(min(xs),2),y0=round(min(ys),2),x1=round(max(xs),2),y1=round(max(ys),2),h=h,src=src,mate=n in ("J9","J11")))
CPO=[round(A-117.93,2),round(B-71.37,2),round(A-0.435,2),round(B-0.17,2)]
holes_db=[(round(f(x.GetPosition().x),2),round(f(x.GetPosition().y),2)) for x in b.GetFootprints() if str(x.GetReference()) in ("H1","H2","H3","H4")]
holes_cp=[(round(A-xe,2),round(B-ye,2)) for xe,ye in ((114.93,3.17),(3.43,3.17),(114.93,68.37),(3.43,68.37))]
ctr=lambda ref,L:[ (round((q['x0']+q['x1'])/2,2),round((q['y0']+q['y1'])/2,2)) for q in L if q['ref']==ref][0]
controls=[]
for r,nm in (('ENC1','Encoder'),('SW-PWR-1','Power button'),('SW-BYPASS-1','Bypass button')):
    if any(q['ref']==r for q in db): controls.append(dict(ref=r,name=nm,x=ctr(r,db)[0],y=ctr(r,db)[1],board='daughterboard'))
for r,nm in (('K3','RESET button'),('K4','BOOT button'),('J1','USB-C port')):
    controls.append(dict(ref=r,name=nm,x=ctr(r,cp)[0],y=ctr(r,cp)[1],board='CrowPanel'))
mcx=(CPO[0]+CPO[2])/2; mcy=(CPO[1]+CPO[3])/2
# user caliper data (2026-10-17): module 4.15 x 2.65 in; lit area 3.75 x 2.125 in; side margins 0.2 in; top margin 0.14 in; bottom margin = 2.65-2.125-0.14 = 0.385 in
LW,LH=3.75*25.4,2.125*25.4; MW,MH=4.15*25.4,2.65*25.4; TOP=0.14*25.4
display=dict(mw=round(MW,2),mh=round(MH,2),w=round(LW,2),h=round(LH,2),mcx=round(mcx,2),mcy=round(mcy,2),cx=round(mcx,2),cy=round(mcy-MH/2+TOP+LH/2,2))
data=dict(controls=controls,display=display,board=[round(v,2) for v in BOARD],cpout=CPO,db=db,cp=cp,holes_db=holes_db,holes_cp=holes_cp,lowest=round(lowest,2))
open(W+"/audio_companion_work/mech_model.json","w").write(json.dumps(data))
tpl=open(W+"/audio_companion_work/scripts/mech_viewer_template.html").read()
html=tpl.replace("__DATA__",json.dumps(data))
open(W+"/audio_companion_work/mech_viewer.html","w").write("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>MD-88 stack model</title></head><body style='margin:0;font-family:system-ui,sans-serif'>"+html+"</body></html>")
print("db parts",len(db),"cp parts",len(cp),"lowest below board",data["lowest"])
