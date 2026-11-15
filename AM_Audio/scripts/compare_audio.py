"""Compare recovered audio (raw float32 @ 48 kS/s from the RX File Sink) with the original wav.
Usage:  python compare_audio.py assets/test_audio_48k.wav recovered_audio.f32
Measures: delay (cross-correlation), waveform similarity (correlation coefficient), residual SNR,
          dominant frequency per note (frequency check), best gain.  Needs numpy, scipy (matplotlib optional).
Because the wav loops every 10 s, delay is only known modulo 10 s."""
import sys, wave, numpy as np
from scipy import signal
fs = 48000
def load_wav(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.0
orig = load_wav(sys.argv[1]); rec = np.fromfile(sys.argv[2], dtype=np.float32).astype(float)
L = len(orig)
if len(rec) < 2*L: sys.exit("Recording too short: need at least 20 s (two loops).")
rec = rec[len(rec)//4:]            # skip start-up transient (DC Blocker settling)
rec = rec[:L] - rec[:L].mean()
o = orig - orig.mean()
# circular cross-correlation via FFT: lag where orig, shifted by lag, best matches rec
cc = np.fft.irfft(np.fft.rfft(rec) * np.conj(np.fft.rfft(o)), n=L)
lag = int(np.argmax(cc))           # recovered(n) ~ orig(n - lag)
al = np.roll(o, lag)
rho = np.corrcoef(rec, al)[0, 1]
g = np.dot(rec, al) / np.dot(al, al)
err = rec - g * al
snr = 10*np.log10(np.mean((g*al)**2) / np.mean(err**2))
print(f"delay (mod 10 s): {lag} samples = {lag/fs*1e3:.2f} ms")
print(f"correlation coefficient: {rho:.3f}   (1.000 = identical shape)")
print(f"best gain (recovered/original): {g:.4f}  (arbitrary: depends on RF gains)")
print(f"residual SNR of recovered audio: {snr:.1f} dB")
def dom(x, a, b):
    i0,i1=int(a*fs),int(b*fs); seg = x[i0:i1] * np.hanning(i1-i0); S = np.abs(np.fft.rfft(seg, 1<<16)); return np.argmax(S)*fs/(1<<16)
rec_al = np.roll(rec, -lag)   # recovered shifted back onto the original time axis
print("note check (original vs recovered dominant frequency):")
t0 = 0.3 + 0.01 + 0.3
for i, name in enumerate(["440", "554.4", "659.3", "880"]):
    a, b = t0 + 0.5*i + 0.05, t0 + 0.5*(i+1) - 0.05
    print(f"  note {name:>6} Hz: original {dom(o, a, b):7.1f}  recovered {dom(rec_al, a, b):7.1f}")
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    f, Po = signal.welch(o, fs, nperseg=4096); f, Pr = signal.welch(rec_al/g, fs, nperseg=4096)
    fig, ax = plt.subplots(2, 1, figsize=(8, 6))
    k=int(1.3*fs); ax[0].plot(np.arange(2000)/fs*1e3, o[k:k+2000], label="original"); ax[0].plot(np.arange(2000)/fs*1e3, rec_al[k:k+2000]/g, label="recovered (gain-matched)"); ax[0].set_xlabel("time (ms)"); ax[0].legend()
    ax[1].semilogy(f, Po, label="original"); ax[1].semilogy(f, Pr, label="recovered"); ax[1].set_xlim(0, 6000); ax[1].set_xlabel("frequency (Hz)"); ax[1].legend()
    plt.tight_layout(); plt.savefig("compare_audio.png", dpi=120); print("saved compare_audio.png")
except Exception as e: print("(plot skipped:", e, ")")
