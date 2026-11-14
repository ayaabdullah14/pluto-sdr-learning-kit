# Primary sources used

Checked against the official GNU Radio **v3.10.12.0** source snapshot on 14 November 2026. The source snapshot was obtained from the official gnuradio/gnuradio tag. No claim is made that documentation checks are actual hardware tests.

| Topic | Primary reference | Used for |
| --- | --- | --- |
| Exact block definitions | https://github.com/gnuradio/gnuradio/tree/v3.10.12.0 | Parameter IDs, enum values, stream types, native generation templates |
| Signal Source | https://wiki.gnuradio.org/index.php/Signal_Source | Signal-generation concepts |
| Throttle | https://wiki.gnuradio.org/index.php/Throttle | Simulation pacing; no resampling |
| Sample rates | https://wiki.gnuradio.org/index.php?title=Sample_Rate_Tutorial | Stream rate versus hardware pacing |
| Frequency Sink | https://wiki.gnuradio.org/index.php?title=QT_GUI_Frequency_Sink | FFT settings and axis labeling |
| Native Pluto Source | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/grc/iio_pluto_source.block.yml | Exact-version receiver interface |
| Native Pluto Sink | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/grc/iio_pluto_sink.block.yml | Exact-version TX attenuation/bandwidth/filter controls |
| Translating FIR | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-filter/grc/filter_freq_xlating_fir_filter_xxx.block.yml | Translation center, tap type and decimation |
| Low-pass design | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-filter/lib/firdes.cc | Cutoff convention, Hamming-window FIR design and tap count |
| Hamming window | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-fft/lib/window.cc | Window definition and design attenuation constant |
| Rational Resampler | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-filter/grc/filter_rational_resampler_xxx.block.yml | Interpolation/decimation and default tap behavior |
| Embedded Python | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/grc/core/blocks/embedded_python.py | Embedded-source format, constructor inspection and code generation |
| Moving Average | https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-blocks/grc/blocks_moving_average_xx.block.yml | Scale and averaging length |
| Beamforming / AoA | https://developer.analog.com/docs/system-level/solutions/platforms/pluto/pilots/beamforming/index.html | Later-stage multi-channel antenna/calibration considerations |

The reports' worked predictions are calculated for the supplied examples. They are not copied hardware measurements. The bibliography is a way to check definitions and assumptions, not a list of required reading before starting Example 1.
