# Example 05 Report: AM audio transmission

Check status: sections D and E numbers were calculated or computed with Python (`results/tx_level_check.txt`, `results/audio_stats.txt`). The compare script was tested only on synthetic data. Nothing here was measured on a Pluto. Section F is for your measurements.

## A. Objective
Transmit and recover a real audio signal over a Pluto-to-Pluto AM link, keep the signal inside safe amplitude and bandwidth limits, convert sample rates correctly between the sound card, GNU Radio and the Pluto, and quantify the quality of the recovered audio.

## B. What this example adds (compared with the sine-wave AM link)
| Addition | Why needed |
|---|---|
| Wav File Source (and optional Audio Source) | A realistic, changing message with known content |
| Low Pass Filter 4 kHz before modulation | Fixes the occupied bandwidth at 8 kHz |
| Multiply Const `m` | Message level is now a stored audio level, so modulation depth is set by scaling |
| Rational Resampler (TX Interpolation 20, RX Decimation 1 then 1/2) | Audio rate 48 kS/s must match the 960 kS/s Pluto rate and return to 48 kS/s for the sound card |
| Audio Sink and `volume` | Hear the result |
| File Sink + `compare_audio.py` | Quantitative comparison with the original: delay, shape, frequency, SNR |
| `samp_rate` 960 kS/s, carrier +100 kHz | Integer ratios and lighter CPU than 2.4 MS/s |
New concept: occupied bandwidth, rate conversion, cross-correlation delay measurement.

## C. Design rationale
Requirements: keep the transmit signal narrow (about 8 kHz), below clipping, with exact rate ratios; recover audio the same way as for the sine message.
Assumptions: audio normalized to a peak below 1 (here 0.9); receiver sees only this signal; envelope detection is valid because the carrier is strong (m x peak < 1).
Choices:
- Audio band 4 kHz: enough for speech and the test tones, so occupied bandwidth is 8 kHz.
- 48 kS/s x 20 = 960 kS/s: both integers, so the Rational Resampler is simple and exact. 960 kS/s is also well above the Pluto minimum.
- Carrier at +100 kHz: far from the DC spike and wide enough from the audio sidebands (96 to 104 kHz).
- Channel filter +-15 kHz: wide enough to tolerate carrier offset between two Pluto clocks, narrow enough to reject noise.
- Envelope detection: robust against small frequency and phase differences between the two Plutos, which are not synchronized.
Alternatives and tradeoffs:
| Alternative | Gain | Cost |
|---|---|---|
| Coherent (synchronous) demodulation | Lower noise, can recover without carrier | Needs carrier phase and frequency recovery |
| DSB-SC or SSB | Less power wasted in the carrier | Needs coherent demodulation |
| 2.4 MS/s | Same as earlier labs | Heavier CPU/USB; interpolation 50 |
| Wide audio (8 kHz) | Better sound | Wider signal, more noise |
The design suits the objective: simple, robust, and every block has a predictable effect.

## D. Mathematical model and equations

### D1. AM signal with an audio message
```
s[n] = A_c * ( 1 + m * x_a[n] ) * exp( j*2*pi*f_c*n / f_s ),     |x_a[n]| <= 1
```
Purpose: describes the transmitted complex baseband stream into PlutoSDR Sink.
Symbols: A_c carrier amplitude (0.4, unit-less digital full scale = 1), m modulation depth (0.6), x_a message (audio, peak 0.9), f_c carrier offset (100000 Hz), f_s sample rate (960000 S/s), n sample index.
Assumptions: x_a is already band-limited to 4 kHz and resampled to f_s.
Calculation: envelope minimum = 1 - m*0.904 = 0.458 for m = 0.6 (> 0, so no overmodulation).
Block link: Add Const (1), Multiply Const (`carrier_amp`), Float To Complex, Multiply with the carrier Signal Source.

### D2. Amplitude limit (no clipping)
```
peak = A_c * ( 1 + m * max|x_a| ) <= 1
```
Purpose: keep the Pluto Sink input within digital full scale.
Calculation (computed from the real audio after the filter and resampler, max|x_a| = 0.904): m = 0.3 gives 0.508; m = 0.6 gives 0.617; m = 0.9 gives 0.725; all less than 1.
Meaning: any value of m up to 1 is safe at the Sink. The RX can still clip: that depends on gains.

### D3. Occupied bandwidth
```
B = 2 * W
```
Purpose: how wide the AM signal is.
Symbols: W highest audio frequency (4000 Hz), B bandwidth (Hz).
Derivation: multiplying by the carrier shifts the audio spectrum to both sides of f_c (sidebands at f_c +- f_audio).
Calculation: B = 2 x 4000 = 8000 Hz, from 96 kHz to 104 kHz here.
Block link: TX Low Pass Filter Cutoff Freq; seen on TX tab 3 and RX tab 2.

### D4. Sample-rate conversion
```
f_s,out = f_s,in * L / M        (L interpolation, M decimation)
TX: 48000 * 20 / 1 = 960000
RX: 960000 / 10 = 96000 ;  96000 * 1 / 2 = 48000
```
Purpose: make every block run at a rate its neighbours accept.
Meaning: interpolation adds image copies of the audio spectrum at multiples of 48 kHz, which the resampler's filter removes. Decimation folds spectrum above the new Nyquist (fs/2) onto the wanted band if not filtered first, so the filter comes before the downsampling.
Nyquist check: 96 kS/s -> 48 kS/s has Nyquist 24 kHz; the audio is limited to 4 kHz, so no alias.
Block link: Rational Resampler Interpolation, Decimation; Frequency Xlating FIR Filter Decimation.

### D5. Power split between carrier and sidebands
```
P_carrier = A_c^2 ,   P_sidebands = A_c^2 * m^2 * <x_a^2> ,   share = m^2 <x_a^2> / (1 + m^2 <x_a^2>)
```
Purpose: shows how little power carries information.
Symbols: <x_a^2> mean square of the audio, here 0.302 (from `results/audio_stats.txt`, before the filter; the filtered value is similar).
Calculation: m = 0.3 gives 2.6 percent; m = 0.6 gives 9.8 percent; m = 0.9 gives 19.7 percent (computed).
Meaning: a higher m gives a stronger recovered audio relative to noise, up to m = 1.

### D6. Envelope detection and DC removal
```
|s_bb[n]| = A_c' * ( 1 + m * x_a[n] )     then DC Blocker removes A_c' , leaving A_c' * m * x_a[n]
```
Purpose: recovers the message.
Symbols: s_bb the signal after channel selection (carrier at 0 Hz), A_c' the carrier amplitude as received.
Assumptions: 1 + m x_a > 0 and the channel filter passes carrier and sidebands.
Meaning: magnitude removes the dependence on carrier phase and small frequency offset (Pluto clocks differ), so no synchronization is needed. The recovered level is A_c' * m * x_a, which depends on RF gains, so only relative level and shape are compared.
Block link: Complex to Mag, DC Blocker, Low Pass Filter.

### D7. Frequency offset and the channel filter
```
f_offset = f_carrier,measured - f_c ,    must satisfy |f_offset| < 15 kHz - 4 kHz
```
Purpose: ensure the carrier and sidebands stay inside the Xlating filter.
Meaning: with the carrier within the filter, envelope detection works. The slider `fc_rx` re-centres the filter on the real carrier.
Typical size: Pluto crystals differ by ppm; each 1 ppm at 2.45 GHz is 2.45 kHz, so a few ppm can already give tens of kHz.

### D8. Delay and similarity measurement
```
R[k] = sum_n  rec[n] * orig[n - k]          lag = argmax_k R[k]          delay = lag / f_s
rho = corr( rec, orig shifted by lag )      g = <rec, orig> / <orig, orig>      SNR_res = 10*log10( g^2 P_orig / P_err )
```
Purpose: quantify delay (cross-correlation peak), shape (correlation coefficient rho), gain g and residual error.
Symbols: rec recovered audio, orig original, k lag in samples, P_err = mean of (rec - g*orig_shifted)^2.
Assumption: the recording covers more than one loop of the 10 s file, so delay is known modulo 10 s.
Resolution: one sample = 1/48000 = 20.8 microseconds.
Why not a tone: a pure tone repeats, so many lags have the same correlation; the broadband sweep and melody make the peak unique.
Spectral check: frequency resolution of a 65536-point zero-padded FFT is 48000/65536 = 0.73 Hz (interpolation only); real resolution of a 0.4 s note is about 1/0.4 = 2.5 Hz.
Software check: on synthetic data (known delay 12345 samples, gain 0.37, small noise), the script returned delay 12345, gain 0.3700, rho 0.999, note frequencies 440.2, 554.4, 659.2, 879.6 Hz.

## E. Predicted results
| Quantity | Prediction | Basis |
|---|---|---|
| Occupied bandwidth | 8 kHz, 96 to 104 kHz relative to centre | D3 |
| TX peak amplitude at m = 0.6 | 0.617 | D2 |
| Sideband power share at m = 0.6 | 9.8 percent | D5 |
| Rate points | 48k, 960k, 96k, 48k | D4 |
| Audio note frequencies | 440, 554.4, 659.3, 880 Hz | wav design |
| Recovered amplitude | not predictable | D6 |
| Delay | not predictable; measure it | D8 |

## F. Results and interpretation
Calculated: section E. Expected behavior: recovered audio looks like the original but noisier; low frequencies (below a few tens of Hz) are reduced by the DC Blocker.
Your measurements (empty on purpose):
| Quantity | Measured | Difference from prediction | Explanation |
|---|---|---|---|
| Occupied bandwidth | | | |
| Carrier offset from 100 kHz | | | |
| Note frequencies (rec) | | | |
| Correlation rho | | | |
| Delay (ms) | | | |
| Residual SNR (dB) | | | |
Compare by computing measured minus predicted for each row; explain differences using section G.

## G. Limitations and error sources
- Envelope detection has a noise threshold: at low SNR the demodulated noise rises sharply.
- Sound-card clock and Pluto clock are independent, so over long recordings the audio can drift or glitch (`aU`).
- The DC Blocker slightly reduces very low audio frequencies.
- Interpolation and filters add small amplitude overshoot (peak 0.904 against 0.900).
- Carrier frequency offset between the Plutos; gain changes; clipping; wired vs over-the-air multipath.
- The compare script was tested only on synthetic data; hardware recordings may need a longer capture or a stationary level.
- Amplitude of the recovered audio is arbitrary because gains are not calibrated.

## H. What I should learn
- Predict bandwidth, amplitude limit and rate chain before building.
- Explain why filtering, rate conversion and DC removal are each needed.
- Measure delay, similarity and SNR from a recording instead of judging by ear.
- Next: Example 6 isolates and filters a channel in the presence of other signals; Example 7 studies gain, distance and relative power. Both rely on the spectrum reading and rate bookkeeping learned here.
