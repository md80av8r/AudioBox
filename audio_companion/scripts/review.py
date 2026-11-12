import pcbnew, math, collections
b=pcbnew.LoadBoard("/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb")
mm=1e6
tr=collections.defaultdict(list); vias=collections.defaultdict(list)
for t in b.GetTracks():
    n=t.GetNetname()
    if t.GetClass()=="PCB_VIA": vias[n].append((t.GetPosition().x/mm,t.GetPosition().y/mm))
    else: tr[n].append((t.GetStart().x/mm,t.GetStart().y/mm,t.GetEnd().x/mm,t.GetEnd().y/mm,t.GetWidth()/mm,"F" if t.GetLayer()==pcbnew.F_Cu else "B"))
def L(n): return sum(math.hypot(s[2]-s[0],s[3]-s[1]) for s in tr[n])
def LL(n,l): return sum(math.hypot(s[2]-s[0],s[3]-s[1]) for s in tr[n] if s[5]==l)
def segdist(a,b2):
    # min distance between two segments (sampled)
    best=1e9
    n=max(2,int(max(math.hypot(a[2]-a[0],a[3]-a[1]),math.hypot(b2[2]-b2[0],b2[3]-b2[1]))/0.25))
    pts_a=[(a[0]+(a[2]-a[0])*i/n,a[1]+(a[3]-a[1])*i/n) for i in range(n+1)]
    pts_b=[(b2[0]+(b2[2]-b2[0])*i/n,b2[1]+(b2[3]-b2[1])*i/n) for i in range(n+1)]
    for p in pts_a:
        for q in pts_b:
            d=math.hypot(p[0]-q[0],p[1]-q[1])
            if d<best: best=d
    return best
def mindist(n1,n2):
    best=(1e9,None)
    for a in tr[n1]:
        for c in tr[n2]:
            if a[5]!=c[5]: continue
            d=segdist(a,c)-a[4]/2-c[4]/2
            if d<best[0]: best=(d,(round(a[0],1),round(a[1],1)))
    return best
audio=["/MIC_RAW","/MIC_AMPLIFIED","/MIC_TO_PLANE","/HP_L_RAW","/HP_R_RAW","/HP_L_AMP","/HP_R_AMP","/HP_L_OUT","/HP_R_OUT","/CODEC_HP_L","/CODEC_HP_R","/TPA_IN_L","/TPA_IN_R","/LINE_IN_L","/LINE_IN_R","/LINE_OUT_L","/LINE_OUT_R","/VMID","/VREF","/ADCVREF","/VMID_BIAS","/PTT_PASS","/+3V3_A"]
sw=["Net-(D3-A)","/+12V","/+BATT"]; dig=["/MCLK","/I2S_BCLK","/I2S_LRCK","/I2S_DOUT","/I2C_SCL","/I2C_SDA","/I2S_DIN","/ANR_POWER_EN"]
print("=== AUDIO NETS: length mm (F/B), vias, width, closest approach to switching nets / digital clocks (mm edge-edge)")
for n in audio:
    if n not in tr and n not in vias: print(n,"(no copper)"); continue
    w=sorted({s[4] for s in tr[n]})
    ds=min((mindist(n,s)+(s,) for s in sw if s in tr),key=lambda x:x[0],default=(99,None,""))
    dd=min((mindist(n,s)+(s,) for s in dig if s in tr),key=lambda x:x[0],default=(99,None,""))
    print(f"{n:16s} len {L(n):5.1f} (F{LL(n,'F'):.1f}/B{LL(n,'B'):.1f}) vias {len(vias[n])} w{w}  nearSW {ds[0]:.2f}@{ds[2]}  nearDIG {dd[0]:.2f}@{dd[2]}")
print("=== BOOST")
for n in ["Net-(D3-A)","/+12V","/+BATT","Net-(U6-FB)","/ANR_POWER_EN"]:
    print(f"{n:14s} len {L(n):5.1f} (F{LL(n,'F'):.1f}/B{LL(n,'B'):.1f}) vias {len(vias[n])} widths {sorted({s[4] for s in tr[n]})}")
fp={f.GetReference():f for f in b.GetFootprints()}
def pad(r,n): 
    p=fp[r].FindPadByNumber(n); return (p.GetPosition().x/mm,p.GetPosition().y/mm,p.GetNetname())
for r,n in (("U6","1"),("U6","2"),("U6","5"),("U6","3"),("L2","1"),("L2","2"),("D3","1"),("D3","2"),("C46","1"),("C46","2"),("C47","1"),("C29","1"),("C29","2"),("C30","1"),("C32","2"),("R-FB-TOP-2","1"),("R-FB-TOP-2","2"),("R11","1")):
    if r in fp: print(" pad",r,n,[round(v,2) if not isinstance(v,str) else v for v in pad(r,n)])
# path 12V to LEMO
print("12V pads:",[(r.GetReference(),p.GetNumber()) for r in b.GetFootprints() for p in r.Pads() if p.GetNetname()=="/+12V"])
# nearest GND via to key pads
gv=vias["GND"]
for r,n in (("U6","2"),("C29","2"),("C46","2"),("C47","2"),("D3","1")):
    p=fp[r].FindPadByNumber(n); 
    if p: 
        x,y=p.GetPosition().x/mm,p.GetPosition().y/mm
        print("  GND via nearest to",r,n,round(min(math.hypot(x-a,y-c) for a,c in gv),2),"mm (pad net",p.GetNetname()+")")
