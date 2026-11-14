# Engineering report — Example 2: Receiver observation before transmission

Evidence status: authored design with calculations and source-based GRC checks. Independent numerical references, where supplied, are simulations. No radio measurement or GNU Radio DSP runtime execution was performed in the authoring environment. Actual result fields remain blank.

## A. Objective

Observe what the receiver shows when your intended transmitter is OFF. Learn to test a visible peak instead of assuming it belongs to the robot.

## B. What this example adds, and why

The hardware replaces Signal Source and Throttle. The input is now complex I/Q samples. New settings are the radio URI, LO, capture rate and manual RX gain. One frequency plot is enough; a time plot of noise adds little to this task.

## C. Design rationale

The first hardware question is what the receiver produces before we add a known signal. A single complex frequency display exposes noise, existing emissions and possible receiver artifacts without distracting panels. A manual gain of 20 dB is a starting point that makes later comparisons interpretable; an automatic gain would change the relation between field strength and digital amplitude. A 2.4 Msample/s capture is modest for USB and above the native block threshold for Filter Off. The 32768-sample buffer represents about 13.653 ms at this rate; it is a buffering interval, not a synchronized measurement timestamp.

No carrier identification algorithm is introduced yet. Retuning is a controlled test: external RF frequency remains approximately fixed while its position relative to the receiver LO changes. Receiver artifacts can behave differently, although artifacts are not guaranteed to stay centered. Gain changes are a second test for overload and repeatability.

The design assumes the documented stream rates and data types. The hardware settings are starting values to be verified on your installation; received amplitudes and environmental components are unknown. The native 3.10.12 Source bandwidth behavior is documented in COMPATIBILITY.md. No independent receive-bandwidth control is claimed through an unused GUI field.

## D. Mathematical model and worked predictions

### Complex baseband and tuning

The receiver describes a narrow RF component with a complex signal

$$z[n]=I[n]+jQ[n]\approx B e^{j(2\pi f_b n/F_s+\phi)}+w[n].$$

Here z, I, Q and B use digital sample units; j is the imaginary unit; n is the integer sample index; Fs = 2400000 samples/s; fb is baseband frequency in Hz; phi is phase in radians; w is the combined noise/error contribution. This ideal single-tone model assumes a sufficiently narrow component and no overload. It explains why the Pluto Source emits one complex stream, not two independent real-time radio channels.

$$f_b=f_{\rm RF}-f_{\rm LO},\qquad \Delta f_b=-\Delta f_{\rm LO}.$$

Both RF and LO frequencies are in Hz. If a component is at 2450100000 Hz and RX LO is 2450000000 Hz, it appears at +100000 Hz. Raising LO to 2450200000 Hz moves it to −100000 Hz. This calculation predicts the retune experiment; the example RF component is hypothetical, not an observed transmission.

### FFT observation

$$\Delta f=F_s/N=2400000/4096=585.9375\ \mathrm{Hz},$$
$$T_{\rm FFT}=N/F_s=1.706667\ \mathrm{ms}.$$

N is FFT Size in samples. Delta f is the bin spacing, not a complete measure of resolving ability. A Hann window broadens a narrow peak. Complex sampling represents a signed frequency interval of width Fs, conventionally −Fs/2 to +Fs/2, hence approximately ±1.2 MHz here. This digital span is different from the analog RF filter setting.

An ideal gain change of G dB multiplies an unchanged signal's amplitude by $10^{G/20}$ and its power by $10^{G/10}$. G = 10 dB gives amplitude factor 3.1623 and power factor 10. This is a first-order check, not an exact prediction of hardware noise or saturation behavior. The Frequency Sink's changing floor must not be interpreted as a calibrated total-power measurement.

## E. Predicted results

No specific external peaks or noise level can be predicted without measuring your environment. The deterministic predictions are the displayed span of approximately −1.2 to +1.2 MHz, FFT bin spacing 585.9375 Hz, and approximate −200 kHz motion of a stationary external RF feature when RX LO is raised by 200 kHz.

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

A repeatable TX-off screenshot plus a settings table and controlled retune/gain observations. State which features are confirmed external, possible artifacts, or still unknown. Do not label every visible component as noise or as the robot. Compare values with their measurement resolution and settings. A changed GUI scale, gain, observation duration or filter is a possible explanation to test; do not automatically blame the radio. Never present the worked examples as your hardware observations.

## G. Limitations and error sources

The environment is unknown, spectra have finite resolution, the radio has frequency error and DC/IQ imperfections, and gain can cause overload. A center-stationary feature is only a candidate artifact. No absolute RF power or distance is measured.

## H. Skills gained and connection to the next stage

You can set the URI and LO, obtain a repeatable TX-off spectrum, describe I/Q and the captured span, and use retuning to investigate a feature without claiming more than the evidence supports.

You now have a receiver baseline. Next add a deliberately controlled tone and prove that the newly observed component follows your transmitter.

Primary source references and exact-version source links are in SOURCES.md. Source checks support block/API behavior; the worked mathematics is specific to this course design.
