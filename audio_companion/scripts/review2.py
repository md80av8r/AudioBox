import pcbnew, math, collections
b=pcbnew.LoadBoard("/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb")
mm=1e6
segs=collections.defaultdict(list)
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA": continue
    segs[t.GetNetname()].append((t.GetStart().x/mm,t.GetStart().y/mm,t.GetEnd().x/mm,t.GetEnd().y/mm,t.GetWidth()/mm,"F" if t.GetLayer()==pcbnew.F_Cu else "B"))
def ang(s): return math.atan2(s[3]-s[1],s[2]-s[0])
def par_len(A,B,gap):
    tot=0
    for a in A:
        la=math.hypot(a[2]-a[0],a[3]-a[1])
        if la<0.3: continue
        n=max(2,int(la/0.2)); hits=0
        for c in B:
            if c[5]!=a[5]: continue
            lc=math.hypot(c[2]-c[0],c[3]-c[1])
            if lc<0.3: continue
            da=abs(((ang(a)-ang(c))+math.pi/2)%math.pi-math.pi/2)
            if da>math.radians(20): continue
            cnt=0
            for i in range(n+1):
                x=a[0]+(a[2]-a[0])*i/n; y=a[1]+(a[3]-a[1])*i/n
                # point to segment dist
                dx,dy=c[2]-c[0],c[3]-c[1]; t=max(0,min(1,((x-c[0])*dx+(y-c[1])*dy)/(dx*dx+dy*dy)))
                d=math.hypot(x-(c[0]+t*dx),y-(c[1]+t*dy))-a[4]/2-c[4]/2
                if d<gap: cnt+=1
            hits=max(hits,cnt)
        tot+=la*hits/(n+1)
    return tot
audio=["/MIC_RAW","/MIC_AMPLIFIED","/HP_L_RAW","/HP_R_RAW","/HP_L_OUT","/HP_R_OUT","/CODEC_HP_L","/CODEC_HP_R","/LINE_IN_L","/LINE_IN_R","/LINE_OUT_L","/LINE_OUT_R","/VMID","/VREF","/ADCVREF","/MIC_TO_PLANE","/PTT_PASS"]
agg={"I2C/I2S/MCLK digital":["/MCLK","/I2S_BCLK","/I2S_LRCK","/I2S_DOUT","/I2C_SCL","/I2C_SDA","/I2S_DIN"],"boost SW node":["Net-(D3-A)"],"+12V":["/+12V"],"+BATT":["/+BATT"],"ANR_EN":["/ANR_POWER_EN"]}
print("parallel run length (mm) within 0.5mm gap, same layer, <20deg:")
for n in audio:
    row=[]
    for k,ns in agg.items():
        B=[s for x in ns for s in segs[x]]
        v=par_len(segs[n],B,0.5)
        if v>0.4: row.append(f"{k}:{v:.1f}")
    print(f"{n:15s}", "  ".join(row) if row else "-")
# audio vs audio crosstalk L<->R
for a,c in (("/HP_L_OUT","/HP_R_OUT"),("/HP_L_RAW","/HP_R_RAW"),("/MIC_RAW","/HP_L_RAW"),("/MIC_RAW","/HP_R_RAW"),("/MIC_AMPLIFIED","/CODEC_HP_L"),("/MIC_RAW","/PTT_PASS"),("/MIC_TO_PLANE","/PTT_PASS")):
    print(f"{a} || {c}: {par_len(segs[a],segs[c],0.5):.1f} mm")
# detour ratio: path length vs bbox half-perimeter of pads
fp={f.GetReference():f for f in b.GetFootprints()}
print("detour ratio (routed length / pad-to-pad Manhattan span):")
for n in ["/HP_L_OUT","/HP_R_OUT","/HP_L_RAW","/HP_R_RAW","/MIC_RAW","/MIC_TO_PLANE","/PTT_PASS","/+12V","/+3V3_A","/ANR_POWER_EN","Net-(D3-A)","/MIC_AMPLIFIED","/CODEC_HP_L","/CODEC_HP_R"]:
    pads=[(p.GetPosition().x/mm,p.GetPosition().y/mm,f.GetReference()) for f in b.GetFootprints() for p in f.Pads() if p.GetNetname()==n]
    xs=[p[0] for p in pads];ys=[p[1] for p in pads]
    span=(max(xs)-min(xs))+(max(ys)-min(ys))
    Ln=sum(math.hypot(s[2]-s[0],s[3]-s[1]) for s in segs[n])
    print(f"  {n:15s} routed {Ln:6.1f}  span {span:6.1f}  ratio {Ln/max(span,0.1):.2f}  pads {sorted({p[2] for p in pads})}")
