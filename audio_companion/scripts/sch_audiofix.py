import re, uuid
P="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_sch"
t=open(P).read()
U=lambda: str(uuid.uuid4())
def fmt(v): return ('%.4f'%v).rstrip('0').rstrip('.')
def sym_span(ref):
    for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "([^"]+)"\)\n\t\t\(at ([\d.\-]+) ([\d.\-]+) (\d+)\)',t):
        i=m.start()+1; j=t.find('\n\t(symbol\n',i+10); j=len(t) if j<0 else j+1
        if f'(property "Reference" "{ref}"' in t[i:j]: return i,j,float(m.group(2)),float(m.group(3))
    raise SystemExit("no symbol "+ref)
def rename_label(old,new,x,y):
    global t
    pat=re.compile(r'(\t\(label ")'+re.escape(old)+r'("\n\t\t\(at '+re.escape(fmt(x))+' '+re.escape(fmt(y))+r' \d+\))')
    assert len(pat.findall(t))==1,(old,x,y,len(pat.findall(t)))
    t=pat.sub(lambda m:m.group(1)+new+m.group(2),t,1)
def remove_label(name,x,y):
    global t
    pat=re.compile(r'\t\(label "'+re.escape(name)+r'"\n\t\t\(at '+re.escape(fmt(x))+' '+re.escape(fmt(y))+r' \d+\).*?\n\t\)\n',re.S)
    m=pat.search(t); assert m,("nolabel",name,x,y); t=t[:m.start()]+t[m.end():]
def remove_wire(x1,y1,x2,y2):
    global t
    for a,b in (((x1,y1),(x2,y2)),((x2,y2),(x1,y1))):
        pat=re.compile(r'\t\(wire\n\t\t\(pts\n\t\t\t\(xy '+re.escape(fmt(a[0]))+' '+re.escape(fmt(a[1]))+r'\) \(xy '+re.escape(fmt(b[0]))+' '+re.escape(fmt(b[1]))+r'\)\n\t\t\)\n.*?\n\t\)\n',re.S)
        m=pat.search(t)
        if m: t=t[:m.start()]+t[m.end():]; return
    raise SystemExit(("nowire",x1,y1,x2,y2))
def add_label(name,x,y,ang):
    global t
    just="left bottom" if ang in (0,90) else "right bottom"
    s=f'\t(label "{name}"\n\t\t(at {fmt(x)} {fmt(y)} {ang})\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{U()}")\n\t)\n'
    k=t.index('\t(sheet_instances'); t=t[:k]+s+t[k:]
pwr_n=[max(int(x) for x in re.findall(r'"#PWR0*(\d+)"',t))]
def clone(src,newref,value,footprint,x,y,rot=None):
    global t
    i,j,sx,sy=sym_span(src); blk=t[i:j]; dx,dy=x-sx,y-sy
    blk=re.sub(r'\(at ([\-\d.]+) ([\-\d.]+)',lambda m:'(at %s %s'%(fmt(float(m.group(1))+dx),fmt(float(m.group(2))+dy)),blk)
    if rot is not None: blk=re.sub(r'(\t\t\(at [\-\d.]+ [\-\d.]+ )\d+\)',lambda m:m.group(1)+'%d)'%rot,blk,1)
    blk=re.sub(r'(\(property "Reference" ")[^"]*"',lambda m:m.group(1)+newref+'"',blk,1)
    blk=re.sub(r'(\(reference ")[^"]*"',lambda m:m.group(1)+newref+'"',blk)
    if value is not None: blk=re.sub(r'(\(property "Value" ")[^"]*"',lambda m:m.group(1)+value+'"',blk,1)
    if footprint is not None: blk=re.sub(r'(\(property "Footprint" ")[^"]*"',lambda m:m.group(1)+footprint+'"',blk,1)
    for ou in set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)',blk)): blk=blk.replace(ou,U())
    for ou in set(re.findall(r'\(pin "[^"]+"\n\t\t\t\(uuid "([0-9a-f-]{36})"',blk)): blk=blk.replace(ou,U())
    t=t[:j]+blk+t[j:]
R0402="Resistor_SMD:R_0402_1005Metric"
def two_pin_vertical(newref,value,fp,x,y,top,bottom,src="R8",rot=0):
    # R8 is vertical rot 180 (pins at y+-3.81); we force rot 0 for polarized/cap templates handled by caller
    clone(src,newref,value,fp,x,y,rot)
    add_label(top,x,y-3.81,90); add_label(bottom,x,y+3.81,270)
# ---------------- TPA stage ----------------
rename_label("TPA_IN_L","TPA_IN_L_N",196.85,110.49)
rename_label("TPA_IN_R","TPA_IN_R_N",237.49,113.03)
rename_label("HP_L_AMP","HP_L_VO",194.31,106.68)
rename_label("HP_R_AMP","HP_R_VO",231.14,110.49)
# SHUTDOWN -> GND
remove_label("+3V3",231.14,115.57)
pwr_n[0]+=1; clone("#PWR011","#PWR%02d"%pwr_n[0],None,None,231.14,115.57,90)
# new parts, left channel row y=152, right channel row y=172 ; x spacing 14
for side,y in (("L",152.4),("R",172.72)):
    n=side
    two_pin_vertical(f"R-TPA-IN-{n}","10k",R0402,35.56,y,f"TPA_IN_{n}",f"TPA_IN_{n}_N",src="R8",rot=180)
    two_pin_vertical(f"R-TPA-FB-{n}","10k",R0402,48.26,y,f"HP_{n}_VO",f"TPA_IN_{n}_N",src="R8",rot=180)
    two_pin_vertical(f"C-HP-{n}","220uF 6.3V","Capacitor_Tantalum_SMD:CP_EIA-6032-28_Kemet-C",60.96,y,f"HP_{n}_VO",f"HP_{n}_CAP",src="C-BULK-3V3",rot=0)
    two_pin_vertical(f"R-HP-{n}","10R",R0402,73.66,y,f"HP_{n}_CAP",f"HP_{n}_AMP",src="R8",rot=180)
# ---------------- Mic preamp ----------------
remove_wire(227.33,207.01,227.33,242.57)
remove_wire(207.01,207.01,207.01,212.09)
remove_wire(207.01,212.09,209.55,212.09)
add_label("MIC_RAW",209.55,212.09,180)
rename_label("+3V3","MIC_BIAS_SRC",217.17,212.09)
# solder jumper (3V3 -> MIC_BIAS_SRC) from Conn_01x02 template
clone("J-HAPTIC-1","JP-MIC-BIAS","SolderJumper","Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",100.33,152.4,0)
add_label("+3V3",100.33-5.08,152.4,180); add_label("MIC_BIAS_SRC",100.33-5.08,152.4+2.54,180)
# series bias resistor
two_pin_vertical("R-MICBIAS","100k",R0402,114.3,152.4,"VMID_BIAS","MIC_IN_P",src="R8",rot=180)
add_label("MIC_IN_P",230.0,207.01,0)
# ---------------- ANR enable pull-down ----------------
remove_label("+3V3",334.01,140.97)
pwr_n[0]+=1; clone("#PWR011","#PWR%02d"%pwr_n[0],None,None,334.01,140.97,0)
open(P,"w").write(t); print("schematic edited")
