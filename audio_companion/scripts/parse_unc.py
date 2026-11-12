import re, json, sys
t=open(sys.argv[1]).read().split("\n"); pairs=[]; i=0
def parse(line):
    m=re.match(r'\s*@\(([-\d.]+) mm, ([-\d.]+) mm\): (.*)',line)
    if not m: return None
    x,y,rest=float(m.group(1)),float(m.group(2)),m.group(3)
    net=re.search(r'\[(.*?)\]',rest).group(1)
    if rest.startswith("Track"): L=["F"] if "F.Cu" in rest else ["B"]
    elif rest.startswith("Via") or rest.startswith("PTH"): L=["F","B"]
    else: L=["F"] if "F.Cu" in rest else ["B"]
    return dict(c=[x,y],net=net,layers=L,desc=rest[:40])
while i<len(t):
    if t[i].startswith("[unconnected_items]"):
        ats=[parse(l) for l in t[i+1:i+5] if l.strip().startswith("@")]
        if len(ats)>=2 and ats[0]["net"]==ats[1]["net"]: pairs.append(dict(net=ats[0]["net"],a=ats[0],b=ats[1]))
        i+=3
    else: i+=1
json.dump(pairs,open(sys.argv[2],"w")); print(len(pairs),"pairs")
