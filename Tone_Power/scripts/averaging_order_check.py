"""Why average in linear units BEFORE converting to dB (numpy; not GNU Radio, not hardware)."""
import numpy as np
rng = np.random.default_rng(0)
z = (rng.standard_normal(1_000_000) + 1j*rng.standard_normal(1_000_000)) / np.sqrt(2)   # complex noise, true power = 1.0
p = np.abs(z)**2
print("true power = 1.0000  -> 0.00 dB")
print(f"mean of linear power, then dB : {10*np.log10(p.mean()):+.3f} dB   (correct)")
print(f"dB of each sample, then mean  : {np.mean(10*np.log10(p)):+.3f} dB   (biased low; theory -2.507 dB for noise)")
tone = 0.1*np.exp(2j*np.pi*0.01*np.arange(1_000_000))
print(f"P = mean(I^2+Q^2) for a complex tone of amplitude 0.1: {np.mean(tone.real**2+tone.imag**2):.5f} (theory 0.01000 = -20 dB)")
