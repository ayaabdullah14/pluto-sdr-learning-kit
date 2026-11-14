# Practical assessment — are you ready for the next SDR project stage?

Use your own saved flowgraphs and observations. This checks the SDR foundation, not the complete graduation project. Do not move to localization solely because a spectrum looked convincing.

## Part 1 — explain and predict before running

1. Explain the difference between signal frequency, RF LO, baseband offset, sample rate, analog bandwidth and digital filter cutoff.
2. For a real 1500 Hz cosine sampled at 48000 samples/s, predict its period, samples/cycle and real-spectrum components. Explain what changes if only the frequency display's rate label is wrong.
3. For a complex beacon at +100 kHz and the approved LO, calculate its nominal RF frequency. Explain why a real cosine and a complex tone do not have identical signed-frequency spectra.
4. For AM with Ac = 0.25 and mu = 0.5, calculate envelope extrema and the sideband frequencies for a 1 kHz message. Explain why the received amplitude remains unknown.
5. Trace the audio rates: file, low-pass, interpolation, hardware TX/RX, selection/decimation, envelope and speakers. Explain why a Throttle does not fix a rate mismatch.

## Part 2 — demonstrate a working link

1. Obtain and save a repeatable TX-off baseline, with URI, tuning, rate, gain and FFT settings recorded.
2. Enable TX and prove which received component is yours through at least two on/off transitions and a deliberate +25 kHz offset change.
3. Measure the actual received carrier location. Center the narrow selector using that measurement. Explain the selected-channel plot's new frequency reference.
4. Recover a 1 kHz AM message and then a 2 kHz message; verify both the time period and sideband spacing.
5. Recover the supplied audio tone sequence in the correct order and at the correct pitch. Show a measured period for at least one section.

## Part 3 — diagnose without random changes

Introduce one fault at a time and restore the baseline afterward:

| Fault | Required diagnostic evidence |
| --- | --- |
| Wrong frequency-display bandwidth label | Show the unchanged time-domain period and corrected label; explain that no resampling occurred |
| Incorrect narrow-channel center | Find the actual carrier with the full-span receiver and set the measured center |
| Too much listening gain | Show that audio clipping can change while RF settings remain fixed; restore listening headroom |
| Incompatible baseline gain | Make the CSV summary reject the comparison and explain why |

Do not change three parameters and call the final result a diagnosed fault.

## Part 4 — extract measurements you can defend

1. Save TX-off and stationary TX-on power logs with identical selected-channel settings and manual gain.
2. Check full-window length, sample-index progression, valid rows, timestamps and metadata.
3. Compute the mean in linear power units, then convert it to relative dB. Do not average dB and call it the same calculation.
4. Compare a controlled TX-level change. Explain the ideal prediction and observed deviation, including noise/interference and variability.
5. Repeat at least one stationary condition to measure repeatability. If doing distance experiments, keep antenna orientation and settings fixed and retain nonmonotonic results.

## Readiness criteria

You are ready for the **next SDR project stage** when you can reproduce all four parts, explain your evidence without unexplained copied settings, and clearly state these limits:

- Your power is relative digital channel power, not calibrated dBm or direct distance.
- A manually assigned log label is not a decoded robot identity.
- Host processing timestamps are not synchronized RF sample times.
- One receiver's power does not uniquely determine a 2D position or heading.
- Independent ordinary Plutos do not automatically provide a coherent antenna array for AoA.

## Concrete handoff to localization work

Deliver the final TX/RX `.grc` files, an approved settings sheet, a repeatability report, TX-off/on logs, labeled reference-position runs and a note explaining units and timestamp semantics. Then design the multi-anchor layout, antenna/measurement calibration, identity/association method, robot odometry interface, timing strategy, position model and camera ground-truth alignment. Only after those decisions should an EKF or other fusion method be evaluated against real reference trajectories.
