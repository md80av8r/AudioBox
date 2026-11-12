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

rename_label("MIC_AMPLIFIED","MIC_TO_RELAY",105.41,273.05)
add_label("MIC_PREAMP_OUT",251.46,215.27,0)
clone("C46","C-MIC-AIR","1uF 25V","Capacitor_SMD:C_0402_1005Metric",127.0,152.4,0)
add_label("MIC_PREAMP_OUT",127.0,152.4-3.81,90); add_label("MIC_TO_RELAY",127.0,152.4+3.81,270)
open(P,"w").write(t); print("mic DC block added")
