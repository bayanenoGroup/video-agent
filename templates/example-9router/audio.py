"""Generate music bed + SFX in code, synced to timeline.json. Output: audio/music_sfx.wav (48k stereo float)."""
import json, wave, numpy as np, os, sys
sys.path.insert(0, os.path.join(os.environ.get("VIDEO_TOOLS", os.path.expanduser("~/video-tools")), "Lemo-Opuscar"))
from core.audio import sfx as LS  # Lemo-Opuscar procedural SFX + limiter
HERE = os.path.dirname(__file__)
T = json.load(open(os.path.join(HERE, "timeline.json")))
C = T["cues"]; SR = 48000; DUR = T["duration"]; N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def t_arr(d): return np.arange(int(SR * d)) / SR
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), N - i)
    if n <= 0: return
    L[i:i+n] += sig[:n] * gain * (1 - max(pan, 0)); R[i:i+n] += sig[:n] * gain * (1 + min(pan, 0))
def lp(x, fc):  # FFT brickwall-ish lowpass with soft knee
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    X *= 1 - 1 / (1 + (f / max(fc,1)) ** 4); return np.fft.irfft(X, len(x))
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def env(n, a, d):  # attack/decay exp envelope, seconds
    t = np.arange(n) / SR; return np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)

# ---------- instruments ----------
def kick(g=1.0):
    t = t_arr(0.45); f = 45 + 110 * np.exp(-t * 28); ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * env(len(t), 0.002, 0.16) * g
def impact():
    n = int(SR*1.8); thump = np.pad(LS.thump(0.7, 60), (0, n - int(SR*.35)))
    return LS.ignite(1.0) * 0.9 + thump * 0.6
def _old_impact():
    t = t_arr(2.2); f = 38 + 90*np.exp(-t*9); ph = 2*np.pi*np.cumsum(f)/SR
    sub = np.sin(ph) * env(len(t), 0.003, 0.7)
    nz = lp(rng.standard_normal(len(t)), 2500) * env(len(t), 0.001, 0.12) * 0.6
    return np.tanh((sub + nz) * 1.6) * 0.9
def whoosh(d=0.6, up=True):
    return LS.whoosh(d, 0.55)
def _old_whoosh(d=0.6, up=True):
    n = int(SR*d); x = rng.standard_normal(n); t = np.arange(n)/n
    out = np.zeros(n); seg = 8
    for k in range(seg):  # sweeping band
        a, b = k*n//seg, (k+1)*n//seg; c = (k+.5)/seg; c = c if up else 1-c
        out[a:b] = bp(x, 300+3000*c, 900+7000*c)[a:b]
    shape = np.sin(np.pi*t) ** 2
    return out * shape * 0.5
def tick(f=2400, g=0.25):
    return LS.step(1.0) * g * 0.9 if f < 2000 else LS.pop(1.0)[:int(SR*.06)] * g * 0.6
def _old_tick(f=2400, g=0.25):
    t = t_arr(0.06); return np.sin(2*np.pi*f*t) * env(len(t), 0.0005, 0.012) * g
def hat(g=0.08):
    n = int(SR*0.05); return hp(rng.standard_normal(n), 7000) * env(n, 0.0005, 0.012) * g
def snare(g=0.35):
    n = int(SR*0.25); return (bp(rng.standard_normal(n), 1200, 6000)*0.7 + np.sin(2*np.pi*190*np.arange(n)/SR)*0.4) * env(n, 0.001, 0.07) * g
def beep():
    t = t_arr(0.38); s = np.sign(np.sin(2*np.pi*880*t)) * 0.35 + np.sin(2*np.pi*440*t)*0.3
    s[int(.12*SR):int(.18*SR)] = 0; return lp(s, 4000) * env(len(t), .002, .3) * 0.5
def notif(f1=1320, f2=1760):
    t = t_arr(0.22); s = np.where(t < 0.07, np.sin(2*np.pi*f1*t), np.sin(2*np.pi*f2*t))
    return s * env(len(t), .002, .08) * 0.3
def buzz():
    t = t_arr(0.7); s = np.sin(2*np.pi*150*t) * (0.5+0.5*np.sign(np.sin(2*np.pi*6*t)))
    return lp(np.tanh(s*3), 900) * env(len(t), .01, .5) * 0.5
def counter():
    out = np.zeros(int(SR*0.7))
    for k in range(14):
        tk = tick(1800+60*k, 0.15); i = int(k*0.045*SR); out[i:i+len(tk)] += tk
    return out
def glitch():
    n = int(SR*0.35); x = rng.standard_normal(n); t = np.arange(n)/SR
    gate = (np.sin(2*np.pi*38*t) > 0).astype(float)
    s = np.sign(np.sin(2*np.pi*(300+2000*rng.random())*t)) * 0.3 + bp(x, 800, 5000)*0.5
    return s * gate * env(n, .001, .2) * 0.5
def riser(d):
    n = int(SR*d); t = np.arange(n)/n; x = rng.standard_normal(n); out = np.zeros(n)
    for k in range(10):
        a, b = k*n//10, (k+1)*n//10; c = (k+.5)/10
        out[a:b] = bp(x, 200+5000*c**2, 800+10000*c**2)[a:b]
    tone = np.sin(2*np.pi*np.cumsum(110+880*t**2)/SR) * 0.25
    return (out*0.6 + tone) * t**2 * 0.7
def chord_pad(freqs, d, g=0.12):
    t = t_arr(d); s = np.zeros(len(t))
    for f in freqs:
        for det in (-0.25, 0.25):
            ph = 2*np.pi*(f+det)*t; s += 2*((ph/(2*np.pi)) % 1) - 1  # saw
    s = lp(s, 1600) / (2*len(freqs))
    a = np.minimum(t/0.8, 1) * np.minimum((d - t)/1.5, 1).clip(0, 1)
    return s * a * g

# ---------- arrangement ----------
BPM = 120; beat = 60/BPM
# drone under problems (0 -> silence)
dr_d = C["silence"]; t = t_arr(dr_d)
drone = (np.sin(2*np.pi*55*t) + 0.5*np.sin(2*np.pi*82.4*t) + 0.25*lp(rng.standard_normal(len(t)), 300))
drone *= np.minimum(t/1.5, 1) * 0.22
add(drone, 0, 1)
for k in range(int(C["burst"]/ (beat/2))): add(tick(3200, 0.06), k*beat/2, 1, (-1)**k*0.5)  # HUD ticks
add(riser(1.4), C["burst"]-1.4, 0.8); add(impact(), C["burst"], 0.9); add(whoosh(0.8), C["burst"], 0.7)
# problems: kicks + specific SFX
add(beep(), C["p1"]+0.02, 0.9)
for i in range(3): add(notif(), C["p2"]+0.12*i, 0.9, [-.5, 0, .5][i])
add(counter(), C["p3"], 0.9)
add(buzz(), C["p4"], 0.9)
for k, p in enumerate(["p1", "p2", "p3", "p4"]):
    add(kick(1.0), C[p], 0.95)
    for j in range(1, 4): add(kick(0.55), C[p] + j*beat/2, 0.6)  # pulse quickens feeling
# converge riser -> silence -> logo
add(riser(C["silence"]-C["converge"]+0.1), C["converge"], 1.0)
add(impact(), C["logo"], 1.15); add(whoosh(1.0, False), C["logo"], 0.6)
# main groove from promise to final
g0, g1 = C["promise"]-beat*2, C["final"]
bass_notes = [55, 55, 65.4, 49]  # A A C G
k = 0; tt = g0
while tt < g1 - 0.01:
    bar = int((tt-g0)/(beat*4)) % 4
    if k % 2 == 0: add(kick(0.9), tt, 0.85)
    if k % 4 == 2: add(snare(), tt, 0.7)
    add(hat(), tt + beat/2, 1, 0.3); add(hat(0.05), tt, 1, -0.3)
    # bass (8th pulses)
    for h in (0, beat/2):
        bt = t_arr(beat/2*0.9); f = bass_notes[bar]
        b = np.tanh(np.sin(2*np.pi*f*bt)*2 + 0.4*np.sin(2*np.pi*f*2*bt)) * env(len(bt), .003, .12) * 0.32
        add(lp(b, 900), tt + h, 1)
    # arp
    arp = [440, 523.3, 659.3, 880][(k) % 4] * (1 if bar != 2 else 1.189)
    at = t_arr(0.12); add(np.sin(2*np.pi*arp*at)*env(len(at), .002, .05)*0.07, tt + beat/4, 1, 0.4*((-1)**k))
    k += 1; tt += beat
# pads per 4 bars
pads = [[220, 261.6, 329.6], [196, 246.9, 293.7], [174.6, 220, 261.6], [196, 246.9, 329.6]]
for i, tt in enumerate(np.arange(g0, g1, beat*8)):
    add(chord_pad(pads[i % 4], min(beat*8+1, g1-tt+1.5)), tt, 0.9, (-.2, .2)[i % 2])
# UI transitions: whoosh + hit
for key in ["ui_endpoint", "ui_cli", "ui_claude", "ui_providers", "ui_combo", "ui_console", "ui_key", "ui_usage", "ui_pause", "routing"]:
    add(whoosh(0.45), C[key]-0.3, 0.55, 0.3); add(kick(0.7), C[key], 0.5); add(tick(1500, 0.2), C[key]+0.02, 0.8)
for key in ["ui_endpoint", "ui_providers", "ui_key"]: add(impact(), C[key], 0.45)
# routing break
add(glitch(), C["reroute"]-0.25, 0.9); add(impact(), C["reroute"], 0.6)
add(chord_pad([523.3, 659.3, 784], 1.2, 0.2), C["reroute"], 0.6)
# console scroll ticks
for j in range(16): add(tick(2600+(j % 3)*200, 0.08), C["ui_console"]+0.2+j*0.09, 1, 0.4)
# usage counter
add(counter(), C["ui_usage"]+0.4, 0.6)
# reasons: rising chord ticks
for j, key in enumerate(["r1", "r2", "r3", "r4"]):
    f = [523.3, 659.3, 784, 1046.5][j]; tt2 = t_arr(0.5)
    add(np.sin(2*np.pi*f*tt2)*env(len(tt2), .002, .25)*0.25, C[key], 1, [-.4, -.1, .1, .4][j])
# always on: build + snare roll
add(riser(C["final"]-C["always"]), C["always"], 0.8)
nroll = int((C["final"]-C["always"]) / (beat/4))
for j in range(nroll): add(snare(0.12 + 0.3*j/nroll), C["always"] + j*beat/4, 0.8)
# finale
add(impact(), C["final"], 1.2); add(whoosh(1.2, False), C["final"], 0.6)
add(chord_pad([110, 220, 277.2, 329.6, 440], DUR-C["final"], 0.45), C["final"], 1.0)
for key in ["lockup", "tag1", "tag2", "cta"]: add(tick(1760, 0.18), C[key], 0.9); add(whoosh(0.35), C[key]-0.2, 0.25)
add(LS.ding(0.25), C["cta"], 1)
add(LS.rumble(1.6, 0.5), C["converge"], 0.8)

# simple stereo reverb (multi-tap feedback-free)
for d, g in [(0.031, .22), (0.047, .18), (0.071, .14), (0.113, .1), (0.167, .07)]:
    s = int(d*SR); L[s:] += R[:-s]*g; R[s:] += L[:-s]*g*0.9
mx = np.max(np.abs([L, R])); L /= mx/1.6; R /= mx/1.6
L = LS.limit(L, .9); R = LS.limit(R, .9)
out = (np.stack([L, R], 1) * 32767).astype(np.int16)
os.makedirs(os.path.join(HERE, "..", "audio"), exist_ok=True)
with wave.open(os.path.join(HERE, "..", "audio", "music_sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("ok", DUR)
