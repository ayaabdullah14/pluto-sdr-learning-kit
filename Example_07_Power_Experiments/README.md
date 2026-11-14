# Example 7 — Gain, distance and selected-channel power

## Purpose and project connection

Measure repeatable relative digital power and learn why it is not a universal distance meter. Change one condition at a time and keep a proper measurement record. This directly supports the robot-beacon measurement chain; it does not by itself estimate robot coordinates.

## Requirements and prerequisites

Complete channel selection. Use the two-radio arrangement and known fixed TX tone. A distance experiment also needs marked positions and consistent antenna orientation.

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

**Mean-square power** averages |I+jQ|². **dB** compares a positive power to a stated reference. **dBm** references physical milliwatts and requires calibration; it is not used here. **AGC** automatically changes receiver gain, which complicates received-amplitude comparisons. **Multipath** means reflections combine constructively or destructively, so indoor power may rise or fall irregularly with movement.

## Circuit files and signal paths

All block names below correspond to the saved `.grc` files. Variables are grouped above the signal path. Processing runs left to right; monitoring branches appear below or after the relevant stage.

### ex07_rx_power.grc

| Block ID | Block / role | Input → output | Rate information |
| --- | --- | --- | --- |
| `radio_rx` | iio_pluto_source: Receive digital I/Q from the local Pluto. | RF / radio device → Complex float32 | samp_rate = 2400000 samples/s |
| `select_beacon` | freq_xlating_fir_filter_xxx: Translate the measured beacon, filter and decimate by 50. | Complex at 2400000 samples/s → Complex at 48000 samples/s | 2400000 → 48000 samples/s; center channel_offset |
| `selected_spectrum` | qtgui_freq_sink_x: Show frequency content with the stated bandwidth/FFT; not calibrated dBm. | complex → GUI | bandwidth channel_rate; FFT 4096 |
| `instant_power` | blocks_complex_to_mag_squared: Compute I² + Q² without a square root. | Complex at 48000 samples/s → Float at 48000 samples/s | as stated in input/output columns |
| `average_power` | blocks_moving_average_xx: Compute sliding 4800-sample linear power mean using scale 1/4800. | Float at 48000 samples/s → Float at 48000 samples/s | as stated in input/output columns |
| `report_10_per_second` | blocks_keep_one_in_n: Keep every 4800th power report for display. | Float at 48000 samples/s → Float reports at about 10/s | as stated in input/output columns |
| `relative_power_db` | blocks_nlog10_ff: Compute 10 log10(P) relative to one squared digital unit. | positive Float power reports → Float dB reports at about 10/s | as stated in input/output columns |
| `power_display` | qtgui_number_sink: Show relative digital mean-square power in dB. | Float reports → GUI only | as stated in input/output columns |

Rate map: Pluto RX → selecting filter: Complex 2.4 Msample/s. Selecting-filter output and AM magnitude/DC/listening stages where present: 48 ksample/s. The power averaging chain stays at 48 ksample/s until Keep 1 in N, whose reports are about 10/s. The logger reads selected Complex 48 ksample/s directly.

### ex07_tx_beacon.grc

| Block ID | Block / role | Input → output | Rate information |
| --- | --- | --- | --- |
| `beacon` | analog_sig_source_x: Generate the named tone or positive AM envelope. | none → complex | samp_rate; frequency beacon_offset |
| `radio_tx` | iio_pluto_sink: Send the digital I/Q stream through the local Pluto TX. | Complex float32 → RF / radio device | samp_rate = 2400000 samples/s |
| `tx_spectrum` | qtgui_freq_sink_x: Show frequency content with the stated bandwidth/FFT; not calibrated dBm. | complex → GUI | bandwidth samp_rate; FFT 4096 |

Rate map: all envelope/carrier/complex conversion/multiplication streams in this TX circuit use 2.4 Msample/s. In AM TX circuits, tx_monitor translates and decimates a separate display-only branch to 48 ksample/s so the spectrum can show sidebands clearly; the actual RF input remains at 2.4 Msample/s.


Read the exact rate map below each circuit table before changing sample rates. Display settings label a stream; they do not convert its rate.

## Important configuration: value, reason and effect

| Parameter | Value | Reason and effect of changes |
| --- | --- | --- |
| RX gain | Manual, initially 20 dB | Hold fixed during TX-level and distance runs. |
| Selected channel | 5 kHz nominal cutoff / 3 kHz transition / 48 ksample/s output | Keep its taps and center fixed while comparing power; record retuning if needed. |
| Moving Average | Length 4800; Scale 1/4800 | Computes a 100 ms mean of linear magnitude-squared samples. |
| Keep 1 in N | N=4800 | Reports about 10 averaged values/s; it is for display reporting, not RF channel downsampling. |
| Log10 | n=10; k=0 | Displays 10 log10(P) relative to 1 digital amplitude-squared unit. |
| TX tone | amplitude 0.2; attenuation 60 dB | Reference conditions; adjust only the variable under test. |

## Step-by-step execution

1. Open `ex07_tx_beacon.grc` on A and `ex07_rx_power.grc` on B. Center the RX channel using the full-span measurement procedure.
2. Start RX with TX stopped. Wait at least one second. Write down ten power readings, their approximate range, gain and filter settings. This is the same-channel TX-off baseline.
3. Start TX. After settling, write ten more readings without changing gain, filters, antennas or position. Confirm the selected spectral peak also appears.
4. TX-level experiment: stop A, increase tx_atten_db by 10 dB, rerun and record. A stable, strong, linear link should show approximately a 10 dB signal-power decrease. Total channel power may decrease less when the noise floor is significant. Restore the baseline.
5. Digital-level experiment: halve tx_amplitude to 0.1 with attenuation fixed. Predict −6.02 dB signal-power change, record, then restore.
6. RX-gain experiment: keep the link fixed and increase rx_gain_db by 10 dB. Record the change. This demonstrates why digital power from different gain settings cannot be compared blindly. Restore baseline.
7. Distance experiment only under approved over-the-air conditions: mark several positions, keep gain/TX settings/antenna orientation fixed, collect at least ten readings at each point, and repeat a starting point at the end. Record obstacles and antenna height. Do not assume readings must be monotonic.
8. Stop TX then RX. Use Example 8 for automatic windowed logging instead of manual copying.

## Expected results

The number is relative digital selected-channel power, including noise and any in-channel interference. No absolute RX value is predicted. Under a stable linear signal-dominated link, +10 dB TX attenuation should reduce signal power about 10 dB, and halving digital amplitude should reduce it about 6.02 dB. Indoor distance behavior may be nonmonotonic.

## Verification: evidence to collect

Show a consistent TX-off/on power difference and controlled level-change responses, recording settings and variability. For a distance run, repeat points and report spread. A single smooth-looking curve is not evidence of accurate ranging.

## Guided experiments

Predict each change, run it, observe, and explain the difference from your prediction. Change one variable at a time.

Perform the TX attenuation, TX digital amplitude, RX gain and distance experiments separately, restoring baseline between them. Predict the sign and ideal size of each change. Explain deviations using noise floor, gain changes, clipping, drift and multipath rather than forcing a distance formula to fit.

## Troubleshooting

| Symptom | Possible cause | How to check | Correction |
| --- | --- | --- | --- |
| Power stays similar when TX changes | Noise/interference dominates or wrong channel selected | Inspect selected peak and compare TX-off/on at fixed gain | Re-identify/re-center the beacon; do not infer distance from floor readings. |
| Power falls less than expected | Noise adds to total measured power | Compare linear TX-on/off values | Subtract a comparable baseline only in linear units and report uncertainty. |
| Power jumps between runs | Gain/AGC, antennas, environment or frequency changed | Check the settings worksheet | Use manual gain, fixed geometry and repeated points. |
| Number shows −inf | Mean-square input is zero, or invalid data reached display | Check hardware sample flow and selected spectrum | Diagnose the source; do not call −inf a calibrated RF power. |
| Closer position is weaker | Multipath or orientation change | Repeat position and orientation under controlled conditions | Report the nonmonotonic result; do not erase it as an error. |

## Understanding check — try before the answers

1. Why average before Log10?
2. Why manual gain?
3. Is the number an RF dBm measurement?
4. Does doubling indoor distance guarantee a 6 dB reduction?

## Answers

1. We want log of mean linear power; mean of logged values is a different statistic.
2. A fixed gain makes digital amplitude comparisons easier to interpret.
3. No. Its reference is one squared digital unit, not one milliwatt.
4. No. That is an ideal free-space prediction under restrictive assumptions; indoor multipath often violates them.

## Completion criteria

You can calculate and interpret relative power, maintain fixed gain/measurement bandwidth, quantify variability and explain why power alone does not guarantee distance or position.

## Your results worksheet

These fields are for your observations. Do not copy reference simulations into the measured-results column.

| Run / single changed variable | Prediction | LO / offset / rates | Gain / attenuation / amplitude | Measurement and units | Variability / error | Interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline | ___ | ___ | ___ | ___ | ___ | ___ |
| Controlled change 1 | ___ | ___ | ___ | ___ | ___ | ___ |
| Restored baseline | ___ | ___ | ___ | ___ | ___ | ___ |
| Controlled change 2 | ___ | ___ | ___ | ___ | ___ | ___ |

Keep screenshots only when they demonstrate a specific criterion, with the relevant settings recorded. Read REPORT.md for the engineering explanation and equations.
