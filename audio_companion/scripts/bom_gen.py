import xml.etree.ElementTree as ET, csv, collections, sys, os
NET=sys.argv[1]; OUT=sys.argv[2]
# (value, footprint-name) -> (MPN, LCSC, kind, package label, note)  kind: SMT = JLCPCB assembles, HAND = you solder
M={
 ("100nF","C_0402_1005Metric"):("CL05B104KO5NNNC","C1525","SMT","0402","100nF 16V X7R"),
 ("10uF","C_0402_1005Metric"):("CL05A106MQ5NUNC","C15525","SMT","0402","10uF 6.3V X5R (3V3 rails only)"),
 ("1uF","C_0402_1005Metric"):("CL05A105KA5NQNC","C52923","SMT","0402","1uF 25V X5R"),
 ("1uF 25V","C_0402_1005Metric"):("CL05A105KA5NQNC","C52923","SMT","0402","1uF 25V X5R - mic DC block, keep >=16V"),
 ("10uF","C_0805_2012Metric"):("CL21A106KAYNNNE","C15850","SMT","0805","10uF 25V X5R"),
 ("22uF 10V","C_0805_2012Metric"):("CL21A226MAQNNNE","C45783","SMT","0805","22uF 25V X5R (covers 10V use)"),
 ("22uF 25V","C_0805_2012Metric"):("CL21A226MAQNNNE","C45783","SMT","0805","22uF 25V X5R - boost output, must be >=25V"),
 ("220UF","CP_EIA-6032-28_Kemet-C"):("T491C227M006AT","C1952817","SMT","6032-28","220uF 6.3V tantalum - + toward pad 1 marking"),
 ("220uF 6.3V","CP_EIA-6032-28_Kemet-C"):("T491C227M006AT","C1952817","SMT","6032-28","220uF 6.3V tantalum - headphone output coupling, + toward TPA"),
 ("SS14","D_SMA"):("SS14","C2480","SMT","SMA","Schottky 40V 1A - boost rectifier"),
 ("1N4148WS","D_SOD-323"):("1N4148WS","C2128","SMT","SOD-323","relay flyback"),
 ("SPM6530T-4R7M","IND-SMD_L7.1-W6.5"):("SPM6530T-4R7M","C76857","SMT","7.1x6.5","TDK 4.7uH 5.6A"),
 ("FerriteBead","L_0603_1608Metric"):("BLM18AG601SN1D","C19330","SMT","0603","600R@100MHz 500mA"),
 ("LED Green","LED_0603_1608Metric"):("KT-0603G","C12624","SMT","0603","PWR - emerald green"),
 ("LED Yellow","LED_0603_1608Metric"):("KT-0603Y","C2287","SMT","0603","ACTIVE - yellow"),
 ("LED White","LED_0603_1608Metric"):("KT-0603W","C2290","SMT","0603","ANR 12V - white"),
 ("LED Red","LED_0603_1608Metric"):("KT-0603R","C2286","SMT","0603","BYPASS - red"),
 ("0","R_0402_1005Metric"):("0402WGF0000TCE","C17168","SMT","0402","0R AGND/GND tie"),
 ("10R","R_0402_1005Metric"):("0402WGF100JTCE","C25077","SMT","0402","10R"),
 ("100R","R_0402_1005Metric"):("0402WGF1000TCE","C25076","SMT","0402","100R"),
 ("330R","R_0402_1005Metric"):("0402WGF3300TCE","C25104","SMT","0402","330R"),
 ("1k","R_0402_1005Metric"):("0402WGF1001TCE","C11702","SMT","0402","1k"),
 ("2.2k","R_0402_1005Metric"):("0402WGF2201TCE","C25879","SMT","0402","2.2k"),
 ("10k","R_0402_1005Metric"):("0402WGF1002TCE","C25744","SMT","0402","10k"),
 ("22k","R_0402_1005Metric"):("0402WGF2202TCE","C25768","SMT","0402","22k"),
 ("100k","R_0402_1005Metric"):("0402WGF1003TCE","C25741","SMT","0402","100k"),
 ("200k","R_0402_1005Metric"):("0402WGF2003TCE","C25764","SMT","0402","200k"),
 ("ES8388","QFN-28-1EP_4x4mm_P0.45mm_EP2.6x2.6mm"):("ES8388","C365736","SMT","QFN-28-EP(4x4)","audio codec"),
 ("DRV2605LDGSR","VSSOP-10_L3.0-W3.0-P0.50-LS4.9-BL"):("DRV2605LDGSR","C527464","SMT","VSSOP-10","haptic driver"),
 ("PCA9534APWR","TSSOP-16_L5.0-W4.4-P0.65-LS6.4-BL"):("PCA9534APWR","C2871127","SMT","TSSOP-16","I2C IO expander"),
 ("MCP6022","SOIC-8_3.9x4.9mm_P1.27mm"):("MCP6022T-I/SN","C57639","SMT","SOIC-8","dual op amp"),
 ("TPA6111A2DR","SOIC-8_L5.0-W4.0-P1.27-LS6.0-BL"):("TPA6111A2DR","C497472","SMT","SOIC-8","headphone amp"),
 ("MT3608","SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL"):("MT3608","C84817","SMT","SOT-23-6","12V boost"),
 ("2N7002","SOT-23"):("2N7002","C8545","SMT","SOT-23","relay driver (superseded by AO3400A)"),
 ("AO3400A","SOT-23"):("AO3400A","C20917","SMT","SOT-23","relay driver, logic-level 30V 5.7A, Basic"),
 ("BYPASS","SW_SPST_TL3305A"):("TL3305AF260QG","C2886902","SMT","4.5x4.5 SMD","emergency bypass button 260gf"),
 # hand-soldered through-hole parts
 ("G6K-2P-Y DC3","RELAY-TH_G6K-2P-Y"):("G6K-2P-Y DC3","C1525307","HAND","THT","Omron DPDT 3V coil"),
 ("B2B-PH-K-S","JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"):("B2B-PH-K-S(LF)(SN)","C131337","HAND","THT","battery tap, vertical"),
 ("S2B-PH-K-S","JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal"):("S2B-PH-K-S(LF)(SN)","C173752","HAND","THT","JST PH 2-pin side entry"),
 ("S3B-PH-K-S","JST_PH_S3B-PH-K_1x03_P2.00mm_Horizontal"):("S3B-PH-K-S(LF)(SN)","C157929","HAND","THT","JST PH 3-pin side entry"),
 ("S4B-PH-K-S","JST_PH_S4B-PH-K_1x04_P2.00mm_Horizontal"):("S4B-PH-K-S(LF)(SN)","C157926","HAND","THT","JST PH 4-pin side entry"),
 ("S5B-PH-K-S","JST_PH_S5B-PH-K_1x05_P2.00mm_Horizontal"):("S5B-PH-K-S(LF)(SN)","C157923","HAND","THT","JST PH 5-pin side entry"),
 ("EC10E1220503","SW-TH_EC10EXXXXXXX"):("EC10E1220503","C110291","HAND","THT","Alps encoder 24/12 - CHECK if it has a push switch (pins 4,5 on GND)"),
 ("Tactile 6x6","SW_PUSH_6mm"):("PTS645SL43-2LFS","C221874","HAND","THT","6x6 tactile 4.3mm - power button"),
 ("LEMO-6P","PinHeader_1x06_P2.54mm_Vertical"):("2.54-1*40 header (cut to 6)","C2977586","HAND","THT","LEMO pigtail header"),
 ("Conn_01x07_Socket","PinHeader_1x07_P2.54mm_Vertical"):("1x7 male header, 19mm LONG pins","NOT_ON_LCSC","HAND","THT","stack-on to CrowPanel - source separately, pin length must bridge the 10mm gap"),
 ("SolderJumper","SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm"):("(PCB pads only)","-","NONE","pads","MIC BIAS jumper - bridge with solder to enable electret bias"),
}
t=ET.parse(NET).getroot()
rows=collections.defaultdict(list); missing=[]
for c in t.find("components"):
    ref=c.get("ref"); v=c.findtext("value") or ""; fp=(c.findtext("footprint") or "").split(":")[-1]
    key=(v,fp)
    if key not in M:
        # case-insensitive value match
        cand=[k for k in M if k[1]==fp and k[0].lower()==v.lower()]
        key=cand[0] if cand else key
    if key in M: rows[key].append(ref)
    else: missing.append((ref,v,fp))
def natural(r):
    import re
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)',r)]
full=[];jlc=[];hand=[]
for key,refs in sorted(rows.items(),key=lambda kv:(M[kv[0]][2],M[kv[0]][1],kv[0])):
    mpn,lcsc,kind,pkg,note=M[key]; refs=sorted(refs,key=natural); d=",".join(refs)
    full.append([key[0],d,len(refs),pkg,mpn,lcsc,{"SMT":"JLCPCB assembles","HAND":"hand solder","NONE":"no part"}[kind],note])
    if kind=="SMT": jlc.append([f"{key[0]} {mpn}",d,pkg,lcsc])
    if kind=="HAND": hand.append([mpn,lcsc,len(refs),d,note])
_m=collections.OrderedDict()
for c,dd,pk,l in jlc:
    if l in _m: _m[l][1]+=","+dd
    else: _m[l]=[c,dd,pk,l]
jlc=[v[:] for v in _m.values()]
for r in jlc: r[1]=",".join(sorted(r[1].split(","),key=natural))
os.makedirs(OUT,exist_ok=True)
with open(OUT+"/BOM_full.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["Value","Designators","Qty","Package","Manufacturer part","LCSC #","Assembly","Notes"]); w.writerows(full)
with open(OUT+"/JLCPCB_BOM.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["Comment","Designator","Footprint","JLCPCB Part #"]); w.writerows(jlc)
with open(OUT+"/HAND_SOLDER_parts_to_buy.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["Part","LCSC #","Qty on board","Designators","Notes (buy 1-2 spares)"]); w.writerows(hand)
smt=sum(len(r.split(",")) for _,r,*_ in [(x[0],x[1]) for x in jlc]); print("BOM lines SMT",len(jlc),"SMT parts",smt,"| hand lines",len(hand),"| unmapped",missing)
print("total parts mapped",sum(len(v) for v in rows.values()))
