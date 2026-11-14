# Engineering report — Example 7: Gain, distance and selected-channel power

Evidence status: authored design with calculations and source-based GRC checks. Independent numerical references, where supplied, are simulations. No radio measurement or GNU Radio DSP runtime execution was performed in the authoring environment. Actual result fields remain blank.

## A. Objective

Measure repeatable relative digital power and learn why it is not a universal distance meter. Change one condition at a time and keep a proper measurement record.

## B. What this example adds, and why

RX adds Complex to Mag^2, Moving Average, Keep 1 in N, Log10 and a number display. One selected-channel spectrum plus one power number replaces unnecessary waveform panels. Each display has a different purpose.

## C. Design rationale

The selected complex stream is the proper input to this measurement because its bandwidth is defined and most unrelated bands have been rejected. Complex to Mag^2 produces instantaneous squared magnitude; averaging in linear units estimates mean-square power. Keep 1 in N reduces only the rate of reporting averaged values. Log10 then produces a compact relative scale for the number display.

The 100 ms averaging interval reduces rapid fluctuation while retaining a useful update rate. The moving average is a sliding filter; the display samples it about ten times a second. Startup and scheduler phase are not precise nonoverlapping window boundaries, so Example 8 uses explicit window accumulation for saved measurements. RX gain remains manual. A distance exercise is framed as a characterization of variability, not a promise of ranging accuracy. A clean CW tone also lacks robot identity and cannot distinguish multiple co-channel beacons.

The design assumes the documented stream rates and data types. The hardware settings are starting values to be verified on your installation; received amplitudes and environmental components are unknown. The native 3.10.12 Source bandwidth behavior is documented in COMPATIBILITY.md. No independent receive-bandwidth control is claimed through an unused GUI field.

## D. Mathematical model and worked predictions

### Instantaneous and averaged digital power

$$p[n]=|z[n]|^2=I[n]^2+Q[n]^2,\qquad \bar P[n]=\frac1L\sum_{k=0}^{L-1}p[n-k].$$

z is the selected complex sample, I/Q are digital components, p and Pbar have squared digital units, and L = 4800 is the number of samples averaged. At Fout = 48000 samples/s, Tavg = L/Fout = 0.1 s. Complex to Mag^2 and Moving Average with scale 1/L implement these equations. Keep 1 in N with N = 4800 reports approximately Fout/N = 10 values/s; it does not replace the earlier anti-aliasing channel filter.

$$P_{\rm dB}=10\log_{10}(\bar P/P_{\rm ref}),\qquad P_{\rm ref}=1\ \text{digital unit squared}.$$

PdB is a dimensionless ratio in dB. For an **illustrative ideal selected complex tone** of amplitude 0.2, P = 0.04 and PdB = −13.9794 dB re 1. This is a mathematical example, not the expected received level. Hardware channel gain is unknown.

Average linear power first. In general, $10\log_{10}(\operatorname{mean}P_i)$ is not equal to $\operatorname{mean}(10\log_{10}P_i)$. The first is the desired power-average statistic here; the second averages logarithmic readings.

### Controlled level changes

$$\Delta P_{\rm dB}=10\log_{10}(P_2/P_1)=20\log_{10}(A_2/A_1)$$

for an unchanged linear channel and a signal with amplitude scale A. Halving A gives −6.0206 dB. Increasing TX attenuation by 10 dB ideally multiplies signal power by 0.1. Increasing RX gain by 10 dB ideally multiplies digital signal power by 10 until compression/clipping or other hardware behavior intervenes. These predictions apply to the signal contribution; total channel power also includes noise/interference.

For comparable TX-on/off records, an approximate excess signal power is

$$\widehat P_s=\bar P_{\rm on}-\bar P_{\rm off}.$$

Pon/Poff are **linear** power means with the same gain, filter and environment. Do not subtract dB readings to estimate linear signal power. If the difference is nonpositive or comparable to the baseline uncertainty, report insufficient evidence above baseline rather than applying a logarithm to a nonpositive value.

### Why power is not automatically distance

An ideal free-space far-field model has Pr proportional to d^(−2). It predicts

$$\Delta P_r=-20\log_{10}(d_2/d_1)\ \mathrm{dB}.$$

Pr is physical received power and d1/d2 are distances in the same length unit. Doubling distance would give −6.0206 dB under constant TX power, antenna gains/polarization and unobstructed far-field propagation. Indoors those assumptions often fail.

A common empirical log-distance model is

$$P_{\rm rel}(d)=P_{\rm rel}(d_0)-10n_p\log_{10}(d/d_0)+X.$$

Prel is a consistent relative-dB measurement, d0 is a reference distance, np is an experimentally fitted dimensionless path-loss exponent, and X is an error term in dB. Both the reference and np need data under the intended conditions. Reflections and orientation can make distance nonunique. The formula is an optional later model, not a guaranteed ranging algorithm.

## E. Predicted results

The number is relative digital selected-channel power, including noise and any in-channel interference. No absolute RX value is predicted. Under a stable linear signal-dominated link, +10 dB TX attenuation should reduce signal power about 10 dB, and halving digital amplitude should reduce it about 6.02 dB. Indoor distance behavior may be nonmonotonic.

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

Show a consistent TX-off/on power difference and controlled level-change responses, recording settings and variability. For a distance run, repeat points and report spread. A single smooth-looking curve is not evidence of accurate ranging. Compare values with their measurement resolution and settings. A changed GUI scale, gain, observation duration or filter is a possible explanation to test; do not automatically blame the radio. Never present the worked examples as your hardware observations.

## G. Limitations and error sources

Uncalibrated digital power is not dBm. AGC, gain drift, noise/interference, antenna differences, saturation and multipath affect readings. A single anchor power reading cannot uniquely determine a 2D position. The number display is for observation; it is not a synchronized multi-anchor data logger.

## H. Skills gained and connection to the next stage

You can calculate and interpret relative power, maintain fixed gain/measurement bandwidth, quantify variability and explain why power alone does not guarantee distance or position.

Automate selected-channel windowing and preserve metadata so later localization work can distinguish measurements from configuration changes.

Primary source references and exact-version source links are in SOURCES.md. Source checks support block/API behavior; the worked mathematics is specific to this course design.
