import json, sys, heapq, math, re
items=json.load(open(sys.argv[1])); pairs=json.load(open(sys.argv[2])); outp=sys.argv[3]
G=0.05; CLR=0.127; VIA_D=0.4; EDGE=(19.241,19.925,150.741,92.335)
def widthfor(net): return 0.4 if net in ("/+BATT","/+12V","/HP_L_OUT","/HP_R_OUT") else (0.3 if net in ("/HP_L_AMP","/HP_R_AMP","/K1_COIL_DRIVE") else 0.2)
def rasterize(items,net,tw,box,infl_track_extra):
    x0,y0,x1,y1=box; nx=int((x1-x0)/G)+1; ny=int((y1-y0)/G)+1
    T={"F":bytearray(nx*ny),"B":bytearray(nx*ny)}; V={"F":bytearray(nx*ny),"B":bytearray(nx*ny)}
    def mark(arr,rect,infl):
        a=max(0,int((rect[0]-infl-x0)/G)); b2=min(nx-1,int((rect[2]+infl-x0)/G)+1)
        c=max(0,int((rect[1]-infl-y0)/G)); d=min(ny-1,int((rect[3]+infl-y0)/G)+1)
        for iy in range(c,d+1):
            base=iy*nx
            for ix in range(a,b2+1): arr[base+ix]=1
    def markseg(arr,p,q,r):
        n=max(1,int(math.hypot(q[0]-p[0],q[1]-p[1])/(G/2)))
        for i in range(n+1):
            x=p[0]+(q[0]-p[0])*i/n; y=p[1]+(q[1]-p[1])*i/n
            markcirc(arr,x,y,r)
    def markcirc(arr,x,y,r):
        a=max(0,int((x-r-x0)/G)); b2=min(nx-1,int((x+r-x0)/G)+1); c=max(0,int((y-r-y0)/G)); d=min(ny-1,int((y+r-y0)/G)+1)
        for iy in range(c,d+1):
            yy=y0+iy*G
            for ix in range(a,b2+1):
                xx=x0+ix*G
                if (xx-x)**2+(yy-y)**2<=r*r: arr[iy*nx+ix]=1
    for it in items:
        if it["net"]==net and net!="":
            if it["k"]=="pad":
                r=it["r"]
                for L,on in (("F",it["F"]),("B",it["B"])):
                    if on: mark(V[L],r,VIA_D/2+0.03)
            continue
        if it["k"]=="pad":
            r=it["r"]
            if r[2]<x0-2 or r[0]>x1+2 or r[3]<y0-2 or r[1]>y1+2: continue
            for L,on in (("F",it["F"]),("B",it["B"])):
                if on: mark(T[L],r,CLR+tw/2); mark(V[L],r,CLR+VIA_D/2)
        elif it["k"]=="via":
            c=it["c"]; rr=it["d"]/2
            if c[0]<x0-2 or c[0]>x1+2 or c[1]<y0-2 or c[1]>y1+2: continue
            for L in "FB": markcirc(T[L],c[0],c[1],rr+CLR+tw/2); markcirc(V[L],c[0],c[1],rr+CLR+VIA_D/2)
        else:
            a,b_=it["a"],it["b"]
            if max(a[0],b_[0])<x0-2 or min(a[0],b_[0])>x1+2 or max(a[1],b_[1])<y0-2 or min(a[1],b_[1])>y1+2: continue
            L=it["L"]; markseg(T[L],a,b_,it["w"]/2+CLR+tw/2); markseg(V[L],a,b_,it["w"]/2+CLR+VIA_D/2)
    # board edge keepout
    for iy in range(ny):
        for ix in range(nx):
            x=x0+ix*G;y=y0+iy*G
            if x<EDGE[0]+0.6 or x>EDGE[2]-0.6 or y<EDGE[1]+0.6 or y>EDGE[3]-0.6:
                for L in "FB": T[L][iy*nx+ix]=1; V[L][iy*nx+ix]=1
    return nx,ny,T,V
def nodes_for(it_pt,layers,box):
    x0,y0=box[0],box[1]
    return [(int(round((it_pt[0]-x0)/G)),int(round((it_pt[1]-y0)/G)),L) for L in layers]
def route(items,net,A,B):
    tw=widthfor(net)
    xs=[A["c"][0],B["c"][0]]; ys=[A["c"][1],B["c"][1]]
    box=(min(xs)-10,min(ys)-10,max(xs)+10,max(ys)+10)
    nx,ny,T,V=rasterize(items,net,tw,box,0)
    st=nodes_for(A["c"],A["layers"],box); gl=set(nodes_for(B["c"],B["layers"],box))
    # free the endpoint neighbourhoods (they sit inside own-net copper which is exempt, but others' inflation may touch)
    def tb(L,ix,iy): return T[L][iy*nx+ix]
    openq=[]; best={}
    gx,gy=list(gl)[0][0],list(gl)[0][1]
    def h(ix,iy):
        dx=abs(ix-gx);dy=abs(iy-gy); return (max(dx,dy)+0.414*min(dx,dy))
    for s in st:
        best[s]=0; heapq.heappush(openq,(h(s[0],s[1]),0,s,None))
    came={}
    VC=int(1.5/G)
    dirs=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)]
    found=None; it=0
    while openq:
        f,g,s,par=heapq.heappop(openq)
        if best.get(s,1e18)<g-1e-9: continue
        if s in gl: found=s; came[s]=par; break
        it+=1
        if it>3_000_000: break
        ix,iy,L=s
        for dx,dy,c in dirs:
            jx,jy=ix+dx,iy+dy
            if jx<0 or jy<0 or jx>=nx or jy>=ny: continue
            if tb(L,jx,jy) and (jx,jy,L) not in gl: continue
            if dx and dy and (tb(L,ix+dx,iy) or tb(L,ix,iy+dy)): continue
            n=(jx,jy,L); ng=g+c+(0.02 if L=="B" else 0)
            if ng<best.get(n,1e18): best[n]=ng; came[n]=s; heapq.heappush(openq,(ng+h(jx,jy),ng,n,s))
        # via
        O="B" if L=="F" else "F"
        if not V["F"][iy*nx+ix] and not V["B"][iy*nx+ix]:
            n=(ix,iy,O); ng=g+VC
            if ng<best.get(n,1e18): best[n]=ng; came[n]=s; heapq.heappush(openq,(ng+h(ix,iy),ng,n,s))
    if not found: return None
    path=[];s=found
    while s is not None: path.append(s); s=came.get(s)
    path.reverse()
    return [(box[0]+p[0]*G,box[1]+p[1]*G,p[2]) for p in path],tw
def simplify(pts):
    segs=[]; vias=[]; cur=[pts[0]]
    for i in range(1,len(pts)):
        p=pts[i]; q=cur[-1]
        if p[2]!=q[2]:
            segs.append(cur); vias.append((q[0],q[1])); cur=[p]
        else: cur.append(p)
    segs.append(cur)
    out=[]
    for sg in segs:
        pl=[sg[0]]
        for i in range(1,len(sg)-1):
            a,b_,c=pl[-1],sg[i],sg[i+1]
            if abs((b_[0]-a[0])*(c[1]-b_[1])-(b_[1]-a[1])*(c[0]-b_[0]))>1e-6: pl.append(b_)
        if len(sg)>1: pl.append(sg[-1])
        out.append(pl)
    return out,vias
import os
PRI=os.environ.get('MAZE_PRI','').split(',')
pairs.sort(key=lambda p: (PRI.index(p['net']) if p['net'] in PRI else 99, abs(p['a']['c'][0]-p['b']['c'][0])+abs(p['a']['c'][1]-p['b']['c'][1])))
res=[]; fails=[]
for pr in pairs:
    net=pr["net"]; A=pr["a"]; B=pr["b"]
    r=route(items,net,A,B)
    if r is None: fails.append(pr); continue
    path,tw=r
    polys,vias=simplify(path)
    res.append(dict(net=net,tw=tw,polys=[[ (p[0],p[1],p[2]) for p in pl] for pl in polys],vias=vias))
    # add to obstacles
    for pl in polys:
        for i in range(len(pl)-1):
            items.append(dict(k="trk",net=net,a=[pl[i][0],pl[i][1]],b=[pl[i+1][0],pl[i+1][1]],w=tw,L=pl[i][2]))
    for v in vias: items.append(dict(k="via",net=net,c=list(v),d=VIA_D))
    print("routed",net,len(path),"nodes",len(vias),"vias",flush=True)
json.dump(dict(routes=res,fails=[(f["net"],f["a"]["c"],f["b"]["c"]) for f in fails]),open(outp,"w"))
print("done: routed",len(res),"failed",len(fails),[ (f["net"],f["a"]["c"],f["b"]["c"]) for f in fails])
