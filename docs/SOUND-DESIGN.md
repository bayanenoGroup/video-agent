# Sound design: how the agent scores a video on its own

The user only says something like "make this motion and take care of the music and sound effects". Everything below is the agent's job; the user never names instruments, libraries or commands.

## 1. Write the sound brief (`build/sound-brief.md`)

Derive it from the scenario, storyboard, narration timing and reference video. One table row per section of the video:

| Section | Time | Story job | Mood / energy (1-5) | Tempo & key | Instruments (sampler names) | Synth layers | SFX per beat |
|---|---|---|---|---|---|---|---|

How to fill it:

- **Story job → mood.** A problem or pain section is tense: minor key, low drones, sparse, energy 2-3. A reveal is a riser, then ~0.5 s of silence, then an impact. A solution or demo section drives: ostinato and pulse, energy 3-4. The finale is a major lift, the widest voicing, energy 5, then a tail.
- **Tempo.** Use the reference video's tempo (`givemotion audio reference.mp4`). With no reference, use 120 BPM for tech or product videos, 90-100 for calm or explainers, and 128-140 for hype.
- **Key.** Pick one key for the whole video. Use the relative minor for tension and the major for the lift (D minor → F major, or a D major finale).
- **Instruments.** Choose them from the style table (§3). When the reference sounds electronic, keep the synth layers from `templates/example-9router/audio.py` and add real instruments only where they help (strings for tension, horns for the lift, timpani for hits).
- **SFX.** Every visible event gets a sound: scene change → whoosh, logo or reveal → ignite + thump, UI click → step or pop, typing → tick runs, error → beep or glitch, counter → tick roll, notification → two-tone ping, CTA → ding. Each one sits exactly on its cue from `timeline.json`.
- **Narration.** Duck the music under the voice (`data-duck`). Keep pads and strings below 1 kHz busy and leave 1-4 kHz free for the voice.

## 2. Turn the brief into code

1. Copy `templates/score_template.py` to `build/score.py`. Replace the EXAMPLE block with the brief's sections, keeping every time as a `timeline.json` cue.
2. Run `ensure-instruments build/score.py`. It reads the file, works out which sample libraries hold those instruments, and downloads only those (karoryfer 78 MB, salamander 218 MB, vcsl 271 MB, vsco2ce 395 MB, freepats 416 MB). Libraries already on disk are skipped. Do this without asking the user, and report the downloads in the final summary.
3. Run `python3 build/score.py`, which writes `build/audio/music_sfx.wav`. Check the peak with `ffmpeg -af volumedetect` (aim for about −1 dBFS peak) and listen through the timeline by checking that `givemotion audio` finds the beat you meant.
4. If a download fails or a library is missing, replace those parts with the synth equivalents from `audio.py` (saw pad for strings, sine/tanh bass, noise snare), finish the video, and say so.

Unpitched instruments take the variant in the pitch slot: `(t, 'gran_cassa', 'hit', None, .8, 0)`, `(t, 'sus_cymbal', 'roll', None, .5, 0)`. Run `ensure-instruments --list` to see every name and its library.

## 3. Instruments by style (from Lemo-Opuscar `core/audio/INSTRUMENTS.md` §6)

| Feel | Combination |
|---|---|
| Tech / product / motion reel | synth bed (audio.py) + `cellos_spic` ostinato + `violins_trem` tension + `timpani` / `gran_cassa` hits + `horn` lift |
| Orchestral / epic / documentary | `violins` `violas` `cellos` `contrabass` bed + `horn` `trombone` `tuba` + `timpani` `gran_cassa` `sus_cymbal:roll` `gong` |
| Gentle / handmade / kids | `glockenspiel` `kalimba` `harp` `vibraphone` `hand_chimes` `ukulele` `guitar_nylon` + `clarinet` `flute` |
| Jazz / café | `piano` `jazz_bass` `alto_sax` `tenor_sax` `trumpet_mute` `vibraphone_hard` + `drum_kit` `snare2:taps` `claps` |
| Pop / upbeat | `drum_kit` `electric_bass` `electric_guitar` `piano` `glockenspiel` `claps` `shaker` `tambourine` |
| Cold / ethereal / sci-fi | `vibraphone_bowed` `glass` `hang` `sus_cymbal:bow` `violins_trem` (soft) + `S.room(size=.9, mix=.35)` |
| Persian / Middle-Eastern colour | `dan_tranh` (santur-like plucks) `frame_drum` (daf-like) `world_perc` (darbuka) `oboe` / `clarinet` lines in a dastgah-like mode (e.g. Shur ≈ D Phrygian) |
| Retro / old film | `honky_tonk` `upright` `accordion` `harmonica` `clarinet` `tuba_stac` |

## 4. Licences

The samples are CC0 except Salamander piano (CC BY 3.0) and the MuldjordKit drums (CC BY 4.0). If `piano` or `drum_kit` is used, put a credit line in the report and the video description, using the wording from INSTRUMENTS.md §4.
