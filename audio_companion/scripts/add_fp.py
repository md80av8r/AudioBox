import pcbnew, sys
path,ref,value,lib,name=sys.argv[1:6]
b=pcbnew.LoadBoard(path)
fp=pcbnew.FootprintLoad("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"+lib+".pretty",name)
fp.SetReference(ref); fp.SetValue(value)
fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(130),pcbnew.FromMM(60))); b.Add(fp); b.Save(path); print("added",ref)
