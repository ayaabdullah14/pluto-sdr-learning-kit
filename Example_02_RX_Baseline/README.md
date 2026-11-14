# Example 2 — Receiver observation before transmission

## Purpose and project connection

Observe what the receiver shows when your intended transmitter is OFF. Learn to test a visible peak instead of assuming it belongs to the robot. This directly supports the robot-beacon measurement chain; it does not by itself estimate robot coordinates.

## Requirements and prerequisites

Complete Example 1 and verify that each Pluto is recognized. Only laptop B and its RX Pluto are needed for the first observations. Leave the other transmitter stopped.

## Hardware setup and operating rules

This example targets **GNU Radio 3.10.12.0 / Python 3.12.9**, using the native **PlutoSDR Source / PlutoSDR Sink** blocks from `gnuradio.iio`, not Soapy substitutes. Laptop A has the transmitting Pluto, connected to its **TX** port. Laptop B has the receiving Pluto, connected to its **RX** port. Each laptop sees its own radio; they do not need to share one USB address.

1. Unzip the complete package. Keep each example's folders together.
2. Open the relevant `.grc` file using **File → Open** in GNU Radio Companion. The file in `flowgraphs/` is the editable circuit. Do not open `REPORT.md` as a circuit.
3. Identify the radio on each laptop. In the same terminal/environment used for GNU Radio, run `iio_info -s`. The default `device_uri` is `'ip:192.168.2.1'`. If that does not reach your device, replace it with the exact discovered URI, quoted as a Python string, for example `'usb:1.2.3'` only if that is the URI actually reported. Do not copy an example USB address blindly.
4. The numeric LO default is **2450000000 Hz**, solely a design reference for a supervisor-approved conducted/shielded setup. It is not a statement that transmitting there is authorized. For over-the-air tests use the frequency and operating conditions approved for your lab and location. Put the same approved `rf_center` on TX and RX. Do not directly cable TX into RX without a suitable approved attenuation arrangement; obtain the arrangement from your lab's hardware limits.
5. TX starts at **60 dB attenuation** and digital tone amplitude **0.2**. RX starts in **Manual** gain mode at **20 dB**. These are conservative starting settings, not guaranteed received levels. If the signal is too weak, diagnose URI/frequency/TX state first, then adjust one gain/attenuation setting while recording it. Stop if clipping, broad unwanted products or saturation appears.
6. Leave `samp_rate = 2400000`, Buffer size `32768`, Cyclic `False` on TX, and Filter Configuration `Off` for these supplied graphs. TX requests RF bandwidth 1 MHz; the upstream 3.10.12 RX Source implementation uses its internal 20 MHz default in this mode (see COMPATIBILITY.md). The receiver's **digital captured span is still 2.4 MHz**, and later digital channel filtering is much narrower. Do not claim that the RX UI field independently set an exact analog bandwidth. Hardware readback is still needed to verify actual settings.
7. Run **Generate** and then **Execute**. Record the first error if either fails. Start RX first; observe TX-off; then start TX. Stop TX first when finishing. There is no Throttle in hardware graphs: the radios provide pacing.
8. Two independent Plutos have frequency error. Before narrow-channel examples, use Example 3's full-span RX graph to measure the actual beacon/carrier peak. Set `channel_offset` in the narrow RX graph to that **measured baseband frequency**, not blindly to 100000. Aim for residual offset within about 500 Hz for the audio experiment. Change settings with the graph stopped, regenerate, and rerun.

All RF spectra are labeled in **baseband Hz**, not absolute RF Hz. The reference RF frequency is `rf_center + baseband_frequency`. The selected-channel plot is relative to the selected channel center. RX waveform plots may autoscale to make a weak signal visible; that does not prove its power is unchanged. Power comparisons use explicit measurements with constant gain.

Actual hardware results are blank until you run the test. Synthetic figures in `results/`, when present, are labeled numerical reference simulations. No generated reference image is a GNU Radio screenshot or a Pluto measurement.


## New concepts

**Noise floor** is the background level in the spectrum display. **I/Q** stores a real (I) and imaginary (Q) value for each complex sample. **LO** is the radio tuning reference. **DC** means zero baseband frequency. A peak at zero can be a hardware-related artifact, but its location alone is not proof. **Manual gain** keeps the gain setting under your control.

## Circuit files and signal paths

All block names below correspond to the saved `.grc` files. Variables are grouped above the signal path. Processing runs left to right; monitoring branches appear below or after the relevant stage.

### ex02_rx_baseline.grc

| Block ID | Block / role | Input → output | Rate information |
| --- | --- | --- | --- |
| `radio_rx` | iio_pluto_source: Receive digital I/Q from the local Pluto. | RF / radio device → Complex float32 | samp_rate = 2400000 samples/s |
| `baseline_spectrum` | qtgui_freq_sink_x: Show frequency content with the stated bandwidth/FFT; not calibrated dBm. | complex → GUI | bandwidth samp_rate; FFT 4096 |


The Pluto Source supplies Complex 2.4 Msample/s; the single sink labels that full span.

## Important configuration: value, reason and effect

| Parameter | Value | Reason and effect of changes |
| --- | --- | --- |
| samp_rate | 2400000 samples/s | Sets complex capture span and frequency-axis interpretation; lower it only with a justified hardware/filter plan. |
| rf_center | 2450000000 Hz reference | Tuning reference; retuning shifts external RF signals relative to baseband. |
| rx_gain_db | 20 dB, manual | Provides a repeatable starting condition; changing it affects signal and noise levels. |
| FFT Size | 4096 | Gives 585.9375 Hz bin spacing; increase observation length to examine close features. |
| Frequency Sink | one complex input; Hann; baseband center 0 | Shows the captured span without an unnecessary waveform panel. |

## Step-by-step execution

1. Open `flowgraphs/ex02_rx_baseline.grc` on laptop B. Apply the hardware setup above; do not run TX.
2. Execute RX and wait several seconds for the display to settle. Record the center frequency, gain, sample rate and prominent baseband peaks.
3. Save one screenshot with the settings written alongside it. Record a noise-floor reading as an approximate **GUI spectral level** using a quiet region and unchanged FFT/window settings, not calibrated total noise power.
4. Stop RX, change `rf_center` by +200000 Hz within the approved receive/test conditions, regenerate and run. Track the same feature. A stable external signal should move approximately −200000 Hz in baseband; a receiver-centered artifact may remain near zero. This is evidence, not an infallible classification.
5. Restore the original tuning. Repeat at RX gain 30 dB, then restore 20 dB. Note changes and any signs of overload. Keep every other setting fixed.
6. Restore the baseline before Example 3.

## Expected results

No specific external peaks or noise level can be predicted without measuring your environment. The deterministic predictions are the displayed span of approximately −1.2 to +1.2 MHz, FFT bin spacing 585.9375 Hz, and approximate −200 kHz motion of a stationary external RF feature when RX LO is raised by 200 kHz.

## Verification: evidence to collect

A repeatable TX-off screenshot plus a settings table and controlled retune/gain observations. State which features are confirmed external, possible artifacts, or still unknown. Do not label every visible component as noise or as the robot.

## Guided experiments

Predict each change, run it, observe, and explain the difference from your prediction. Change one variable at a time.

Retune by +200 kHz and predict peak motion first. Next change gain by +10 dB, keeping LO and FFT fixed. Return to baseline between experiments. Do not change frequency and gain together.

## Troubleshooting

| Symptom | Possible cause | How to check | Correction |
| --- | --- | --- | --- |
| No device / context error | URI or driver/environment | Run iio_info -s in the active environment | Use the exact discovered URI and verify the native iio module. |
| Large peak at zero | DC-related artifact or an actual signal at LO | Retune and compare feature motion | Keep the intended beacon off DC; retain uncertainty until tested. |
| Noise changes across runs | Gain, FFT/window, antenna or environment changed | Compare all recorded settings | Fix conditions before comparing levels. |
| Many new wide features | Possible overload or real emissions | Reduce RX gain and observe reversibility | Use a lower gain; do not interpret saturation products as independent transmitters. |

## Understanding check — try before the answers

1. Why observe before TX?
2. Does a central peak prove an external signal?
3. What should happen to a stationary RF signal if RX LO rises by 200 kHz?
4. Why keep FFT size and window fixed during a floor comparison?

## Answers

1. To know which features existed before your signal and establish a baseline.
2. No. Retuning and controlled TX tests are needed.
3. Its baseband frequency decreases by about 200 kHz.
4. They affect the displayed spectral level and spreading of noise.

## Completion criteria

You can set the URI and LO, obtain a repeatable TX-off spectrum, describe I/Q and the captured span, and use retuning to investigate a feature without claiming more than the evidence supports.

## Your results worksheet

These fields are for your observations. Do not copy reference simulations into the measured-results column.

| Run / single changed variable | Prediction | LO / offset / rates | Gain / attenuation / amplitude | Measurement and units | Variability / error | Interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline | ___ | ___ | ___ | ___ | ___ | ___ |
| Controlled change 1 | ___ | ___ | ___ | ___ | ___ | ___ |
| Restored baseline | ___ | ___ | ___ | ___ | ___ | ___ |
| Controlled change 2 | ___ | ___ | ___ | ___ | ___ | ___ |

Keep screenshots only when they demonstrate a specific criterion, with the relevant settings recorded. Read REPORT.md for the engineering explanation and equations.
