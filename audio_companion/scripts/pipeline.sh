set -e
S=/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad
W=/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
cp $S/pre_place.kicad_pcb $W/audio_companion.kicad_pcb
$PY $S/place.py 2>&1 | grep -v -E "assert|Fontconfig|swig|Debug" || true
$PY $S/planes.py 2>&1 | grep -v -E "assert|Fontconfig|swig|Debug" || true
$PY $S/fanout.py 2>&1 | grep -v -E "assert|Fontconfig|swig|Debug" || true
$PY - <<P 2>&1 | grep -v -E "swig|Debug" || true
import pcbnew, wx
app=wx.App(False)
b=pcbnew.LoadBoard("$W/audio_companion.kicad_pcb")
print("dsn",pcbnew.ExportSpecctraDSN(b,"$S/ac.dsn"))
P
rm -f $S/ac.ses
java -Djava.awt.headless=true -jar /Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/tools/freerouting/freerouting-2.5.0.jar -de $S/ac.dsn -do $S/ac.ses -mp 25 -l en > $S/fr2.log 2>&1
$PY - <<P 2>&1 | grep -v -E "swig|Debug" || true
import pcbnew, wx
app=wx.App(False)
b=pcbnew.LoadBoard("$W/audio_companion.kicad_pcb")
print("ses",pcbnew.ImportSpecctraSES(b,"$S/ac.ses"))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save("$W/audio_companion.kicad_pcb")
P
echo PIPELINE_DONE
