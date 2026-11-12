import pcbnew, json, math, sys
import numpy as np
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work"
mm=pcbnew.FromMM; V=lambda x,y: pcbnew.VECTOR2I(mm(float(x)),mm(float(y))); f=lambda v:v/1e6
b=pcbnew.LoadBoard(sys.argv[1]); OUT=sys.argv[2]
G=0.25; X0,Y0=15.0,15.0; nx=int(130/G); ny=int(85/G)
NEW=["J-ENC-1","J-PANEL-1","R-BYP-SENSE-1"]+["R-ENC-PU-%s"%n for n in ("OA","OB","IA","IB","PUSH")]+["R-ENC-S-%s"%n for n in ("OA","OB","IA","IB","PUSH")]+["C-ENC-%s"%n for n in ("OA","OB","IA","IB","PUSH")]
# CrowPanel tall parts (daughterboard coordinates, height mm) from the mech model
D=json.load(open(W+"/mech_model.json"))
tall_body=[(c["x0"],c["y0"],c["x1"],c["y1"]) for c in D["cp"] if c["h"]>=12-4.4-0.4 and not c["mate"]]   # keep-out for 4.4 mm connectors
tall_plug=[(c["x0"],c["y0"],c["x1"],c["y1"]) for c in D["cp"] if c["h"]>=12-6.5 and not c["mate"]]
def newgrid(): return np.zeros((ny,nx),bool)
def mark(g,x0,y0,x1,y1,m=0):
    a=max(0,int((x0-m-X0)/G)); c=min(nx,int((x1+m-X0)/G)+1); d=max(0,int((y0-m-Y0)/G)); e=min(ny,int((y1+m-Y0)/G)+1); g[d:e,a:c]=True
occ=newgrid(); occp=newgrid()
move=b.FindFootprintByReference("J-BTN-1"); move.SetPosition(V(23.6,78.55))
for fp in b.GetFootprints():
    r=str(fp.GetReference())
    if r in NEW: continue
    bb=fp.GetBoundingBox(False); mark(occ,f(bb.GetX()),f(bb.GetY()),f(bb.GetRight()),f(bb.GetBottom()),0.35); mark(occp,f(bb.GetX()),f(bb.GetY()),f(bb.GetRight()),f(bb.GetBottom()),0.2)
    for p in fp.Pads():
        q=p.GetBoundingBox(); mark(occ,f(q.GetX()),f(q.GetY()),f(q.GetRight()),f(q.GetBottom()),0.3)
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        q=t.GetBoundingBox(); mark(occ,f(q.GetX()),f(q.GetY()),f(q.GetRight()),f(q.GetBottom()),0.25)
    else:
        p,q=t.GetStart(),t.GetEnd(); n=max(1,int(math.hypot(f(p.x-q.x),f(p.y-q.y))/(G/2)))
        for i in range(n+1): mark(occ,f(p.x+(q.x-p.x)*i/n),f(p.y+(q.y-p.y)*i/n),f(p.x+(q.x-p.x)*i/n),f(p.y+(q.y-p.y)*i/n),0.15+f(t.GetWidth())/2)
# board edge margin
EX0,EX1,EY0,EY1=19.241,150.741,19.925,92.335
mark(occ,0,0,EX0+1.2,200,0); mark(occ,EX1-1.2,0,300,200,0); mark(occ,0,0,300,EY0+1.2,0); mark(occ,0,EY1-1.2,300,300,0)
def free(g,x0,y0,x1,y1):
    a=int((x0-X0)/G); c=int((x1-X0)/G)+1; d=int((y0-Y0)/G); e=int((y1-Y0)/G)+1
    if a<0 or d<0 or c>nx or e>ny: return False
    return not g[d:e,a:c].any()
def overlap(a,r):
    return not (a[2]<=r[0] or a[0]>=r[2] or a[3]<=r[1] or a[1]>=r[3])
def place_conn(ref,target,w,h):
    fp=b.FindFootprintByReference(ref); best=None
    for rot in (0,90,180,270):
        bw,bh=(w,h) if rot in (0,180) else (h,w)
        ex,ey={0:(0,1),90:(1,0),180:(0,-1),270:(-1,0)}[rot]
        for cy in np.arange(EY0+3,EY1-3,0.5):
            for cx in np.arange(EX0+3,EX1-3,0.5):
                rect=(cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2)
                if not free(occ,*rect): continue
                if any(overlap(rect,k) for k in tall_body): continue
                # entry region: 9 mm deep in front of the open face
                if ex==0: er=(rect[0],rect[3],rect[2],rect[3]+7) if ey>0 else (rect[0],rect[1]-7,rect[2],rect[1])
                else: er=(rect[2],rect[1],rect[2]+7,rect[3]) if ex>0 else (rect[0]-7,rect[1],rect[0],rect[3])
                # entry region may leave the board edge (cables exit) but must not hit other parts
                if er[0]>=EX0-3 and er[2]<=EX1+3 and er[1]>=EY0-3 and er[3]<=EY1+3 and not free(occp,*[max(er[0],X0),max(er[1],Y0),min(er[2],X0+130-1),min(er[3],Y0+85-1)]): continue
                if any(overlap(er,k) for k in tall_plug): continue
                sc=math.hypot(cx-target[0],cy-target[1])
                if best is None or sc<best[0]: best=(sc,cx,cy,rot,rect)
    assert best,ref
    sc,cx,cy,rot,rect=best
    fp.SetOrientationDegrees(rot); 
    c0=fp.GetPosition(); bb=fp.GetBoundingBox(False); ccx=f(bb.GetX()+bb.GetRight())/2; ccy=f(bb.GetY()+bb.GetBottom())/2
    fp.SetPosition(V(f(c0.x)+cx-ccx,f(c0.y)+cy-ccy))
    mark(occ,*rect,0.4); mark(occp,*rect,0.2); print(ref,"at",round(cx,1),round(cy,1),"rot",rot)
    return (cx,cy)
def put(ref,cx,cy,rot):
    fp=b.FindFootprintByReference(ref); fp.SetOrientationDegrees(rot)
    c0=fp.GetPosition(); bb=fp.GetBoundingBox(False); ccx=f(bb.GetX()+bb.GetRight())/2; ccy=f(bb.GetY()+bb.GetBottom())/2
    fp.SetPosition(V(f(c0.x)+cx-ccx,f(c0.y)+cy-ccy)); print(ref,"at",cx,cy,"rot",rot)
put("J-ENC-1",143.0,50.0,90); put("J-PANEL-1",143.0,76.0,90)
c1=(126.0,56.0)
# passives near the encoder connector
def place_small(ref,target,w=1.9,h=1.0):
    fp=b.FindFootprintByReference(ref); best=None
    for rot in (0,90):
        bw,bh=(w,h) if rot==0 else (h,w)
        for cy in np.arange(EY0+2,EY1-2,0.25):
            for cx in np.arange(EX0+2,EX1-2,0.25):
                rect=(cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2)
                if not free(occ,*rect): continue
                sc=math.hypot(cx-target[0],cy-target[1])
                if best is None or sc<best[0]: best=(sc,cx,cy,rot,rect)
    assert best,ref
    sc,cx,cy,rot,rect=best; fp.SetOrientationDegrees(rot); fp.SetPosition(V(cx,cy)); mark(occ,*rect,0.35)
tx,ty=c1
for k,nm in enumerate(("OA","OB","IA","IB","PUSH")):
    for pre in ("R-ENC-PU-","R-ENC-S-","C-ENC-"): place_small(pre+nm,(tx,ty+(k-2)*1.0))
place_small("R-BYP-SENSE-1",(100,56))
b.Save(OUT); print("saved")
