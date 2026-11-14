# Example 1 — Understand a signal before using Pluto

## Purpose and project connection

Create a known digital cosine and prove its amplitude, period and frequency using two displays. You will later use the same predictions to identify the robot's beacon. This example uses one laptop and no RF transmission. Its 48 ksample/s rate is a simulation choice, not a proposed Pluto interface rate.

Estimated time: 1.5–2.5 hours. Read this guide while building. Read REPORT.md for the mathematics. Use BUILD_IN_GRC.md for the exact block-by-block recipe.

## Requirements

- One Windows 11 laptop with the already-installed GNU Radio Companion.
- Ordinary blocks: Options, Variable, Signal Source, Throttle, QT GUI Time Sink and QT GUI Frequency Sink.
- No Pluto, antennas, second laptop, Audio Sink or microphone needed.
- Optional reference-script execution needs Python, NumPy and Matplotlib. This is an independent numerical comparison, not a prerequisite for learning GNU Radio.

Target: GNU Radio 3.10.12.0 with Python 3.12.9. Open `flowgraphs/ex01_signal_basics.grc` directly; the complete editable circuit is included. BUILD_IN_GRC.md is an optional manual rebuilding exercise. The file has passed exact-version GRC structure/code-generation checks; actual DSP/GUI execution still needs your installation.

## New concepts

- **Sample:** one stored numerical value of a signal.
- **Sample rate, Fs:** samples representing one second, in samples/s.
- **Float stream:** one real number per sample; our cosine has no imaginary component.
- **Amplitude:** the largest magnitude of this zero-offset cosine, here 0.5 digital units.
- **Period:** time for one complete cycle.
- **Time domain:** signal value against time.
- **Frequency domain:** strength of frequency components against frequency.
- **FFT:** a calculation on a finite group of samples to show frequency content.
- **FFT bin spacing:** frequency interval between neighboring FFT values; not a guarantee that two close tones are resolvable.
- **Window:** weighting applied before the FFT to control leakage. It also broadens peaks and affects their displayed level.
- **Baseband:** the digital frequency axis around zero. No RF carrier exists in this simulation.

## Signal path

Place Signal Source on the left, Throttle in the middle, and the time/frequency displays on the right. Branch only after Throttle. Keep Variable blocks in one row above the path.

| Block | Input | Action | Output | Type and rate |
| --- | --- | --- | --- | --- |
| Signal Source | No stream input; numerical settings | Evaluates a sampled cosine | x[n] | Float, 48,000 samples/s |
| Throttle | x[n] | Limits simulation throughput; does not resample | The same x[n] | Float, 48,000 samples/s |
| QT GUI Time Sink | x[n] | Displays 192 samples against time | GUI only | Float input, label rate 48,000 samples/s |
| QT GUI Frequency Sink | x[n] | Computes an FFT-based display from 4,096 samples | GUI only | Float input, bandwidth label 48,000 Hz |

The sink's sample-rate/bandwidth setting labels the axis; changing it does not change the actual samples. Throttle limits average wall-clock throughput. It does not create a precisely clocked acquisition device.

## Configuration

| Parameter | Value | Why | If changed |
| --- | --- | --- | --- |
| samp_rate | 48000 samples/s | Easy arithmetic; 32 samples/cycle | Update source, Throttle and both display settings together |
| tone_freq | 1500 Hz | Visible cycles; exact FFT bin at N=4096 | Period and spectral peaks move |
| amplitude | 0.5 digital units | Easy fixed vertical scale | Time peaks scale linearly, power quadratically |
| Signal Source Waveform | Cosine | Known equation and initial maximum | Sine changes phase but not tone frequency |
| Signal Source Offset | 0 | Avoid a DC component | A nonzero offset adds a central spectrum component |
| Initial Phase | 0 radians | Predictable first sample | Moves waveform in time, not its frequency |
| Time Sink Number of Points | 192 | Nominal 4 ms frame; six cycles | Changes displayed time interval |
| Time Sink Y Min / Y Max | -0.6 / 0.6 | Keeps amplitude comparisons meaningful | Autoscale can conceal amplitude changes |
| FFT Size | 4096 samples | 11.71875 Hz bin spacing | Larger FFT gives smaller spacing and longer observation |
| Window Type | Rectangular | Exact-bin numerical reference is easy | Other windows broaden peaks; compare levels carefully |
| Frequency Sink Center Frequency | 0 Hz | This is baseband simulation | Only relabels the axis; does not tune hardware |
| Frequency Sink Bandwidth | samp_rate | Correct time-to-frequency interpretation | An incorrect value gives a wrong frequency reading |
| Spectrum Width | Full, if available | Show both positive and negative components | Half view shows nonnegative frequencies only |

## Build and run

1. Open GNU Radio Companion and start a new QT GUI flowgraph.
2. Follow BUILD_IN_GRC.md. Use the listed block IDs so you can discuss them clearly.
3. Check every stream port is Float. Do not use a complex output by accident.
4. Connect source to Throttle. Branch its output to both sinks.
5. Save your copy of `ex01_signal_basics.grc`. Use the toolbar's Generate and Execute actions. Record an error exactly if either action fails.
6. Find two peaks in a Full spectrum, or one positive-frequency peak in a Half spectrum. Read frequency from the horizontal axis.
7. On the time plot, use two neighboring maxima to measure one period. If the display drifts, use its trigger controls to stabilize a positive-going zero crossing; exact trigger controls vary by version.
8. Stop the flowgraph before editing variables. Change one variable, predict, restart and record.

No TX/RX laptop sequence applies here. Later hardware examples will start RX first, record TX-off data, and then enable TX.

## Expected results and verification

| Quantity | Prediction | Practical check |
| --- | --- | --- |
| Positive / negative extrema | +0.5 / -0.5 | Read fixed-scale time plot; use about ±0.02 reading tolerance |
| Period | 0.666667 ms | Neighboring peaks; cursor tolerance about one sample = 0.020833 ms |
| Samples/cycle | 32 | Confirm with samples or period × sample rate |
| Time frame | 192/Fs = 4 ms nominal | Six cycles; last sample is at 191/Fs = 3.979167 ms |
| Spectrum | Peaks at ±1500 Hz in Full view | Peak position within one FFT bin of prediction |
| FFT bin spacing | 11.71875 Hz | Calculate from actual FFT size and rate |
| Mean-square power | 0.125 digital units squared | Verified by the optional numerical script, not by eyeballing FFT height |

Success requires period and spectrum to agree, plus a deliberate change that produces the predicted response. A plausible waveform alone is insufficient.

The provided PNG is a **NumPy reference simulation**, not a GNU Radio screenshot or a hardware measurement. Its vertical spectrum axis is explicitly a normalized two-sided DFT magnitude. GNU Radio's GUI uses its own spectral scaling; compare frequencies directly, not absolute heights across these two displays.

## Guided experiments: predict, observe, explain

1. Change tone_freq from 1500 to 3000 Hz. Predict period 0.333333 ms, 16 samples/cycle, and peaks at ±3000 Hz. Restore 1500 Hz.
2. Change amplitude from 0.5 to 0.25. Predict unchanged frequency/period, half-height time peaks and one-quarter mean-square power (−6.0206 dB). Keep the time Y axis fixed. Restore 0.5.
3. Change FFT Size from 4096 to 1024. Predict bin spacing 46.875 Hz and a shorter 21.3333 ms FFT record. Frequency remains 1500 Hz.
4. Set tone_freq to 1510 Hz with N=4096 and Rectangular window. Predict energy spread across bins because the record contains a noninteger number of cycles. Try Hann or Blackman-harris and explain narrower leakage tails versus a broader main lobe. Do not compare absolute peak levels without understanding normalization.
5. Restore baseline, then deliberately change **only** Frequency Sink Bandwidth to 96000. Predict an apparent ±3000 Hz label while the time plot remains 1500 Hz. This is a display error. Restore it to samp_rate.
6. Optional aliasing experiment: set the source tone to 30000 Hz, keeping all rates at 48000. Predict a sampled real tone at 18000 Hz. A source frequency above Nyquist is not uniquely represented. Restore baseline before moving on.

## Troubleshooting

| Symptom | Possible cause | Check | Correction |
| --- | --- | --- | --- |
| Ports cannot connect | Complex/Float mismatch | Open source and sinks; inspect Type/Output Type | Select Float throughout |
| Unexpected frequency | Source frequency or display bandwidth wrong | Read both values, then measure the time period | Restore 1500 and 48000 respectively |
| Unexpected time interval | Time Sink sample-rate setting wrong | Compare with samp_rate variable | Use samp_rate |
| Peaks look wide | Window broadening, off-bin tone or short FFT | Restore 1500 Hz, 4096 and Rectangular | Compare baseline before other windows |
| Only one peak visible | Half spectrum selected | Check Spectrum Width / x-axis | Use Full, or interpret Half correctly |
| Flat line or hidden peaks | Wrong scale, offset or amplitude | Inspect amplitude and Y limits | Set 0.5, offset 0 and limits ±0.6 |
| High CPU use | Throttle missing or disconnected | Trace the source-to-display path | Put one Throttle before the branch |
| Generate fails | Missing block or local version difference | Read the first GRC error; inspect Help → About | Record exact version and unavailable parameter; do not guess replacements |

## Understanding check — try before reading answers

1. Why is 48000 samples/s not the frequency of our cosine?
2. What is the difference between changing tone_freq and changing only a sink's bandwidth label?
3. Why can a real cosine have peaks at both positive and negative frequency?
4. Does Throttle resample the signal?
5. If amplitude halves, what happens to mean-square power?
6. Is a peak marked −20 dB on a GUI automatically −20 dBm?
7. Why does increasing FFT size not automatically guarantee separation of two tones?
8. What evidence would be missing if you submitted only the time plot?

## Answers

1. Sample rate counts numerical samples per second. Tone frequency counts waveform cycles per second. Here each cycle has 32 samples.
2. tone_freq changes generated samples. The sink setting only changes its interpretation/axis labels.
3. A real cosine is the sum of two oppositely rotating complex exponentials. They represent one real tone, not two separate transmitters.
4. No. It limits throughput without changing values or sample count.
5. Power becomes one quarter, a change of −6.0206 dB.
6. No. dBm needs a valid absolute calibration/reference. These are digital sample/display quantities.
7. Window main-lobe width, relative tone strengths, noise and observation duration all matter. Smaller bin spacing is only part of resolution.
8. A measured frequency-domain peak and a controlled parameter-change check, among other verification evidence.

## Completion criteria

Move on when you can rebuild the four processing/display blocks, explain their stream types, predict and measure the baseline, correctly perform experiments 1–5, and explain why the simulation has no RF center frequency or calibrated dBm measurement.

## Your results worksheet

Fill this with your GNU Radio observations. All reference numbers elsewhere are predictions or numerical simulation.

| Run | Fs | Tone | Amplitude | FFT size/window | Measured period | Measured peak frequency | Observed extrema | Explanation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline | 48000 | 1500 | 0.5 | 4096 / Rectangular | ___ | ___ | ___ | ___ |
| Frequency change | 48000 | 3000 | 0.5 | 4096 / Rectangular | ___ | ___ | ___ | ___ |
| Amplitude change | 48000 | 1500 | 0.25 | 4096 / Rectangular | ___ | ___ | ___ | ___ |
| Short FFT | 48000 | 1500 | 0.5 | 1024 / Rectangular | ___ | ___ | ___ | ___ |
| Off-bin | 48000 | 1510 | 0.5 | 4096 / Rectangular | ___ | ___ | ___ | ___ |
| Wrong display bandwidth | 48000 | 1500 | 0.5 | 4096 / Rectangular | ___ | ___ | ___ | Explain intentional axis error |
