# Engineering report — Example 4: See AM, then transmit and recover a sinusoidal message

Evidence status: authored design with calculations and source-based GRC checks. Independent numerical references, where supplied, are simulations. No radio measurement or GNU Radio DSP runtime execution was performed in the authoring environment. Actual result fields remain blank.

## A. Objective

First understand AM visually, like the supplied illustration. Then transmit the same principle between two Plutos and verify that the recovered message has the correct frequency.

## B. What this example adds, and why

4A adds a slowly drawn real carrier multiplied by a positive envelope. 4B uses a complex offset RF envelope. 4C adds Frequency Xlating FIR Filter, decimation, Complex to Mag and DC Blocker. These stages isolate the AM channel, extract the envelope and remove its constant part.

## C. Design rationale

A physical 2.45 GHz waveform cannot be drawn as a few visible carrier cycles on an ordinary millisecond-scale GUI trace. Even a +100 kHz baseband carrier becomes dense beside a 1 kHz message. Therefore the visual example intentionally uses a 10 kHz real carrier and a 500 Hz message. It teaches envelope geometry using two curves, then the hardware graph introduces realistic complex baseband without pretending that its raw trace must look exactly like a textbook RF drawing.

The ordinary AM design keeps |mu m(t)| ≤ 1 so the envelope does not reverse sign. The hardware envelope maximum is 0.375, comfortably below normalized TX component magnitude 1. The receive filter translates the measured carrier, selects its narrow band, and decimates from 2.4 MHz to 48 kHz. Magnitude removes the complex carrier rotation, then DC Blocker removes the envelope's constant part. Noncoherent magnitude recovery avoids requiring carrier phase synchronization. It still requires that the carrier and sidebands pass through the channel filter.

The design assumes the documented stream rates and data types. The hardware settings are starting values to be verified on your installation; received amplitudes and environmental components are unknown. The native 3.10.12 Source bandwidth behavior is documented in COMPATIBILITY.md. No independent receive-bandwidth control is claimed through an unused GUI field.

## D. Mathematical model and worked predictions

### Real AM and its envelope

$$s(t)=A_c[1+\mu\cos(2\pi f_m t)]\cos(2\pi f_v t).$$

Ac is carrier amplitude in digital units, mu is dimensionless modulation index, fm is message Hz, fv is the visual carrier Hz, and t is seconds. For 4A, Ac = 0.5, mu = 0.5, fm = 500 and fv = 10000. The slowly varying factor is e(t) = Ac[1 + mu cos(2 pi fm t)]. For 0 ≤ mu ≤ 1, e(t) stays nonnegative, making it the positive envelope.

$$E_{\max}=A_c(1+\mu)=0.75,\quad E_{\min}=A_c(1-\mu)=0.25,$$
$$\mu=\frac{E_{\max}-E_{\min}}{E_{\max}+E_{\min}}=0.5.$$

The extrema are envelope values in digital units. The last expression follows by subtracting the first two expressions (2Ac mu) and dividing by their sum (2Ac). It lets you verify the modulation depth from the blue curve. The message period is 1/fm = 2 ms. The 768-sample frame at 192000 samples/s is 4 ms, showing two message periods and about 40 carrier cycles.

### Derive the sidebands

Using cos a cos b = [cos(a+b) + cos(a−b)]/2,

$$s(t)=A_c\cos(2\pi f_vt)+\frac{A_c\mu}{2}\cos(2\pi(f_v+f_m)t)+\frac{A_c\mu}{2}\cos(2\pi(f_v-f_m)t).$$

The carrier real-cosine amplitude is Ac; each real sideband amplitude is Ac mu/2. Their positive frequencies are 10000, 10500 and 9500 Hz. Each sideband/carrier amplitude ratio is mu/2 = 0.25. The corresponding **power** ratio is (mu/2)² = 0.0625, giving 10 log10(0.0625) = −12.0412 dB. Equal filtering and a linear channel are assumed. Exact GUI peak heights vary with FFT-bin alignment and window normalization; measure integrated tone power or use consistent settings before making precise level claims.

### Hardware complex envelope and recovery

$$z_{\rm TX}[n]=A_c[1+\mu\cos(2\pi f_m n/F_s)]e^{j2\pi f_b n/F_s}.$$

Now Ac = 0.25, mu = 0.5, fm = 1000 Hz, fb = 100000 Hz and Fs = 2400000 samples/s. Signal Source produces the real envelope; Float To Complex makes it I+j0; multiplication by the complex offset tone positions it away from DC. The complex spectrum has carrier at 100000 Hz and sidebands at 99000 and 101000 Hz. RF frequencies are these offsets added to the chosen LO. The envelope ranges from 0.125 to 0.375.

After selecting the channel with center fsel, residual frequency is delta = f_peak − fsel. Assuming a flat linear channel over the AM bandwidth and that all components pass the filter:

$$z_{\rm sel}(t)\approx hA_c[1+\mu\cos(2\pi f_mt)]e^{j2\pi\delta t},$$
$$|z_{\rm sel}(t)|\approx |h|A_c[1+\mu\cos(2\pi f_mt)].$$

h is the complex channel multiplier; delta is Hz. Complex to Mag implements the absolute value. DC removal leaves approximately |h|Ac mu cos(2 pi fm t), with filter-dependent delay and gain. Thus the recovered period must be 1 ms, although its amplitude is not known in advance.

$$F_{\rm out}=F_s/D=2400000/50=48000\ \mathrm{samples/s}.$$

D is dimensionless decimation. The translating low-pass filter is specified at the **input** rate Fs. Its nominal cutoff is 5 kHz and transition width 3 kHz; cutoff is not an ideal brick-wall edge. The new Nyquist edge is 24 kHz. Filtering before downsampling prevents unwanted translated components from aliasing into this output band.

### Keep spectral monitoring readable without wrong axes

The 4A time display observes the original 192000-sample/s signal. A separate display-only low-pass with nominal cutoff 14000 Hz, transition width 4000 Hz and decimation 4 produces a 48000-sample/s spectrum stream. The 9.5/10/10.5 kHz components remain inside that stream's ±24 kHz span. Its FFT Size 4096 gives 48000/4096 = 11.71875 Hz spacing. This makes the sideband group easier to inspect without falsely changing a bandwidth label.

For hardware TX, a separate Complex Frequency Xlating FIR Filter centers the known +100000 Hz digital carrier and decimates by 50 to 48000 samples/s only for the local spectrum. That monitor shows the carrier at 0 and sidebands at ±1000 Hz. The stream sent to Pluto still has carrier offset +100000 Hz at 2400000 samples/s. These are two coordinate references for the same design, not a change in emitted carrier.

## E. Predicted results

4A: envelope 0.25–0.75, message 500 Hz, carrier 10 kHz, sidebands 9.5 and 10.5 kHz. 4B: envelope 0.125–0.375; complex carrier 100 kHz, sidebands 99 and 101 kHz. Each sideband is ideally about 12.04 dB below the carrier in power. 4C: recovered 1 kHz message, with unknown channel-dependent amplitude and startup/filter delay.

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

4A must match envelope extrema and sideband positions. The hardware test must pass TX-on/off identification, show the AM sideband spacing, and recover the selected message frequency. Confirm the 1 kHz → 2 kHz controlled change in both the selected spectrum and recovered period. Compare values with their measurement resolution and settings. A changed GUI scale, gain, observation duration or filter is a possible explanation to test; do not automatically blame the radio. Never present the worked examples as your hardware observations.

## G. Limitations and error sources

Envelope detection fails under strong overmodulation or channel distortion. Frequency offset can move components outside the selection filter. Multipath changes amplitude; noise and DC filtering change the recovered waveform. The visual carrier is a teaching model, not the emitted GHz waveform.

## H. Skills gained and connection to the next stage

You can identify message, carrier, envelope and sidebands, calculate mu from extrema, explain each receiver stage, and prove that the recovered frequency follows a controlled message change.

You now understand a full modulation/recovery chain. Replace the sinusoidal message with band-limited audio while preserving the same envelope and rate reasoning.

Primary source references and exact-version source links are in SOURCES.md. Source checks support block/API behavior; the worked mathematics is specific to this course design.
