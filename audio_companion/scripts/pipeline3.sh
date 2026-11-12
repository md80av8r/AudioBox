set -e
S=/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad
W=/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
F='assert|Fontconfig|swig|Debug'
cp $W/audio_companion_routed_v5_pre_strip.kicad_pcb $W/audio_companion.kicad_pcb
$PY $S/strip.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 57.6 27 73.6 43 2>&1 | grep -v -E "$F" || true
$PY $S/strip2.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 4.4 2>&1 | grep -v -E "$F" || true
$PY $S/escape.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 2>&1 | grep -v -E "$F" || true
$K pcb drc --format report -o $S/drcA.rpt --severity-error $W/audio_companion.kicad_pcb > /dev/null 2>&1
grep -E "^\[" $S/drcA.rpt | sed 's/ \[.*//; s/ (board.*//' | sort | uniq -c | sort -rn
python3 $S/parse_unc.py $S/drcA.rpt $S/pairsA.json
$PY $S/dump_items.py $W/audio_companion.kicad_pcb $S/itemsA.json 2>&1 | grep -v -E "$F" || true
python3 $S/maze.py $S/itemsA.json $S/pairsA.json $S/routesA.json > $S/mazeA.log 2>&1 || true
tail -1 $S/mazeA.log | cut -c1-900
$PY $S/apply_routes.py $W/audio_companion.kicad_pcb $S/routesA.json $W/audio_companion.kicad_pcb 2>&1 | grep -v -E "$F" || true
$PY $S/dedupe.py $W/audio_companion.kicad_pcb $W/audio_companion.kicad_pcb 0.38 2>&1 | grep -v -E "$F" || true
$K pcb drc --format report -o $S/drcB.rpt --severity-error $W/audio_companion.kicad_pcb > /dev/null 2>&1
grep -E "^\[" $S/drcB.rpt | sed 's/ \[.*//; s/ (board.*//' | sort | uniq -c | sort -rn
echo PIPELINE3_DONE
