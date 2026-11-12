"""Score template: real instruments (Lemo sampler) + synth bed + Lemo SFX, every cue from build/timeline.json.
Run `ensure-instruments build/score.py` first (it downloads only the libraries this file names), then `python3 build/score.py`.
Output: build/audio/music_sfx.wav (48 kHz stereo). Edit SECTIONS / HITS from the sound brief; keep the structure."""
import json, os, sys
import numpy as np, soundfile as sf
VT = os.environ.get("VIDEO_TOOLS", os.path.expanduser("~/video-tools")); sys.path.insert(0, os.path.join(VT, "Lemo-Opuscar"))
from core.audio import sampler as S, sfx as X
from core.audio.sfx import SR

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "timeline.json"))); C = T["cues"]; DUR = T["duration"]
BPM = T.get("bpm", 120); BEAT = 60 / BPM
buf = np.zeros((int(SR * DUR), 2), np.float32)

# --- 1. Music: one entry per section of the sound brief -------------------------------------------
# (time, instrument, pitch | variant for unpitched | None, dur, velocity, pan)   instrument names: `ensure-instruments --list`
notes = []
def chord(t, inst, pitches, d, v=.5, pan=0): notes.extend((t, inst, p, d, v, pan) for p in pitches)
def pulse(t0, t1, inst, pitch, every, v=.6, pan=0):
    t = t0
    while t < t1 - 1e-3: notes.append((t, inst, pitch, every * .9, v, pan)); t += every

# EXAMPLE (replace from the brief): tense intro -> reveal -> driving middle -> warm finale
chord(0, 'cellos', ['D2', 'A2'], C.get("logo", 8) , .35)                       # low tension bed
pulse(C.get("promise", 10), C.get("final", 40), 'cellos_spic', 'D3', BEAT / 2, .45, -.2)   # ostinato drive
chord(C.get("promise", 10), 'violins', ['D4', 'F4', 'A4'], C.get("final", 40) - C.get("promise", 10), .3, .2)
chord(C.get("final", 40), 'horn', ['D3', 'A3', 'D4', 'F#4'], DUR - C.get("final", 40), .55)  # major lift at the end
notes.append((C.get("logo", 8), 'timpani', 'A2', 2.0, .8, 0))
notes.append((C.get("final", 40), 'gran_cassa', 'hit', None, .8, 0))   # unpitched: pitch slot = variant
music = S.render(notes, dur=DUR)
music = S.room(music, size=.5, mix=.2)
buf += music[:len(buf)] * 0.8

# --- 2. SFX: one per storyboard beat ---------------------------------------------------------------
def add(x, at, g=1.0, pan=0.0): X.add(buf, x.astype(np.float32), at, g, pan)
for k, at in C.items():                       # a whoosh into every scene change (cue names starting with "ui_" or "s")
    if k.startswith(("ui_", "s")): add(X.whoosh(.4), at - .3, .5, .3)
for k in ("logo", "final"):                   # big impacts on the reveal and the finale
    if k in C: add(X.ignite(1.0), C[k], .9); add(X.thump(.8, 55), C[k], .6)
if "cta" in C: add(X.ding(.5), C["cta"], .6)

# --- 3. Master ---------------------------------------------------------------------------------------
for ch in (0, 1): buf[:, ch] = X.limit(buf[:, ch], .9)
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
sf.write(os.path.join(HERE, "audio", "music_sfx.wav"), buf, SR); print("music_sfx.wav", DUR, "s")
