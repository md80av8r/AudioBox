import re, uuid
exec(open("/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/scripts/sch_micdc.py").read().split("\nrename_label(")[0].replace('open(P,"w")','#'))
ROOT="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
# 1. ENC1 pin 4: replace GND with EXP_SPARE1
m=None
for mm in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "power:GND"\)\n\t\t\(at 39\.37 111\.76 (\d+)\)',t): m=mm
assert m
i=m.start()+1; j=t.find('\n\t(symbol\n',i+10)+1; assert '"#PWR' in t[i:j]
t=t[:i]+t[j:]
add_label("EXP_SPARE1",39.37,111.76,180)
# 2. TestPoint lib symbol
src=open('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector.kicad_sym').read()
a=src.index('\t(symbol "TestPoint"'); d=0; k=a
while True:
    c=src[k]
    if c=='(':d+=1
    elif c==')':
        d-=1
        if d==0: break
    k+=1
lib=src[a:k+1].replace('(symbol "TestPoint"','(symbol "Connector:TestPoint"',1).replace('"TestPoint_0_1"','"TestPoint_0_1"')
ls=t.index('(lib_symbols'); le=t.index('\n\t)\n',ls)
t=t[:le]+'\n'+lib+t[le:]
# 3. TP instances
FP="TestPoint:TestPoint_Pad_D1.5mm"
def tp(ref,x,y,net,gnd=False):
    global t
    def prop(n,v,dx,dy,hide=False):
        return f'\t\t(property "{n}" "{v}"\n\t\t\t(at {fmt(x+dx)} {fmt(y+dy)} 0)\n'+('\t\t\t(hide yes)\n' if hide else '')+'\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
    s=(f'\t(symbol\n\t\t(lib_id "Connector:TestPoint")\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom no)\n\t\t(on_board yes)\n\t\t(in_pos_files no)\n\t\t(dnp no)\n\t\t(uuid "{U()}")\n'
       +prop("Reference",ref,0,-6.858)+prop("Value","TP",0,-5.08)+prop("Footprint",FP,5.08,0,True)+prop("Datasheet","",5.08,0,True)
       +f'\t\t(pin "1"\n\t\t\t(uuid "{U()}")\n\t\t)\n\t\t(instances\n\t\t\t(project "audio_companion"\n\t\t\t\t(path "/{ROOT}"\n\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')
    k=t.index('\t(sheet_instances'); t=t[:k]+s+t[k:]
    if gnd:
        global gcount
        n=max(int(v) for v in re.findall(r'"#PWR0*(\d+)"',t))+1
        clone(gsrc,"#PWR%03d"%n,None,None,x,y,0)
    else: add_label(net,x,y,270)
gsrc=[r for r in re.findall(r'"(#PWR0*\d+)"',t) if False] or None
# find a GND power symbol ref
for mm in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "power:GND"\)',t):
    q=t.find('(property "Reference" "',mm.start()); gsrc=re.match(r'\(property "Reference" "([^"]+)"',t[q:]).group(1); break
X0,Y0=58.42,62.0
tps=[("TP1","GND",True),("TP2","GND",True),("TP3","+3V3",False),("TP4","+3V3_A",False),("TP5","+12V",False),("TP6","AGND",False),("TP7","I2C_SDA",False)]
for n,(r,net,g) in enumerate(tps): tp(r,X0+n*7.62,Y0,net,g)
# 4. spare header (clone HDR-CP-R-1)
HX,HY=85.0,100.0
clone("HDR-CP-R-1","J-SPARE-1","SPARE-IO","Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical",HX,HY,0)
t=re.sub(r'(\(property "Value" ")Conn_01x07_Socket"',lambda m:m.group(1)+'SPARE-IO"',t) if False else t
nets=["EXP_SPARE1","EXP_SPARE2","EXP_SPARE3","EXP_SPARE4","EXP_SPARE5",None,"+3V3"]
for p,net in enumerate(nets):
    py=HY-7.62+2.54*p; px=HX-5.08
    if net: add_label(net,px,py,180)
    else:
        n=max(int(v) for v in re.findall(r'"#PWR0*(\d+)"',t))+1
        clone(gsrc,"#PWR%03d"%n,None,None,px,py,0)
open(P,"w").write(t); print("done")
