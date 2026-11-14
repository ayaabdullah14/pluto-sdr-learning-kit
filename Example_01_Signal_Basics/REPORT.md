# Engineering report — Example 1: signal simulation

Status: design calculations and independent NumPy simulation. GNU Radio GUI execution and actual hardware measurements have not been performed in this environment. Learner result fields remain blank.

## A. Objective

Build the smallest useful signal experiment: a known cosine, a simulation rate limiter, and time/frequency observers. The engineering problem is to establish that plots and numbers agree before interpreting unknown RF data. The outcome is the ability to predict a signal, construct it, measure it in two domains and diagnose a misleading axis setting.

## B. What this example adds

This is the first example, so there is no previous transmitter or receiver to modify.

| Addition | Why it is necessary |
| --- | --- |
| Three named variables | Make sample rate, tone frequency and amplitude explicit and reusable |
| Signal Source, Float cosine | Create a deterministic reference with a simple mathematical model |
| Throttle | Keep a simulation without clocked hardware from consuming unrestricted CPU time |
| Time Sink | Observe amplitude and period directly |
| Frequency Sink | Independently observe frequency content and learn FFT settings |
| Controlled experiments | Demonstrate cause and effect rather than accepting an attractive plot |

## C. Design rationale

Requirements: a beginner must understand every block, use the existing installation, observe several cycles clearly, and calculate expected results without RF hardware. We assume ideal uniformly spaced samples, a zero-offset real cosine, no channel, no noise and no clipping. These assumptions deliberately isolate display and sampling concepts.

The rate is 48000 samples/s. A 1500 Hz tone then has exactly 32 samples/cycle. Amplitude 0.5 fits easily in fixed ±0.6 display limits. A 4096-sample FFT contains exactly 128 periods, so a Rectangular window gives a clean baseline without off-bin leakage. This is not a recommendation to use Rectangular windows for all real measurements.

A Float stream introduces one value per sample. Complex I/Q will be introduced for the RF link; it is not required to understand this initial real cosine. Both observers connect after one Throttle, so one rate-limited sequence feeds both displays. Hardware-rate control will replace this simulation mechanism in Pluto examples.

Alternatives: a complex source makes positive/negative-frequency direction easier to illustrate but introduces I/Q before it is needed. A sine source has the same spectral frequencies but a different initial phase. A Blackman-harris window reduces leakage away from an off-bin peak but broadens its main lobe. A longer FFT gives more bins and a longer record, with more processing and potentially slower updates. We choose arithmetic and interpretability first.

## D. Mathematical model and equations

### 1. Generate uniformly spaced samples

$$t_n=\frac{n}{F_s},\qquad x[n]=A\cos\left(2\pi f_0\frac{n}{F_s}+\phi\right).$$

Purpose: convert a continuous cosine description into the numerical values emitted by Signal Source. Here n is a dimensionless integer sample index, t_n is time in seconds, Fs = 48000 samples/s, A = 0.5 digital units, f0 = 1500 cycles/s (Hz), and phi = 0 radians. The angle is dimensionless because f0 × n/Fs is a number of cycles.

Substitute:

$$x[n]=0.5\cos(2\pi\,1500\,n/48000)=0.5\cos(\pi n/16).$$

Thus x[0] = 0.5, x[8] ≈ 0, x[16] = −0.5, x[24] ≈ 0 and x[32] = 0.5. These points predict one complete cycle on the Time Sink. The assumptions are constant frequency/rate, no offset and exact arithmetic apart from normal floating-point rounding.

### 2. Predict time-domain properties

$$T_s=\frac{1}{F_s},\qquad T_0=\frac{1}{f_0},\qquad N_{\rm cycle}=\frac{F_s}{f_0}.$$

Purpose: relate sample spacing to waveform period. Ts is seconds/sample, T0 is seconds/cycle, and Ncycle is samples/cycle. Substitution gives Ts = 1/48000 s = 20.833333 µs, T0 = 1/1500 s = 0.666667 ms and Ncycle = 32. The Time Sink should show maxima separated by 0.666667 ms.

For a frame of M = 192 samples:

$$T_{\rm frame}=M/F_s=4\ \mathrm{ms}.$$

Tframe is the nominal represented duration. Samples are indexed 0 through M−1, so the final plotted sample time is (M−1)/Fs = 3.979167 ms. The frame corresponds to six periods. This distinction prevents an off-by-one interpretation of a plotted endpoint.

### 3. Explain the two spectral peaks

$$A\cos(\omega n)=\frac{A}{2}e^{j\omega n}+\frac{A}{2}e^{-j\omega n},\qquad \omega=2\pi f_0/F_s.$$

Purpose: explain why one real tone has symmetric spectral components. j is the imaginary unit, omega is radians/sample, n is sample index, and A retains digital units. Each complex component has amplitude A/2 = 0.25. Full-spectrum display therefore shows components at +1500 Hz and −1500 Hz. This is one real cosine; it does not imply two transmitting devices.

The optional reference plot uses the normalized DFT:

$$X[k]=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N},\qquad a[k]=|X[k]|/N.$$

Here N = 4096 is the number of samples in the transform, k is integer frequency-bin index, X[k] is an unnormalized DFT coefficient, and a[k] is a two-sided amplitude coefficient in digital units. For this exact-bin, Rectangular-window tone, a[k] is 0.25 at each of the two tone bins. GNU Radio GUI spectral scaling/window normalization can differ; absolute GUI height is not being equated with this reference coefficient.

### 4. Calculate FFT bin spacing and record duration

$$\Delta f=\frac{F_s}{N},\qquad T_{\rm FFT}=\frac{N}{F_s},\qquad k_0=\frac{f_0N}{F_s}.$$

Purpose: connect FFT Size and sample rate to the frequency grid. Delta f is Hz/bin, TFFT is seconds of data in one transform, and k0 is the positive-frequency bin index before centering. For Fs = 48000 and N = 4096: Delta f = 11.71875 Hz, TFFT = 85.333333 ms and k0 = 128. The negative-frequency component is at unshifted bin N−128 = 3968, or −1500 Hz on a centered axis.

For N = 1024: Delta f = 46.875 Hz and TFFT = 21.333333 ms. The signal itself remains 1500 Hz. Smaller bin spacing does not alone determine two-tone resolution; window main-lobe width, amplitudes and noise matter.

### 5. Quantify digital power and a relative dB change

$$P=\frac{1}{N}\sum_{n=0}^{N-1}x[n]^2=\frac{A^2}{2}.$$

Purpose: measure average squared digital amplitude. P has digital units squared; it is not watts. The right-hand equality assumes the averaging record contains an integer number of periods of this non-DC cosine. To derive it, use cos²(theta) = [1 + cos(2theta)]/2. The doubled-frequency cosine averages to zero over the complete periods, leaving A²/2.

For A = 0.5, P = 0.25/2 = 0.125. For A = 0.25, P = 0.0625/2 = 0.03125.

$$\Delta P_{\rm dB}=10\log_{10}\left(\frac{P_2}{P_1}\right)=10\log_{10}(0.25)=-6.0206\ \mathrm{dB}.$$

Delta PdB is a dimensionless power ratio expressed in dB; P1 is baseline power and P2 is changed power, both using the same digital reference. The amplitude ratio is 0.5, and 20 log10(0.5) gives the same change. No ADC-to-volts or input-impedance calibration exists here, so these values must not be called dBm. The optional numerical script performs this check; the four-block GRC flowgraph does not include a power meter.

### 6. Show why a wrong axis can fool you

$$f_{\rm shown}=f_0\frac{F_{\rm label}}{F_s}.$$

Purpose: predict a mislabeled sink when its configured rate differs from the rate used to generate the samples. Flabel is the display's bandwidth/rate label in samples/s, Fs is the source model's actual samples/s, and fshown is the apparent frequency in Hz. A tone's cycles/sample stays f0/Fs; multiplying it by the wrong label rate gives the wrong Hz value.

With Flabel = 96000 and Fs = 48000, a 1500 Hz tone appears at 3000 Hz on that display. There is no frequency translation; only the frequency labels changed. Keeping a correctly configured time observer provides a cross-check.

### 7. Introduce aliasing with one controlled example

For a real sinusoid, use |f0| < Fs/2 for a unique frequency interpretation within the ordinary Nyquist interval. Here Fs/2 = 24000 Hz. Frequencies separated by an integer multiple of Fs have identical sampled complex phase progression; real cosine also has even symmetry.

For the optional 30000 Hz example:

$$f_{\rm alias}=|30000-48000|=18000\ \mathrm{Hz}.$$

falias is the observed nonnegative alias frequency in Hz. The samples cannot uniquely distinguish this source description from an 18000 Hz real cosine. In later hardware examples, analog anti-alias filtering and appropriate rate conversion matter. This simulation does not model either filter.

## E. Predicted results

| Calculation | Prediction |
| --- | --- |
| Baseline period | 0.666667 ms |
| Baseline extrema | ±0.5 digital units |
| Baseline spectral frequencies | ±1500 Hz, or +1500 Hz in a Half display |
| FFT bin index | ±128 in centered-bin interpretation |
| Reference two-sided coefficient | 0.25 at each tone component |
| Mean-square digital power | 0.125 |
| Half-amplitude mean-square power | 0.03125; −6.0206 dB relative change |
| FFT spacing, N=4096 / N=1024 | 11.71875 / 46.875 Hz |

## F. Results and interpretation

`results/reference_signal.png` is generated from the stated sample equation using NumPy and Matplotlib. `results/numerical_checks.json` contains the numerical checks, and `results/reference_samples.csv` contains the time samples. They are independently calculated simulation results, not measurements from GRC or Pluto.

Use the following evidence categories separately:

| Evidence type | Status / result |
| --- | --- |
| Analytical predictions | Derived above |
| Independent numerical simulation | See generated reference plot and checks |
| GNU Radio execution | Not executed in the authoring environment; learner to fill |
| Hardware test | Not applicable to this simulation; none performed |

| Your measurement | Value | Difference from prediction | Possible explanation |
| --- | --- | --- | --- |
| Time-plot amplitude | ___ | ___ | Cursor precision / autoscale / wrong source amplitude |
| Time-plot period | ___ | ___ | Cursor precision / wrong rate label |
| Spectral peak frequency | ___ | ___ | FFT grid / display label / wrong source frequency |
| Behavior when amplitude halves | ___ | ___ | Fixed versus automatic scale / spectrum normalization |
| Behavior when FFT size changes | ___ | ___ | Window effects / observation duration |

If the time and spectrum disagree, first check the source's rate and both observers' rate labels. If amplitude appears unchanged after halving it, check autoscaling before assuming the source failed. An off-bin peak may not fall exactly on the requested frequency; report the FFT settings alongside the reading.

## G. Limitations and error sources

- This ideal model excludes channel noise, RF oscillators, frequency offset, hardware gain, quantization and multipath.
- A Rectangular-window exact-bin cosine is unusually clean. Real tones may lie between bins and spread energy.
- GUI cursor readings have finite precision and vary with zoom and display settings.
- FFT display level is not automatically tone amplitude, total power, PSD in calibrated units or dBm.
- Throttle is a software pacing device, not a hardware clock or resampler.
- Changing the plot's sample rate cannot repair incorrect samples or perform real sample-rate conversion.
- A numerical simulation passing does not establish that a user-specific GNU Radio installation can run the corresponding GUI flowgraph.

## H. What you should learn

You should be able to generate a known reference, predict its time and frequency behavior, explain stream rate versus signal frequency, calculate FFT spacing, distinguish a real signal change from a display-label error, and use relative digital power correctly. In Example 2 these skills will be used to inspect an RX baseline without guessing which visible peak is the intended signal. In Example 3 complex I/Q and the RF/baseband relationship will be added to identify a deliberately transmitted beacon.

Documentation: GNU Radio's official Signal Source, Throttle, Sample Rate Tutorial and QT GUI Frequency Sink pages are linked in START_HERE.md. The source documentation supports block roles; the equations and numerical predictions here are derived for this particular design.
