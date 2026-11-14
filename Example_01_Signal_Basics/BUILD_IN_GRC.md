# Manual construction guide

The ready circuit is `flowgraphs/ex01_signal_basics.grc`, targeting GNU Radio 3.10.12.0. Open it directly to begin. This guide is an optional exercise to rebuild it yourself. Do not silently change stream types or rates.

1. Start a blank flowgraph. In **Options**, use ID `signal_basics`, Title `Example 1 - Signal basics`, Generate Options `QT GUI`, and Python output if offered.
2. Add three **Variable** blocks: `samp_rate` = `48000`; `tone_freq` = `1500`; `amplitude` = `0.5`. Put them above the signal path.
3. Add **Signal Source**, ID `tone`. Choose Output Type `Float`, Sample Rate `samp_rate`, Waveform `Cosine`, Frequency `tone_freq`, Amplitude `amplitude`, Offset `0`, Initial Phase `0` radians. Place it on the left.
4. Add **Throttle**, ID `simulation_clock`. Type `Float`, Sample Rate `samp_rate`, Vector Length `1`. If a Limit setting exists, use its default. Put it to the right of the source.
5. Add **QT GUI Time Sink**, ID `time_view`. Type `Float`, Number of Inputs `1`, Name `Time - 1.5 kHz reference`, Number of Points `192`, Sample Rate `samp_rate`, Update Period `0.1` s, Y Min `-0.6`, Y Max `0.6`, Autoscale `No`. Use a line label `x[n]`. Put it on the upper right.
6. Add **QT GUI Frequency Sink**, ID `spectrum_view`. Type `Float`, Number of Inputs `1`, Name `Baseband spectrum - real cosine`, FFT Size `4096`, Window Type `Rectangular`, Center Frequency `0`, Bandwidth `samp_rate`, Update Period `0.1` s. Choose Spectrum Width `Full` if available. Set averaging off (or average factor `1` where applicable). Start with Y limits `-100` and `10` in the sink's native display units. Do not label them dBm. Put it below the time sink.
7. Set GUI Hint `0,0,1,1` on the Time Sink and `1,0,1,1` on the Frequency Sink if the version supports grid hints. This stacks the displays without extra GUI controls. Otherwise use the default layout and resize for readability.
8. Connect `tone:0` to `simulation_clock:0`. Connect `simulation_clock:0` to each sink's stream input `0`. There are exactly three stream connections. Do not connect message ports.
9. Save as `signal_basics.grc`. Generate and Execute from the toolbar. Record the GNU Radio version next to your result screenshots.

| Stream connection | Type | Sample rate |
| --- | --- | --- |
| tone → simulation_clock | Float | 48000 samples/s |
| simulation_clock → time_view | Float | 48000 samples/s |
| simulation_clock → spectrum_view | Float | 48000 samples/s |

The source and Throttle create the simulation. The sinks observe it. No resampler is needed because the stream rate stays the same everywhere. No Pluto block, Audio Sink or second Throttle belongs in this graph.

For each guided experiment, edit the relevant Variable or sink parameter, then regenerate and run. Restore the baseline before testing a different parameter.
