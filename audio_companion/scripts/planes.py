import pcbnew, math
mm=pcbnew.FromMM
W="/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work/audio_companion.kicad_pcb"
b=pcbnew.LoadBoard(W)
for z in list(b.Zones()): b.Remove(z)
for t in list(b.GetTracks()): b.Remove(t)
bb=b.GetBoardEdgesBoundingBox(); m=mm(0.3)
pts=[(bb.GetX()+m,bb.GetY()+m),(bb.GetRight()-m,bb.GetY()+m),(bb.GetRight()-m,bb.GetBottom()-m),(bb.GetX()+m,bb.GetBottom()-m)]
def zone(net,layer,prio=0):
    z=pcbnew.ZONE(b); z.SetLayer(b.GetLayerID(layer)); z.SetNet(b.FindNet(net))
    z.SetIsFilled(False); z.SetAssignedPriority(prio)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.25))
    z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
    o=z.Outline(); o.NewOutline()
    for x,y in pts: o.Append(x,y)
    b.Add(z); return z
print([b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()])
zone("GND","GND"); zone("/+3V3","Power"); zone("/AGND","B.Cu")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(W); print("zones",len(b.Zones()))
