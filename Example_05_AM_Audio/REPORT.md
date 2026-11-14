# Engineering report — Example 5: Transmit and recover an AM audio clip

Evidence status: authored design with calculations and source-based GRC checks. Independent numerical references, where supplied, are simulations. No radio measurement or GNU Radio DSP runtime execution was performed in the authoring environment. Actual result fields remain blank.

## A. Objective

Send a known three-tone audio clip before trying a voice recording. Verify rates and recovered pitch with a predictable test instead of relying only on hearing an arbitrary sound.

## B. What this example adds, and why

TX adds Wav File Source, a 3 kHz audio low-pass and a Float Rational Resampler with interpolation 50. The message is scaled and a constant carrier is added. RX uses the same selection/envelope/DC chain and adds listening gain plus Audio Sink at 48 kHz.

## C. Design rationale

A known audio file is a more controlled first source than a live microphone, whose device configuration and sound-level variability introduce extra uncertainty. The included clip deliberately supplies three measurable pitches and short zero-message intervals. The 3 kHz message low-pass limits the desired AM bandwidth. Interpolation by 50 connects the 48 kHz file to the 2.4 MHz hardware stream without misinterpreting its time scale.

The TX chain multiplies the resampled message by Ac mu and adds Ac, producing Ac[1 + mu m]. The real envelope becomes I+j0 and is shifted to +100 kHz as in Example 4. The receiver preserves that channel, decimates to 48 kHz and performs the established envelope/DC operations. Listening gain is placed at the end so it cannot be confused with radio gain. The GUI stays at two RX panels and one TX reference spectrum. A live microphone, audio compressor and automatic RF gain are deliberately not introduced at this stage.

The design assumes the documented stream rates and data types. The hardware settings are starting values to be verified on your installation; received amplitudes and environmental components are unknown. The native 3.10.12 Source bandwidth behavior is documented in COMPATIBILITY.md. No independent receive-bandwidth control is claimed through an unused GUI field.

## D. Mathematical model and worked predictions

### Rate conversion

$$F_{\rm radio}=F_{\rm audio}\frac{L}{M}=48000\frac{50}{1}=2400000\ \mathrm{samples/s}.$$

Faudio is the WAV sample rate, Fradio is the hardware stream rate, L is integer interpolation and M integer decimation. Rational Resampler implements filtered conversion, rather than changing labels. On RX, channel-filter decimation D = 50 gives 2400000/50 = 48000 samples/s for demodulation and Audio Sink. Every rate refers to its local stream; equal nominal rates on separate devices do not guarantee identical physical clocks.

### Message scaling and envelope headroom

$$e(t)=A_c[1+\mu m(t)],\qquad |m(t)|\leq 0.8.$$

e is in digital units, Ac = 0.25, mu = 0.5 is dimensionless, and m is the dimensionless WAV message after band limitation. The inequality is the intended steady-state message bound; interpolation/filter transients can overshoot slightly. The effective modulation depth for a steady test tone is mu_eff = mu × 0.8 = 0.4. Therefore e_min = 0.25(1−0.4) = 0.15 and e_max = 0.25(1+0.4) = 0.35. Checking peaks after processing is more defensible than assuming a file's original peak is unchanged.

### Bandwidth and recovery predictions

For message components bounded approximately by Bm = 3000 Hz, ordinary double-sideband AM occupies approximately 2Bm = 6000 Hz around its carrier, with transition energy depending on the message filter. Bm is the nominal useful one-sided message bandwidth in Hz, not a guarantee of zero energy beyond an ideal edge. The RX selection filter has nominal cutoff 5000 Hz and transition 3000 Hz. Keep residual carrier offset small, preferably within about 500 Hz, so the useful audio band remains well inside the transition region's lower side. This filter is not an ideal rectangular mask.

Recovered message periods satisfy T = 1/f: for 500, 1000 and 1500 Hz the periods are 2, 1 and 0.666667 ms. These are direct time-plot tests of correct rates.

With a short-term flat channel h and correctly selected AM components,

$$y(t)\approx G_a |h| A_c\mu m(t),$$

where Ga = audio_gain is a dimensionless digital multiplier. Magnitude detection followed by DC removal gives this approximate result after settling; additional filter delay/gain is omitted. The carrier remains when m = 0 because e = Ac. Thus an audio-silent interval is not a TX-off RF baseline.

### TX spectrum monitor

A display-only translating FIR branch centers the known +100 kHz digital carrier and decimates by 50 to 48 ksample/s. It shows the selected AM carrier around 0 Hz and the audio-dependent sidebands either side. The main TX stream remains at 2.4 Msample/s and +100 kHz offset; the monitoring branch does not alter it. The monitor's 4096-point FFT gives 11.71875 Hz bin spacing and uses its actual 48 ksample/s rate to label the axis.

## E. Predicted results

A repeating 7.5 s three-tone sequence with correct pitch order and duration, delayed and attenuated by the chain. With a peak-normalized test message of 0.8 and mu setting 0.5, the envelope is approximately 0.15–0.35 before small filter/resampler transients. Audio silence leaves the AM carrier present, so silence is not equivalent to TX-off.

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

Correct 500/1000/1500 Hz recovered periods plus the expected order and quiet intervals. Compare a TX-off run to rule out unrelated audio. Hearing intelligible speech is a later check, not the only proof of rate correctness. Compare values with their measurement resolution and settings. A changed GUI scale, gain, observation duration or filter is a possible explanation to test; do not automatically blame the radio. Never present the worked examples as your hardware observations.

## G. Limitations and error sources

Audio and SDR clocks are independent, so long-duration buffering can drift. Radio noise, clipping and channel selectivity can distort audio. The file path and output-device configuration are user-specific. This is an audio-file link, not a claimed live microphone or hardware-tested recording.

## H. Skills gained and connection to the next stage

You can trace every rate from WAV to radio and back, recover known pitches, diagnose a path/volume/rate error, and explain why silence is not TX-off.

The rate chain now works with a useful message. Next isolate a wanted signal and quantify what a filter preserves or suppresses.

Primary source references and exact-version source links are in SOURCES.md. Source checks support block/API behavior; the worked mathematics is specific to this course design.
