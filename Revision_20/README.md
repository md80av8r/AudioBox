# Revision 20 (v20) - Audio Companion respin

Started 2026-11-12. Base: as-ordered Y15 board (`../audio_companion/audio_companion.kicad_pcb`, fab_v7) plus the v19 respin work (`../audio_companion/audio_companion_v19_r3.kicad_pcb`).

## Folders
- `jlcpcb_docs/` - drop the JLCPCB documents for the ordered board here (BOM, CPL/placement, gerbers, order confirmation, assembly preview). Used to confirm reference designators and part numbers against the real board.
- KiCad v20 files go in this folder once the base is confirmed (not copied yet).

## Single source of truth
The v20 change list is `../audio_companion/RESPIN_CHECKLIST.md` (section "v20 MUST-FIX list"). Do not keep a second list here. Bench findings: `../BRINGUP_TODO.md`. Lessons learned: `../docs/Audio_Companion_Lessons_Learned.pdf`.

## First steps
1. Confirm refs/parts from the JLCPCB docs (e.g. U8 = TPA6111A2 amp; relays = HEADPHONE_BYPASS-1 / MIC_BYPASS-1).
2. Choose the base board and copy it here as `audio_companion_v20.*`.
3. Apply the must-fix list.
