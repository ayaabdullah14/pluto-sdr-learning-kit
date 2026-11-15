"""Software execution test of the RX power-measurement chain (no Pluto, no GUI).
Real GNU Radio blocks, same settings as rx_tone_power.grc:
  Frequency Xlating FIR Filter (decim 20, low_pass 5 kHz / 2 kHz) -> Complex to Mag^2 -> Moving Average (48000) -> Nlog10 (10*log10)
The PlutoSDR Source is replaced by a Signal Source (tone) + Noise Source.  This is a SIMULATION INPUT, not hardware.
Run:  python gnuradio_headless_test.py
"""
import numpy as np
from gnuradio import gr, blocks, analog, filter
from gnuradio.filter import firdes
FS = 960000; DEC = 20; CH = FS // DEC; LEN = CH
TAPS = firdes.low_pass(1, FS, 5e3, 2e3)
SIGMA = 0.02            # total complex noise std per sample at the 960 kS/s input
SECONDS = 6

def run(tone_hz, amp, fc_rx=100000, sigma=SIGMA, seconds=SECONDS, seed=1):
    tb = gr.top_block()
    n = int(FS * seconds)
    src = analog.sig_source_c(FS, analog.GR_COS_WAVE, tone_hz, amp, 0)
    noi = analog.noise_source_c(analog.GR_GAUSSIAN, sigma, seed)      # Amplitude = std dev of the complex noise
    add = blocks.add_cc(); head = blocks.head(gr.sizeof_gr_complex, n)
    xl = filter.freq_xlating_fir_filter_ccc(DEC, TAPS, fc_rx, FS)
    m2 = blocks.complex_to_mag_squared(1); av = blocks.moving_average_ff(LEN, 1.0/LEN, 4000, 1)
    db = blocks.nlog10_ff(10, 1, 0); snk = blocks.vector_sink_f(); lin = blocks.vector_sink_f()
    tb.connect(src, (add, 0)); tb.connect(noi, (add, 1)); tb.connect(add, head, xl, m2, av)
    tb.connect(av, lin); tb.connect(av, db, snk); tb.run()
    d = np.array(snk.data()); l = np.array(lin.data())
    d = d[2*CH:]; l = l[2*CH:]                   # drop the first 2 s (settling of the 1 s average)
    return d.mean(), d.std(), l.mean()

E_h = float(np.sum(np.array(TAPS)**2))           # noise power gain of the filter
Pn_th = SIGMA**2 * E_h
print(f"filter taps: {len(TAPS)}   sum(h^2) = {E_h:.5f}   predicted noise power in channel = sigma^2*sum(h^2) = {Pn_th:.3e}  ({10*np.log10(Pn_th):.2f} dB)")
b, bs, bl = run(100300, 0.0)
print(f"[1] TX OFF baseline (noise only): reading {b:.2f} dB, std {bs:.3f} dB, linear {bl:.3e}")
print("[2] TX power steps (tone at 100.3 kHz, filter centre 100 kHz => 300 Hz offset): 30 dB -> 40 dB -> 30 dB attenuation")
print("    target SNR | amp@30 | read@30 | read@40 | read@30 again | drop 30->40 | predicted drop | restore error")
for snr in (40, 20, 10, 0):
    Ps = Pn_th * 10**(snr/10); a = np.sqrt(Ps)
    r30, s30, _ = run(100300, a); r40, s40, _ = run(100300, a/np.sqrt(10)); r30b, _, _ = run(100300, a, seed=7)
    pred = 10*np.log10((Ps/10 + Pn_th)/(Ps + Pn_th))
    print(f"    {snr:6d} dB | {a:.4f} | {r30:7.2f} | {r40:7.2f} | {r30b:13.2f} | {r40-r30:9.2f} dB | {pred:10.2f} dB | {r30b-r30:+.2f} dB")
print("[3] Reading versus filter centring error (SNR 40 dB signal, tone at 100.3 kHz):")
Ps = Pn_th * 1e4; a = np.sqrt(Ps)
for fc in (100000, 103000, 104500, 107000, 112000):
    r, _, _ = run(100300, a, fc_rx=fc); print(f"    filter centre {fc/1e3:7.1f} kHz (tone offset from centre {(100300-fc)/1e3:+6.1f} kHz): reading {r:7.2f} dB")
print(f"[4] Definition check: tone amplitude a gives P = a^2 -> for a = 0.05: {10*np.log10(0.05**2):.2f} dB")
