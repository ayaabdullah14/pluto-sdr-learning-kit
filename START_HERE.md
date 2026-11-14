# SDR foundations for Aya's robot-localization project

The robot carries a known RF beacon. Fixed receiving anchors measure that beacon. A later fusion server combines RF measurements and wheel odometry to estimate motion; a camera provides reference measurements. This training develops the SDR measurements feeding that server. It does not implement an EKF or claim a localization accuracy.

## Learning path

Times are estimates of active beginner practice, excluding installation and debugging.

| Example | Purpose | Prerequisites | Skills gained | Project connection | Time |
| --- | --- | --- | --- | --- | --- |
| 1. Signal simulation | Understand samples, waveform, spectrum and predictions | Basic arithmetic | Measure period, peak frequency, amplitude and relative power | Interpret the beacon before using radios | 1.5–2.5 h |
| 2. Receiver before TX | Observe a repeatable RX baseline | Example 1; working Pluto driver | Separate noise, existing transmissions and possible artifacts using controlled tests | Avoid identifying a hardware artifact as the robot | 1–2 h |
| 3. Known-tone link | Send an offset complex tone from laptop A to laptop B | Example 2; approved test setup | Relate RF to baseband; identify the signal by TX on/off and tone changes; measure frequency offset | Establish an identifiable beacon | 1.5–3 h |
| 4. AM tone | Build carrier-plus-sidebands and recover the envelope | Example 3 | Calculate modulation index and expected spectrum; verify recovered message | Understand a complete modulation and recovery chain | 2–3 h |
| 5. AM audio | Transmit a known audio clip, then optionally voice | Example 4 | Match audio/SDR rates, resample, measure recovered tone and listen | Diagnose end-to-end rate and processing problems | 2–4 h |
| 6. Filtering | Select the wanted channel and reject an unwanted test tone | Examples 3–5 | Choose passband/transition band; filter before decimation; compare equal-scale measurements | Restrict beacon measurements to its channel | 1.5–3 h |
| 7. Gain and power | Compare controlled gain, TX attenuation and distance experiments | Example 6 | Average linear power, convert to relative dB, keep manual RX gain and record settings | Build interpretable received-power data; study multipath limitations | 2–4 h |
| 8. Beacon logging | Record a selected beacon measurement with metadata | Examples 6–7 | Log timestamps, settings, channel power and TX-off baseline; handle invalid records | Supply a defensible measurement stream to later localization work | 2–4 h |

Total: approximately 13.5–25.5 active hours. Three days can cover the first link and AM milestones; mastery of the whole path may need more time.

## This delivery
+
+All eight examples are supplied, with **16 ready `.grc` circuits**, a README and REPORT for every example, layout images, a known WAV clip and the measurement logger/summary scripts. Target: **GNU Radio 3.10.12.0 / Python 3.12.9**.
+
+Start by reading **START_AR.md**, then open `Example_01_Signal_Basics/flowgraphs/ex01_signal_basics.grc`. Follow one example at a time. The README is the operating guide; REPORT.md supplies the deeper engineering explanation. The layout PNG beside each circuit is a guide, not a GNU Radio screenshot.
+
+Every application window has **one or two purposeful panels**. Comparison signals share one plot where that helps. AM starts with a deliberately slower visual simulation before the two-radio link. Display-only filtering reduces spectral span by actually changing a monitoring branch's sample rate; it does not falsify frequency-axis labels or alter the main TX stream.
+
+Read COMPATIBILITY.md before hardware execution, especially its exact-version RX bandwidth finding. Read VALIDATION.md for what has and has not been checked. The native Pluto IIO module must be present on your installation. Examples 1, 4A and 6A run without radios.
+
+## What each experiment must prove

1. RX baseline: repeat with the intended transmitter off; inspect response to retuning and gain changes. A central peak alone does not prove an external transmission.
2. Known tone: the peak must follow a deliberate tone-frequency change and the TX on/off sequence.
3. AM: carrier and sideband spacing must match the selected message frequency; the recovered message must match it as well.
4. Audio: verify a known test tone before a speech clip. Hearing sound alone is a weak diagnostic.
5. Filtering: compare signal and unwanted-tone measurements on the same input and scale, allowing for filter delay and transient settling.
6. Power: keep RX gain, TX settings, antennas, orientation, frequency, sample rate and measurement bandwidth fixed during a distance comparison.
7. Logging: store UTC host timestamps and sample counts; distinguish them from synchronized hardware timestamps. Do not use host-clock timestamps as proof of sample synchronization.

## Scope boundaries that affect the proposal

- Two Plutos support one transmitter and one receiving anchor for the first stage. A simultaneous multi-anchor system needs additional receiving hardware or a separately justified architecture.
- Position, heading and trajectory are later estimates. A single power reading does not uniquely determine 2D position. Heading may be inferred from odometry/motion and fusion; a single isotropic beacon does not directly measure heading.
- AoA is optional advanced work requiring coherent multi-channel measurements, antenna geometry and calibration. Independent ordinary receivers cannot be assumed phase coherent.
- Relative digital power is not calibrated dBm. RSSI-to-distance is affected by walls, multipath, antenna orientation and gain; do not promise precise distance from one universal formula.
- AM is an instructional step. A localization beacon does not have to carry AM audio.
- Use only a supervisor-approved conducted/shielded RF arrangement or explicitly authorized over-the-air test conditions. There is no universal legal test frequency. For conducted tests, obtain suitable attenuation from the hardware limits and expected power; do not directly cable TX to RX without an approved attenuation plan.

## Final practical assessment (after Example 8)

| Task | Evidence of independent ability |
| --- | --- |
| Configure a link | List URI, LO, sample rates, analog bandwidths, TX attenuation, RX gain mode and stream types; explain every choice |
| Identify the beacon | Record TX-off/on and a deliberate offset change; match observed frequency changes |
| Explain the plots | Distinguish baseband/RF, time interval/sample rate, FFT bin spacing and window broadening |
| Repair a fault | Diagnose one deliberately introduced frequency, rate or gain error with a controlled test |
| Measure power | State the channel bandwidth, averaging interval and relative reference; maintain constant gain |
| Log usable data | Produce settings-rich records with timestamps, validity flags and a documented baseline |
| State limits | Explain why this does not yet prove accurate position, synchronized anchors or AoA |

Proceed when every row has evidence you can reproduce without unexplained copied settings.

## Sources checked on 14 November 2026

- GNU Radio Signal Source: https://wiki.gnuradio.org/index.php/Signal_Source
- GNU Radio Throttle: https://wiki.gnuradio.org/index.php/Throttle
- GNU Radio Sample Rate Tutorial: https://wiki.gnuradio.org/index.php?title=Sample_Rate_Tutorial
- GNU Radio QT GUI Frequency Sink: https://wiki.gnuradio.org/index.php?title=QT_GUI_Frequency_Sink
- GNU Radio PlutoSDR Source: https://wiki.gnuradio.org/index.php/PlutoSDR_Source
- GNU Radio PlutoSDR Sink: https://wiki.gnuradio.org/index.php?title=PlutoSDR_Sink
- Analog Devices beamforming introduction: https://developer.analog.com/docs/system-level/solutions/platforms/pluto/pilots/beamforming/index.html

Documentation and generator checks verify definitions and file structure. They do not replace local GNU Radio runtime and actual radio tests. See VALIDATION.md for the exact evidence.
