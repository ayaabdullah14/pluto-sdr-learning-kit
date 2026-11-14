# Engineering report — Example 6: Filtering and selecting the beacon

Evidence status: authored design with calculations and source-based GRC checks. Independent numerical references, where supplied, are simulations. No radio measurement or GNU Radio DSP runtime execution was performed in the authoring environment. Actual result fields remain blank.

## A. Objective

Learn filtering on a controlled two-tone simulation, then select the real beacon with the same translate/filter/decimate reasoning.

## B. What this example adds, and why

6A introduces two complex tones, one Low Pass Filter and a single equal-scale comparison spectrum. The hardware RX reuses Frequency Xlating FIR Filter to select the known beacon and reduce its rate to 48 ksample/s.

## C. Design rationale

A two-tone ideal simulation separates filter behavior from unknown RF conditions. Both streams entering the comparison display remain at 48 ksample/s because decimation is deliberately 1. This avoids the common error of plotting two rates against one nominal axis. The desired +1 kHz tone lies well inside the filter; +10 kHz lies well outside its transition region. Moving only the unwanted tone toward cutoff teaches that a real filter is gradual.

The hardware graph then combines frequency translation, low-pass filtering and decimation. This is needed before power measurement because wideband power may include unrelated signals. The chosen digital cutoff and transition define a repeatable measurement channel, although the effective noise bandwidth is determined by the actual taps, not just the nominal cutoff label. A finer filter rejects more interference but requires tighter frequency tracking, more taps and longer settling.

The design assumes the documented stream rates and data types. The hardware settings are starting values to be verified on your installation; received amplitudes and environmental components are unknown. The native 3.10.12 Source bandwidth behavior is documented in COMPATIBILITY.md. No independent receive-bandwidth control is claimed through an unused GUI field.

## D. Mathematical model and worked predictions

### FIR filtering

$$y[n]=\sum_{k=0}^{K-1}h[k]x[n-k],\qquad H(f)=\sum_{k=0}^{K-1}h[k]e^{-j2\pi fk/F_s}.$$

x and y are complex sample streams in digital units, h[k] are dimensionless real taps, K is the tap count, Fs is samples/s, and H is dimensionless frequency response. Each output is a weighted sum of recent samples. A steady tone at f is multiplied by H(f), so its amplitude changes by |H(f)| and its power by |H(f)|². This predicts preservation at 1 kHz and attenuation at 10 kHz without inventing hardware measurements.

The simulation uses Fs = 48000 Hz, nominal cutoff 3000 Hz, transition width 2000 Hz and a Hamming window. In GNU Radio `firdes.low_pass`, the nominal cutoff is the center of the designed transition, not an ideal brick-wall passband edge. Finite tap length creates a gradual response. For a symmetric linear-phase FIR, delay is approximately (K−1)/(2Fs) seconds. Allow settling before comparing traces.

### Translation and decimation

$$u[n]=x[n]e^{-j2\pi f_{\rm sel}n/F_s},\qquad y[m]=\sum_k h[k]u[mD-k].$$

fsel is the selected input-band center in Hz, D = 50 is integer decimation, n/m are input/output sample indices. This expression describes translation followed by low-pass filtering and keeping every Dth output. Frequency Xlating FIR Filter implements the combined operation efficiently; it need not calculate this literal sequence internally.

For f_peak = fsel, the target moves to 0 Hz. Increasing fsel by 1000 Hz moves that same target to −1000 Hz. Output rate is Fs/D = 2400000/50 = 48000 samples/s, with Nyquist edges ±24000 Hz. The selected low-pass is specified at the input rate of 2.4 MHz, not the output rate.

### Quantify a controlled tone change

For x[n] = 0.2 exp(j2 pi 1000 n/48000) + 0.2 exp(j2 pi 10000 n/48000), the two tones have mean-square powers 0.04 each. Over an integer number of cycles their cross term averages to zero, so total input power is 0.08. An ideal selector keeping only the first tone would give 0.04, a total-power change of 10 log10(0.04/0.08) = −3.0103 dB. The real filter gives finite attenuation and passband ripple, so compute its actual response or measure after settling. This −3 dB total change must not be confused with the desired tone itself losing 3 dB.

## E. Predicted results

Simulation: two equal input tones; after selection the 1 kHz tone is near its previous level and the 10 kHz tone is much lower. Hardware: selected beacon near zero relative frequency, with output rate 48 ksample/s. A +1 kHz selection-center change shifts its displayed frequency about −1 kHz.

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

Show preservation of the desired component and attenuation of the unwanted one with consistent scales and after settling. For hardware, confirm the selected component follows TX-off/on and the predicted center-frequency change. Compare values with their measurement resolution and settings. A changed GUI scale, gain, observation duration or filter is a possible explanation to test; do not automatically blame the radio. Never present the worked examples as your hardware observations.

## G. Limitations and error sources

Finite attenuation, passband ripple, transition shape, group delay, CFO drift and nearby interference remain. Two-tone simulation does not prove that a real environment contains only those components. Selection reduces interference but does not authenticate a beacon.

## H. Skills gained and connection to the next stage

You can explain which tone is preserved and why, use equal-scale comparisons, translate a measured beacon center, trace the decimated rate and state the selected measurement bandwidth.

You now have a defined, selected stream. Use this stream for repeatable relative received-power experiments.

Primary source references and exact-version source links are in SOURCES.md. Source checks support block/API behavior; the worked mathematics is specific to this course design.
