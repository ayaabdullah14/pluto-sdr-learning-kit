# Example 8 — Known-beacon measurement and timestamped logging

## Purpose and project connection

Produce a usable, auditable measurement stream for the next project stage: selected-channel power windows, host timestamps and the settings needed to interpret them. This directly supports the robot-beacon measurement chain; it does not by itself estimate robot coordinates.

## Requirements and prerequisites

Complete Example 7 and understand relative power, fixed gain, carrier centering and TX-off baselines. Python is introduced here because saving structured measurements now serves a concrete purpose.

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

**Timestamp** needs a stated meaning: this log records when the host processed a window, not synchronized radio sample time. **Metadata** records settings needed to interpret a measurement. **Nonoverlapping window** uses each retained sample in one saved power estimate. **Validity flag** distinguishes finite data from invalid numerical values. **run_label** is a manually supplied experiment tag, not a beacon ID decoded from RF.

## Circuit files and signal paths

All block names below correspond to the saved `.grc` files. Variables are grouped above the signal path. Processing runs left to right; monitoring branches appear below or after the relevant stage.

### ex08_rx_logger.grc

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
| `measurement_logger` | epy_block: Accumulate full nonoverlapping power windows with metadata; source code included. | Complex at 48000 samples/s → CSV; no stream output | as stated in input/output columns |

Rate map: Pluto RX → selecting filter: Complex 2.4 Msample/s. Selecting-filter output and AM magnitude/DC/listening stages where present: 48 ksample/s. The power averaging chain stays at 48 ksample/s until Keep 1 in N, whose reports are about 10/s. The logger reads selected Complex 48 ksample/s directly.

### ex08_tx_beacon.grc

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
| Embedded Python input | Complex selected channel at 48000 samples/s | Uses the same stream whose spectrum is visible. |
| window_samples | 4800 | One 100 ms saved measurement; approximately ten rows/s in steady flow. |
| Initial discard | 48000 samples = 1 s | Reduces startup transients; not a guarantee of hardware settling in every setup. |
| run_label | 'tx_off' initially | Change to a descriptive TX-on/location label before the corresponding run. |
| log_file | 'beacon_log.csv' initially | An absolute writable path is clearer on Windows; existing files are preserved with a unique suffix. |
| Logged settings | rate, LO, selected offset, gain/mode, cutoff and transition | Prevent later analysis from mixing incompatible measurement conditions. |

## Step-by-step execution

1. Open `ex08_tx_beacon.grc` on A and `ex08_rx_logger.grc` on B. Apply the fixed-gain setup and measured channel center.
2. On B set `log_file` to a writable absolute path using a quoted Python string, for example `'C:/Users/YOUR_NAME/Desktop/SDR/tx_off.csv'` with your actual path. Forward slashes avoid accidental escape characters. Set `run_label = 'tx_off'`. The embedded code is already included; you do not need to paste it into GRC.
3. Keep TX off, run RX for about 12 seconds, then stop it normally. The first second is discarded. Read the console line beginning **Power log:** for the exact saved path. Closing normally flushes and closes the file.
4. Set a new output path such as `tx_on_stationary.csv` and `run_label = 'tx_on_stationary'`. Start TX, then run the configured RX for about 12 seconds with identical settings. Stop RX normally, then stop TX. A live baseline observation already occurred in the previous step.
5. Open the CSV in a text editor or spreadsheet and inspect the header. Consecutive full windows should have sample_start increasing by 4800 and window_s = 0.1. The first saved window starts at sample 48000, after startup discard. Runtime duration is approximate; scheduler buffering and startup mean the exact row count may vary.
6. In a terminal with Python, run `python summarize_log.py "FULL_PATH/tx_on_stationary.csv" --baseline "FULL_PATH/tx_off.csv"`, using the script in this example's scripts folder. The output reports finite-row count, linear mean power, dB of that mean, spread and an optional baseline comparison.
7. Collect several repeated stationary runs. Only after these are repeatable, create labeled position runs with settings held fixed. Keep a separate note of antennas, orientation, heights, TX attenuation/amplitude, obstacles, anchor ID and reference position; these are not automatically sensed by the logger.
8. Keep the file and report together when handing data to the localization stage. Do not claim that two laptops' matching UTC strings establish synchronized anchors.

## Expected results

A CSV with valid 0.1 s measurement windows and settings, approximately ten rows per second after startup under continuous sample flow. Host timestamp spacing may be uneven or repeated because processing is buffered. TX-on should show reproducible excess channel power when the beacon is above the baseline; no absolute numerical received level is predicted.

## Verification: evidence to collect

Check sample-index progression, window length, finite validity flags, settings consistency and TX-off/on differences in linear power. Run repeated stationary measurements. The summary script must reject incompatible baseline settings rather than silently comparing them.

## Guided experiments

Predict each change, run it, observe, and explain the difference from your prediction. Change one variable at a time.

Halve TX amplitude with every RX setting fixed; compare dB of mean linear power, accounting for baseline. Next repeat a location without changing orientation. Finally intentionally use a different RX gain for a separate baseline and confirm that the summary refuses the incompatible comparison. Keep deliberately mismatched runs labeled.

## Troubleshooting

| Symptom | Possible cause | How to check | Correction |
| --- | --- | --- | --- |
| No CSV visible | Different working directory, path permission or startup not finished | Read Power log: and the console error; use an absolute output path | Use a writable path and run longer than one second. |
| Existing filename changed | The file already existed | Inspect the unique timestamp/ID suffix printed in console | Use the exact printed path; existing files are intentionally preserved. |
| Uneven host timestamp spacing | Buffered processing or host scheduling | Compare sample_start increments and host timestamp meaning | Use sample counts for stream intervals; do not infer synchronized RF timing. |
| Nonfinite/invalid rows | Invalid stream values | Inspect valid column and numeric fields | Exclude invalid rows and investigate upstream data; do not replace them with invented measurements. |
| Baseline comparison rejected | Different gain/rate/filter/center settings | Read the mismatch listed by the script | Collect comparable baseline data or analyze the conditions separately. |

## Understanding check — try before the answers

1. Does host_processed_utc identify the exact acquisition instant?
2. Why keep sample indices as well as wall-clock timestamps?
3. Is run_label a decoded beacon identity?
4. What should happen if TX-on mean is below TX-off mean?
5. Does this logger prove EKF/localization readiness by itself?

## Answers

1. No. It is the host processing timestamp for a buffered window.
2. They show ordered nonoverlapping stream windows and nominal durations independently of host scheduling.
3. No. It is manually assigned experiment metadata.
4. Report no positive excess above that baseline; do not take log of a negative difference.
5. It prepares measurement handling. More anchors, coordinate calibration, synchronization decisions, a sensor model and validation are still needed.

## Completion criteria

You can independently configure a link, identify its beacon, select its channel, collect repeatable fixed-gain records, explain the timestamps and units, and pass the final practical assessment without claiming a localization accuracy.

## Your results worksheet

These fields are for your observations. Do not copy reference simulations into the measured-results column.

| Run / single changed variable | Prediction | LO / offset / rates | Gain / attenuation / amplitude | Measurement and units | Variability / error | Interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline | ___ | ___ | ___ | ___ | ___ | ___ |
| Controlled change 1 | ___ | ___ | ___ | ___ | ___ | ___ |
| Restored baseline | ___ | ___ | ___ | ___ | ___ | ___ |
| Controlled change 2 | ___ | ___ | ___ | ___ | ___ | ___ |

Keep screenshots only when they demonstrate a specific criterion, with the relevant settings recorded. Read REPORT.md for the engineering explanation and equations.
