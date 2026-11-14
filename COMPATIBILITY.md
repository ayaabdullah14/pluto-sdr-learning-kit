# Compatibility and settings that must be understood

Target supplied by Aya: **GNU Radio 3.10.12.0, Python 3.12.9, Windows 11 Pro**. The flowgraphs use the native `gnuradio.iio` Pluto blocks. Generated Python depends on the matching GNU Radio / Qt / IIO installation; installing only ordinary Python is not enough.

## Minimal environment check

Use the same environment/terminal that launches GNU Radio Companion:

```text
gnuradio-config-info -v
iio_info -s
python -c "from gnuradio import iio; print('Native GNU Radio IIO module is available')"
```

The package does not replace a working installation. If `PlutoSDR Source` or `PlutoSDR Sink` is unavailable, or only Soapy variants are available, record that difference and adapt the hardware interface rather than guessing parameter mappings. Run Examples 1, 4A and 6A while resolving hardware support.

## Exact-version source finding: RX bandwidth field

The upstream v3.10.12.0 `iio_pluto_source.block.yml` contains a Bandwidth parameter but does **not** pass it to a receiver `set_bandwidth` call. The corresponding `fmcomms2_source` public API/binding also has no `set_bandwidth` method. Therefore adding such a call would fail at runtime.

In that source implementation, with Filter Configuration `Off`, `update_dependent_params` requests its internal `d_bandwidth` default of 20000000 Hz. The supplied RX graphs keep `rf_bw = 20000000` and Filter `Off` to reflect that implementation, rather than claiming an independently controlled 1 MHz analog RX bandwidth. The TX Sink does expose/set bandwidth; its default here is 1000000 Hz. Actual device/firmware behavior still needs hardware readback. Downstream digital selection is explicitly implemented and independent of this unused UI field.

This affects **analog RX filtering**, not the statement that a 2400000-sample/s complex output represents a signed digital span of approximately ±1.2 MHz. It also does not mean the full analog band is guaranteed to alias unchanged into that output: internal on-chip processing is outside this simplified host model. Strong unwanted signals can still overload the analog path. For refined sensing work, verify actual radio filter configuration instead of relying on a GUI field.

Primary versioned sources:

- https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/grc/iio_pluto_source.block.yml
- https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/include/gnuradio/iio/fmcomms2_source.h
- https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/lib/fmcomms2_source_impl.h
- https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/lib/fmcomms2_source_impl.cc
- https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/python/iio/bindings/fmcomms2_source_python.cc
- https://github.com/gnuradio/gnuradio/blob/v3.10.12.0/gr-iio/grc/iio_pluto_sink.block.yml

## Which TX/RX settings must agree?

| Setting | Requirement for these examples |
| --- | --- |
| RF signal band and receiver tuning | The desired emitted RF band must lie inside the receiver's useful band. Start with identical LO fields; account for actual frequency error. |
| Modulation/demodulation | Must be compatible: the AM receiver expects carrier-plus-envelope AM, not arbitrary modulation. |
| Sample rates | All blocks must use the correct rate for their own stream. This package starts with equal TX/RX nominal 2.4 MHz for clarity. Different hardware rates can work in a correctly redesigned receiver; they are not automatically an error or automatically compatible. |
| Audio rates | The WAV rate, TX resampler, RX decimator and Audio Sink must form the documented chain. A WAV file's time scale is not inferred from a generic Variable block. |
| RF bandwidths | Both useful passbands must contain the desired signal. They may differ; a setting's actual hardware effect must be verified. |
| TX attenuation / RX gain | Need not be equal and do not use the same meaning/sign. Choose sufficient headroom and stable gain for measurements. |
| URI | Each laptop addresses its own attached radio; matching text does not mean the same physical radio. |
| Buffer size | Need not match across radios. It affects buffering/latency and throughput, not desired RF frequency. |
| Cyclic | Disabled for these live streaming transmitters. A cyclic first-buffer replay can defeat an intended changing signal. |

## Rate changes and useful bandwidth

Never change only a display label to perform resampling. Keep every source/observer label consistent with the corresponding actual stream. When decimating, reject unwanted bands before they can alias into the new output. In the 5 kHz/3 kHz translating filter, cutoff is the nominal center of a gradual transition, not a perfect passband edge. A 3 kHz audio message needs small residual frequency error; use about ±500 Hz or better centering as a practical target here.

Independent SDRs and audio devices have independent clocks. This package does not promise sample-synchronized anchors, phase coherence or indefinitely drift-free audio buffering.
