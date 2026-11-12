import re, uuid
P="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_sch"
t=open(P).read()
u=lambda: str(uuid.uuid4())
def span(ref):
    for m in re.finditer(r'\t\(symbol\n\t\t\(lib_id "[^"]+"\)\n\t\t\(at [\d.\-]+ [\d.\-]+ \d+\)',t):
        i=m.start(); j=t.find('\n\t(symbol\n',i+10); j=len(t) if j<0 else j+1
        if f'(property "Reference" "{ref}"' in t[i:j]: return i,j
    raise SystemExit("no "+ref)
# 1. D3 rotate 180
i,j=span("D3"); blk=t[i:j]; assert "(at 372.11 124.46 0)" in blk
t=t[:i]+blk.replace("(at 372.11 124.46 0)","(at 372.11 124.46 180)",1)+t[j:]
# 2. footprints/values for 22uF caps on +12V and +BATT
for r,val in (("C46","22uF 25V"),("C29","22uF 10V"),("C31","22uF 10V"),("C32","22uF 10V")):
    i,j=span(r); blk=t[i:j]
    blk=blk.replace("Capacitor_SMD:C_0402_1005Metric","Capacitor_SMD:C_0805_2012Metric")
    blk=re.sub(r'\(property "Value" "[^"]*"','(property "Value" "%s"'%val,blk,1)
    t=t[:i]+blk+t[j:]
# 3. clone C46 -> C51 at (394.0,132.08)
i,j=span("C46"); c=t[i:j]
c=c.replace('"C46"','"C51"').replace("375.92 132.08","394 132.08").replace("388.62","406.7").replace("375.92","394")
c=re.sub(r'\(property "Reference" "C51"\n\t\t\t\(at [\d.\-]+ [\d.\-]+ 0\)',lambda m:m.group(0),c)
for ou in set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)',c)): c=c.replace(ou,u())
for ou in set(re.findall(r'\(pin "[12]"\n\t\t\t\(uuid "([0-9a-f-]{36})"',c)): c=c.replace(ou,u())
t=t[:j]+c+t[j:]
# 4. clone GND power symbol at (375.92,135.89) -> (394,135.89)
for m in re.finditer(r'\t\(symbol\n\t\t\(lib_id "power:GND"\)\n\t\t\(at 375\.92 135\.89 0\)',t):
    gi=m.start(); gj=t.find('\n\t(symbol\n',gi+10)+1; g=t[gi:gj]; break
nums=[int(x) for x in re.findall(r'"#PWR0*(\d+)"',t)]; nn=max(nums)+1
g=g.replace("375.92 135.89","394 135.89")
g=re.sub(r'"#PWR0*\d+"','"#PWR%02d"'%nn,g)
for ou in set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)',g)): g=g.replace(ou,u())
for ou in set(re.findall(r'\(pin "1"\n\t\t\t\(uuid "([0-9a-f-]{36})"',g)): g=g.replace(ou,u())
t=t[:gj]+g+t[gj:]
# 5. +12V label at C51 pin1 end
lab=f'\t(label "+12V"\n\t\t(at 394 128.27 90)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n'
k=t.index('\t(sheet_instances'); t=t[:k]+lab+t[k:]
open(P,"w").write(t); print("ok")
