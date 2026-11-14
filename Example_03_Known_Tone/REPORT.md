# Engineering report — Example 3: Known-tone transmission and reception

Evidence status: authored design with calculations and source-based GRC checks. Independent numerical references, where supplied, are simulations. No radio measurement or GNU Radio DSP runtime execution was performed in the authoring environment. Actual result fields remain blank.

## A. Objective

Establish a controlled one-TX/one-RX link. Prove which spectral peak is yours using on/off behavior and a deliberate frequency change.

## B. What this example adds, and why

Laptop A now generates a complex tone at +100 kHz baseband. Laptop B observes the whole capture span. This adds transmitter attenuation, a known reference offset, oscillator-error measurement, and an I/Q waveform.

## C. Design rationale

A single signed-frequency complex tone is the simplest identifiable beacon. The +100 kHz offset separates it from the radio center without approaching the ±1.2 MHz capture edges. Both laptops initially use the same sample rate and LO to reduce configuration ambiguity. Perfectly identical sample rates are not a physical requirement for every possible receiver, but every block must use its own correct rate and the desired RF band must overlap.

TX attenuation and digital amplitude are separate controls. Their effect is predictable only within a linear unsaturated chain. The received I/Q graph is included because it introduces the actual complex samples; the full-span spectrum is retained for signal identification. Exactly two panels are used on RX. A local TX spectrum confirms the digital input to the transmitter but cannot prove the antenna, RF stage or receiver worked.

The design assumes the documented stream rates and data types. The hardware settings are starting values to be verified on your installation; received amplitudes and environmental components are unknown. The native 3.10.12 Source bandwidth behavior is documented in COMPATIBILITY.md. No independent receive-bandwidth control is claimed through an unused GUI field.

## D. Mathematical model and worked predictions

### Signed baseband and RF placement

$$z_{\rm TX}[n]=A e^{j2\pi f_b n/F_s}=A\cos(2\pi f_b n/F_s)+jA\sin(2\pi f_b n/F_s).$$

A = 0.2 digital units, fb = 100000 Hz, Fs = 2400000 samples/s, n is the sample index and j² = −1. Signal Source with Complex output implements this rotating signal. There are Fs/fb = 24 complex samples per cycle, and the magnitude is constant A. Unlike a real cosine, the ideal complex tone has one signed-frequency component.

The corresponding ideal real RF waveform is

$$s(t)=\Re\{z(t)e^{j2\pi f_{\rm LO,TX}t}\},\qquad f_{\rm RF}=f_{\rm LO,TX}+f_b.$$

t is time in seconds; LO and RF frequencies are in Hz. With the reference LO of 2450000000 Hz, RF is 2450100000 Hz. This is a frequency calculation, not a transmit authorization.

### The received carrier

$$z_{\rm RX}(t)\approx hA e^{j[2\pi(f_b+\epsilon)t+\phi]}+w(t).$$

h is the complex channel/gain multiplier, phi is phase in radians, w is additive noise and epsilon is the combined TX/RX tuning error in Hz. The channel is assumed approximately constant over a short observation and linear. Thus f_peak ≈ fb + epsilon, so epsilon_est = f_peak − 100000 Hz. Changing fb by +25000 Hz changes f_peak by about the same amount if the oscillators and channel remain stable.

FFT Size N = 4096 gives Delta f = Fs/N = 585.9375 Hz. A raw peak-bin frequency is quantized to that grid; windowing broadens the feature. Report the grid and avoid presenting an oscillator-error estimate with unsupported precision.

### Complex-tone power and amplitude changes

$$P=\frac1N\sum |z[n]|^2=A^2=0.04.$$

P has digital amplitude-squared units. This equation uses a complex constant-magnitude tone; the factor 1/2 for a real cosine does not apply. Halving A gives P = 0.01 and relative change $10\log_{10}(0.01/0.04)=-6.0206$ dB. At the receiver h and noise alter the numeric result; this is a controlled-change prediction rather than an absolute-power calibration.

## E. Predicted results

TX digital spectrum: one complex component at +100 kHz. RX: near +100 kHz plus unknown offset, channel attenuation and noise. Deliberately increasing TX offset by 25 kHz moves the corresponding received peak about +25 kHz. The absolute received amplitude cannot be calculated without the channel and gain calibration.

Check the equations before using the plots. The supplied configuration values are documented in README.md; stream type/rate maps and the corresponding blocks are included there. In every calculation, Hz denotes cycles/s, samples/s denotes a stream rate, seconds describe duration, and digital units are not calibrated volts or watts.

## F. Results and interpretation

| Evidence category | What is available |
| --- | --- |
| Calculated | Equations and numerical predictions above |
| Expected behavior | Controlled-change predictions above |
| Independent numerical simulation | See labeled reference files if present; no invented RF environment data |
| GRC structure / generation | See VALIDATION.md; generator checks use runtime stand-ins, not actual DSP execution |
| Actual GNU Radio / Pluto measurements | Not performed here; fill the table below |

| Your observation | Predicted / expected | Measured | Difference or uncertainty | Explanation supported by a controlled check |
| --- | --- | --- | --- | --- |
| Baseline | Use Section E | ___ | ___ | ___ |
| Single-variable change | Use README experiment | ___ | ___ | ___ |
| Restored baseline | Should reproduce within variability | ___ | ___ | ___ |

Record at least two TX-off/on transitions and the +25 kHz shift while other settings stay fixed. An identified component should follow both controls. Do not use a visible peak alone as proof. Compare values with their measurement resolution and settings. A changed GUI scale, gain, observation duration or filter is a possible explanation to test; do not automatically blame the radio. Never present the worked examples as your hardware observations.

## G. Limitations and error sources

Oscillator offset and drift, FFT grid, multipath, unequal gains, clipping and noise affect readings. A CW tone has no decoded unique robot ID and by itself provides no range, position or heading.

## H. Skills gained and connection to the next stage

You can run RX before TX, prove reception through two controls, explain I/Q versus RF, and record the carrier offset for a later narrow-channel receiver.

Use the measured carrier location to center the next narrow-channel receiver. Add AM only after the single-tone identification succeeds.

Primary source references and exact-version source links are in SOURCES.md. Source checks support block/API behavior; the worked mathematics is specific to this course design.
