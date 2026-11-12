import re, uuid
P="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_sch"
t=open(P).read()
def u(): return str(uuid.uuid4())
def label_block(name,x,y):
    return f'\t(label "{name}"\n\t\t(at {x} {y} 180)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify right bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n'
# 1. pin1 label I2S_DIN -> MCLK
old='\t(label "I2S_DIN"\n\t\t(at 172.72 261.62 180)'
assert t.count(old)==1
t=t.replace(old,'\t(label "MCLK"\n\t\t(at 172.72 261.62 180)')
# 2. remove MCLK label at pin 4, add no_connect
m=re.search(r'\t\(label "MCLK"\n\t\t\(at 172\.72 269\.24 180\)\n.*?\n\t\)\n',t,re.S)
assert m
t=t[:m.start()]+f'\t(no_connect\n\t\t(at 172.72 269.24)\n\t\t(uuid "{u()}")\n\t)\n'+t[m.end():]
# 3. pin 5: remove no_connect, add I2S_DIN label
old='\t(no_connect\n\t\t(at 172.72 271.78)\n\t\t(uuid "cb583a0a-71c2-45ff-9714-0ebd03fc9136")\n\t)\n'
assert t.count(old)==1
t=t.replace(old,label_block("I2S_DIN",172.72,271.78))
# 4. battery tap connector cloned from PTT_PASS/GND-1
i=t.index('\t(symbol\n\t\t(lib_id "Connector_Generic:Conn_01x02")\n\t\t(at 386.08 71.12 0)')
j=t.index('\t(symbol\n',i+10)
blk=t[i:j]
nb=blk.replace('PTT_PASS/GND-1','J-BAT-1').replace('(at 386.08 71.12 0)','(at 386.08 95.25 0)').replace('(at 388.62 71.1199 0)','(at 388.62 95.2499 0)').replace('(at 388.62 73.6599 0)','(at 388.62 97.7899 0)').replace('(at 386.08 71.12 0)','(at 386.08 95.25 0)')
nb=nb.replace('JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal','JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical').replace('"B2B-PH-K-S"','"B2B-PH-K-S"')
for old_u in re.findall(r'\(uuid "([0-9a-f-]{36})"\)',nb): nb=nb.replace(old_u,u())
# fix: footprint property 'at' lines
nb=nb.replace('(at 386.08 71.12 0)\n\t\t\t(hide yes)','(at 386.08 95.25 0)\n\t\t\t(hide yes)')
t=t[:j]+nb+t[j:]
# labels on pin ends (pin1 +BATT at y95.25, pin2 GND at y97.79, x=381)
lab=label_block("+BATT",381,95.25)+label_block("GND",381,97.79)
k=t.index('\t(sheet_instances')
t=t[:k]+lab+t[k:]
open(P,"w").write(t)
print("ok")
