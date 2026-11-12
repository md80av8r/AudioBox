set -e
S=/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad
W=/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
F='assert|Fontconfig|swig|Debug'
cp $S/pre_place3.kicad_pcb $W/audio_companion.kicad_pcb
$PY $S/place.py 2>&1 | grep -v -E "$F" || true
$PY $S/planes.py 2>&1 | grep -v -E "$F" || true
$PY $S/fanout.py 2>&1 | grep -v -E "$F" || true
$PY - <<P 2>&1 | grep -v -E "swig|Debug" || true
import pcbnew, wx
app=wx.App(False)
b=pcbnew.LoadBoard("$W/audio_companion.kicad_pcb")
print("dsn",pcbnew.ExportSpecctraDSN(b,"$S/ac.dsn"))
P
rm -f $S/ac.ses
java -Djava.awt.headless=true -jar /Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/tools/freerouting/freerouting-2.5.0.jar -de $S/ac.dsn -do $S/ac.ses -mp 25 -l en > $S/fr5.log 2>&1
$PY - <<P 2>&1 | grep -v -E "swig|Debug" || true
import pcbnew, wx
app=wx.App(False)
b=pcbnew.LoadBoard("$W/audio_companion.kicad_pcb")
print("ses",pcbnew.ImportSpecctraSES(b,"$S/ac.ses"))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save("$W/audio_companion.kicad_pcb")
P
cp $W/audio_companion.kicad_pcb $W/audio_companion_routed_v9_pre_strip.kicad_pcb
$PY $S/strip.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 57.6 27 73.6 43 2>&1 | grep -v -E "$F" || true
$PY $S/strip2.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 4.4 2>&1 | grep -v -E "$F" || true
$PY $S/escape.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 2>&1 | grep -v -E "$F" || true
for pass in 1 2 3; do
  $K pcb drc --format report -o $S/drcP.rpt --severity-error $W/audio_companion.kicad_pcb > /dev/null 2>&1
  python3 $S/parse_unc.py $S/drcP.rpt $S/pairsP.json
  if grep -q '^0 pairs' <(python3 $S/parse_unc.py $S/drcP.rpt $S/pairsP.json); then break; fi
  $PY $S/dump_items.py $W/audio_companion.kicad_pcb $S/itemsP.json 2>&1 | grep -v -E "$F" || true
  python3 $S/maze.py $S/itemsP.json $S/pairsP.json $S/routesP.json > $S/mazeP$pass.log 2>&1 || true
  tail -1 $S/mazeP$pass.log | cut -c1-600
  $PY $S/apply_routes.py $W/audio_companion.kicad_pcb $S/routesP.json $W/audio_companion.kicad_pcb 2>&1 | grep -v -E "$F" || true
  $PY $S/dedupe.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 0.5 2>&1 | grep -v -E "$F" || true
done
$K pcb drc --format report -o $S/drcF.rpt --severity-error $W/audio_companion.kicad_pcb > /dev/null 2>&1
grep -E "^\[" $S/drcF.rpt | sed 's/ \[.*//; s/ (board.*//' | sort | uniq -c | sort -rn
grep "^\*\* Found" $S/drcF.rpt
echo PIPELINE5_DONE
