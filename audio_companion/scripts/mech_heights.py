import re, os, sys, json
SYS="/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels"
def step_bbox(path):
    t=open(path,errors="ignore").read()
    pts=[tuple(map(float,m)) for m in re.findall(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*(-?[\d.]+(?:E[-+]?\d+)?)\s*,\s*(-?[\d.]+(?:E[-+]?\d+)?)\s*,\s*(-?[\d.]+(?:E[-+]?\d+)?)\s*\)",t,re.I)]
    if not pts: return None
    return [(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)]
def resolve(model_path, prj="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work"):
    p=str(model_path)
    p=re.sub(r"\$\{KICAD\d*_3DMODEL_DIR\}",SYS,p).replace("${KIPRJMOD}",prj)
    base,ext=os.path.splitext(p); s=base+".step"
    return s if os.path.exists(s) else None
if __name__=="__main__":
    import pcbnew
    b=pcbnew.LoadBoard(sys.argv[1]); seen={}
    for fp in b.GetFootprints():
        n=str(fp.GetFPID().GetLibItemName())
        if n in seen: continue
        ms=list(fp.Models()); r=None
        if ms:
            s=resolve(ms[0].m_Filename)
            if s:
                bb=step_bbox(s)
                if bb: r=[round(bb[2][0],2),round(bb[2][1],2),round(bb[0][1]-bb[0][0],1),round(bb[1][1]-bb[1][0],1)]
        seen[n]=r; print(n,"| z0,z1,dx,dy =",r)
    json.dump(seen,open(sys.argv[2],"w"))
