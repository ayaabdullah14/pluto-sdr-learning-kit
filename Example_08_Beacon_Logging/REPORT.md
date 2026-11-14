# Engineering report — Example 8: Known-beacon measurement and timestamped logging

Evidence status: authored design with calculations and source-based GRC checks. Independent numerical references, where supplied, are simulations. No radio measurement or GNU Radio DSP runtime execution was performed in the authoring environment. Actual result fields remain blank.

## A. Objective

Produce a usable, auditable measurement stream for the next project stage: selected-channel power windows, host timestamps and the settings needed to interpret them.

## B. What this example adds, and why

A documented Embedded Python sink accumulates nonoverlapping 4800-sample windows, discards one second of startup and writes CSV records. The display remains one selected spectrum plus one power number. A separate command-line summary compares records in linear units.

## C. Design rationale

Saved data needs stronger definitions than a live number. This sink groups exactly 4800 retained selected-channel samples per measurement and never averages logarithmic values. It keeps ordered sample indices, nominal stream time, host UTC and monotonic processing time so each time field has an honest interpretation. Startup data is discarded by sample count. The last incomplete window is not written; this prevents pretending that it has the full nominal duration.

The sink opens its file lazily during actual sample processing, so GRC inspecting the block's ports does not create spurious logs. Files are opened exclusively, preserving existing results with a unique suffix if necessary. CSV output is flushed regularly and closed on a normal stop. The logger checks numerical finiteness, but this is not a radio-quality or interference detector. Metadata includes gain and channel settings; experimental geometry and TX state remain the student's recorded responsibility.

The separate summary uses only Python's standard library. It checks that the main measurement settings match before subtracting a baseline, and reports a nonpositive excess honestly. No fabricated hardware CSV is shipped as an actual measurement. A clean-tone beacon is enough to learn extraction but cannot distinguish multiple identical co-channel transmitters without an additional identification design.

The design assumes the documented stream rates and data types. The hardware settings are starting values to be verified on your installation; received amplitudes and environmental components are unknown. The native 3.10.12 Source bandwidth behavior is documented in COMPATIBILITY.md. No independent receive-bandwidth control is claimed through an unused GUI field.

## D. Mathematical model and worked predictions

### Windowed measurement

For retained selected samples z[n], window k begins at n_k = Ns + kL, where Ns = 48000 discarded startup samples and L = 4800 samples/window. The saved estimate is

$$P_k=\frac1L\sum_{r=0}^{L-1}|z[n_k+r]|^2,\qquad T_w=L/F_o=0.1\ \mathrm{s}.$$

Fo = 48000 samples/s is the selected output rate, r is the within-window integer index, k is the window index and Pk has squared digital units. The code converts to complex128 for accumulation, checks finite samples and writes one record per full window. Consecutive window starts differ by L. The first window has sample_start 48000, sample_end_exclusive 52800 and nominal stream_start_s = 1.0. Stream time is counted from this graph's selected-stream start, not a global radio epoch.

$$P_{k,\rm dB}=10\log_{10}(P_k/1).$$

The reference 1 is one squared digital unit. A zero-power finite window has no finite logarithmic value; its linear field is 0, its dB field is blank. A nonfinite sample window is marked invalid. These conventions prevent silent invalid math.

### A run mean and comparable baseline

For M valid equally sized windows,

$$\bar P=\frac1M\sum_{k=0}^{M-1}P_k,\qquad P_{\rm run,dB}=10\log_{10}(\bar P/1).$$

M is the number of valid windows, Pbar is the run mean in linear units and Prun,dB is dB of that mean. This is not the arithmetic mean of the dB column. The summary also reports spread; adjacent radio measurements may be correlated, so that spread alone is not a guaranteed confidence interval.

For a compatible TX-off mean Poff and TX-on mean Pon, excess is Pon−Poff in linear units. A positive result can be logged relative to the same digital reference. A nonpositive result is reported as insufficient positive excess, not as a negative physical signal power. Matching gain, sample rate, channel center and filter settings is necessary; comparable environment and TX-off labeling must also be checked by the operator.

### Timing semantics

The nominal interval between consecutive window starts is L/Fo = 0.1 s. `host_processed_utc` and `host_monotonic_s` are recorded when each window is processed. USB buffering, the scheduler and CPU load can delay or batch these calls. Consequently, timestamp differences are not assumed to equal 0.1 s, nor can two hosts' timestamp strings establish phase coherence or sample synchronization. Future multi-anchor fusion needs a separately designed timing and association strategy.

## E. Predicted results

A CSV with valid 0.1 s measurement windows and settings, approximately ten rows per second after startup under continuous sample flow. Host timestamp spacing may be uneven or repeated because processing is buffered. TX-on should show reproducible excess channel power when the beacon is above the baseline; no absolute numerical received level is predicted.

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

Check sample-index progression, window length, finite validity flags, settings consistency and TX-off/on differences in linear power. Run repeated stationary measurements. The summary script must reject incompatible baseline settings rather than silently comparing them. Compare values with their measurement resolution and settings. A changed GUI scale, gain, observation duration or filter is a possible explanation to test; do not automatically blame the radio. Never present the worked examples as your hardware observations.

## G. Limitations and error sources

The logger does not measure calibrated dBm, decode identity, assess interference, detect all clipping, synchronize anchors or estimate coordinates. Its time is host processing time. A normal stop is required for orderly closing; a crash can lose recent output. Geometry and TX metadata must be maintained separately.

## H. Skills gained and connection to the next stage

You can independently configure a link, identify its beacon, select its channel, collect repeatable fixed-gain records, explain the timestamps and units, and pass the final practical assessment without claiming a localization accuracy.

The SDR foundation is complete when the practical assessment passes. Next specify the multi-anchor layout, measurement calibration, robot odometry interface, timing/association strategy and ground-truth procedure before implementing localization/fusion.

Primary source references and exact-version source links are in SOURCES.md. Source checks support block/API behavior; the worked mathematics is specific to this course design.
