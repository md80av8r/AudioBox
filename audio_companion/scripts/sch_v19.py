import re, uuid
exec(open("/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/scripts/sch_micdc.py").read().split("\nrename_label(")[0].replace('open(P,"w")','#'))
ROOT="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
def remove_symbol(ref):
    global t
    i,j,_,_=sym_span(ref); t=t[:i]+t[j:]
def rmlabel(name,x,y):
    remove_label(name,x,y)
# ---- A/B/C removals
for r in ("ENC1","#PWR051","#PWR052","R2","R3","J-SPARE-1","#PWR059","SW-BYPASS-1","SW-PWR-1"): remove_symbol(r)
def remove_sym_at(lib,x,y):
    global t
    for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "'+re.escape(lib)+r'"\)\n\t\t\(at ([\d.\-]+) ([\d.\-]+) \d+\)',t):
        if abs(float(m.group(1))-x)<.05 and abs(float(m.group(2))-y)<.05:
            i=m.start()+1; j=t.find('\n\t(symbol\n',i+10); j=len(t) if j<0 else j+1; t=t[:i]+t[j:]; return True
    return False
print("removed SW-PWR GND symbol:",remove_sym_at("power:GND",41.91,33.02))
for n,x,y in (("EXP_ENC_A",39.37,109.22),("EXP_ENC_B",39.37,104.14),("EXP_SPARE1",39.37,111.76),("+3V3",50.8,119.38),("EXP_ENC_B",43.18,119.38),("+3V3",50.8,127),("EXP_ENC_A",43.18,127),
 ("EXP_SPARE1",79.92,92.38),("EXP_SPARE2",79.92,94.92),("EXP_SPARE3",79.92,97.46),("EXP_SPARE4",79.92,100),("EXP_SPARE5",79.92,102.54),("+3V3",79.92,107.62),
 ("Q1_GATE",207.01,191.77),("GND",217.17,191.77),("EXP_PWR_BTN",52.07,33.02)): rmlabel(n,x,y)
# ---- D: bypass LED shows the real relay state
rename_label("BYPASS_EN","GND",271.78,168.91)
rename_label("+3V3","K1_COIL_DRIVE",287.02,168.91)
# ---- E: spare-pin renames on U3
rename_label("EXP_SPARE1","EXP_ENC_IA",39.37,72.39)
rename_label("EXP_SPARE2","EXP_ENC_IB",59.69,74.93)
rename_label("EXP_SPARE3","EXP_ENC_PUSH",59.69,72.39)
rename_label("EXP_SPARE4","BYP_STATE",59.69,69.85)
# ---- G: relays -> SMT
for ref in ("HEADPHONE_BYPASS-1","MIC_BYPASS-1"):
    i,j,_,_=sym_span(ref); blk=t[i:j]
    blk=blk.replace('"easyeda_lib:RELAY-TH_G6K-2P-Y"','"Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y"').replace('"G6K-2P-Y DC3"','"G6K-2F-Y DC3"').replace('"C1525307"','"C93168"').replace("https://www.lcsc.com/datasheet/C1525307.pdf","https://www.lcsc.com/datasheet/C93168.pdf")
    t=t[:i]+blk+t[j:]
# ---- free-space finder (after removals)
pts=[(float(a),float(b)) for a,b in re.findall(r'\(at ([\d.\-]+) ([\d.\-]+)',t[t.index('\n\t(symbol\n'):])]+[(float(a),float(b)) for a,b in re.findall(r'\(xy ([\d.\-]+) ([\d.\-]+)\)',t)]
used=[]
def find_free(w,h):
    for y in range(20,280,3):
        for x in range(20,400-int(w),3):
            if any(x-6<=px<=x+w+6 and y-6<=py<=y+h+6 for px,py in pts): continue
            if any(not(x+w<ux or x>ux+uw or y+h<uy or y>uy+uh) for ux,uy,uw,uh in used): continue
            used.append((x,y,w,h)); return x,y
    raise SystemExit("no free space for %dx%d"%(w,h))
# ---- library symbols
src=open('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector_Generic.kicad_sym').read()
def get_conn(n):
    nm="Conn_01x%02d"%n; a=src.index('\t(symbol "%s"'%nm); d=0; k=a
    while True:
        c=src[k]
        if c=='(':d+=1
        elif c==')':
            d-=1
            if d==0: break
        k+=1
    txt=src[a:k+1]
    pins={int(num):(float(x),float(y)) for x,y,num in re.findall(r'\(pin passive line\s+\(at ([\-\d.]+) ([\-\d.]+) \d+\)\s+\(length [\d.]+\)\s+\(name "[^"]*"[^)]*\(effects\s+\(font\s+\(size [\d.]+ [\d.]+\)\s+\)\s+\)\s+\)\s+\(number "(\d+)"',txt)}
    assert len(pins)==n,(n,len(pins))
    return txt.replace('(symbol "%s"'%nm,'(symbol "Connector_Generic:%s"'%nm,1),pins
c8,pin8=get_conn(8); c6,pin6=get_conn(6)
def prop(n,v,x,y,hide=False): return f'\t\t(property "{n}" "{v}"\n\t\t\t(at {x} {y} 0)\n'+('\t\t\t(hide yes)\n' if hide else '')+'\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
ls=t.index('(lib_symbols'); dd=0
for kk in range(ls,len(t)):
    if t[kk]=='(':dd+=1
    elif t[kk]==')':
        dd-=1
        if dd==0: le=kk; break
t=t[:le].rstrip('\n\t')+'\n'+c8+'\n'+c6+'\n\t'+t[le:]
# ---- generic instance builder
def inst(lib,ref,value,fp,x,y,pins,extra=()):
    global t
    body=prop("Reference",ref,x,y-14)+prop("Value",value,x,y+14)+prop("Footprint",fp,x,y,True)+prop("Datasheet","",x,y,True)
    for n,v in extra: body+=prop(n,v,x,y,True)
    pn="".join(f'\t\t(pin "{p}"\n\t\t\t(uuid "{U()}")\n\t\t)\n' for p in pins)
    s=f'\t(symbol\n\t\t(lib_id "{lib}")\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n\t\t(uuid "{U()}")\n{body}{pn}\t\t(instances\n\t\t\t(project "audio_companion"\n\t\t\t\t(path "/{ROOT}"\n\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
    k=t.index('\t(sheet_instances'); t=t[:k]+s+t[k:]
# ---- debounce rows: pull-up, series, cap per line
CAP="Capacitor_SMD:C_0402_1005Metric"
lines=[("OA","EXP_ENC_A"),("OB","EXP_ENC_B"),("IA","EXP_ENC_IA"),("IB","EXP_ENC_IB"),("PUSH","EXP_ENC_PUSH")]
dx,dy=find_free(40,5*26)
for k,(nm,deb) in enumerate(lines):
    y=dy+13+k*26; raw="ENC_%s_RAW"%nm; ex_=dx+8
    clone("R8","R-ENC-PU-%s"%nm,"10k",R0402,ex_,y,180); add_label("+3V3",ex_,y-3.81,90); add_label(raw,ex_,y+3.81,270)
    clone("R8","R-ENC-S-%s"%nm,"10k",R0402,ex_+14,y,180); add_label(raw,ex_+14,y-3.81,90); add_label(deb,ex_+14,y+3.81,270)
    clone("C46","C-ENC-%s"%nm,"10nF",CAP,ex_+28,y,0); add_label(deb,ex_+28,y-3.81,90); add_label("GND",ex_+28,y+3.81,270)
# ---- sense resistor K1_COIL_DRIVE -> BYP_STATE
sx_,sy_=find_free(20,26); sx_+=8; sy_+=13
clone("R8","R-BYP-SENSE-1","10k",R0402,sx_,sy_,180); add_label("K1_COIL_DRIVE",sx_,sy_-3.81,90); add_label("BYP_STATE",sx_,sy_+3.81,270)
# ---- encoder and panel connectors (SMT PH side entry)
ex,ey=find_free(40,34); ex+=30; ey+=17
enc_nets={1:"GND",2:"ENC_OA_RAW",3:"ENC_OB_RAW",4:"ENC_IA_RAW",5:"ENC_IB_RAW",6:"ENC_PUSH_RAW",7:"GND",8:"+3V3"}
inst("Connector_Generic:Conn_01x08","J-ENC-1","S8B-PH-SM4-TB","Connector_JST:JST_PH_S8B-PH-SM4-TB_1x08-1MP_P2.00mm_Horizontal",ex,ey,list(range(1,9)),(("MPN","S8B-PH-SM4-TB(LF)(SN)"),("Manufacturer","JST")))
for n,(px,py) in pin8.items(): add_label(enc_nets[n],ex+px,ey-py,180)
px0,py0=find_free(40,28); px0+=30; py0+=14
pan_nets={1:"EXP_PWR_BTN",2:"GND",3:"Q1_GATE",4:"GND",5:"EXP_SPARE5",6:"+3V3"}
inst("Connector_Generic:Conn_01x06","J-PANEL-1","S6B-PH-SM4-TB","Connector_JST:JST_PH_S6B-PH-SM4-TB_1x06-1MP_P2.00mm_Horizontal",px0,py0,list(range(1,7)),(("MPN","S6B-PH-SM4-TB(LF)(SN)"),("Manufacturer","JST")))
for n,(px,py) in pin6.items(): add_label(pan_nets[n],px0+px,py0-py,180)
open(P,"w").write(t); print("done")
