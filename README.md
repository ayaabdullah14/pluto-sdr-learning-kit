# Pluto SDR Learning Kit

GNU Radio learning files for two ADALM-PLUTO devices, organized from the supplied files.

| Experiment | Files and guide |
|---|---|
| AM modulation and demodulation with a sinusoidal message | [AM tone guide](AM_Mod_Demod/pluto/README.md) · [TX](AM_Mod_Demod/pluto/am_tx_pluto.grc) · [RX](AM_Mod_Demod/pluto/am_rx_pluto.grc) |
| AM audio transmission and recovery | [Audio guide](AM_Audio/README.md) · [Report](AM_Audio/REPORT.md) · [TX](AM_Audio/flowgraphs/am_audio_tx_pluto.grc) · [RX](AM_Audio/flowgraphs/am_audio_rx_pluto.grc) |

| Relative digital power measurement with a known tone | [Power measurement guide](Tone_Power/README.md) · [TX](Tone_Power/flowgraphs/tx_tone_atten.grc) · [RX](Tone_Power/flowgraphs/rx_tone_power.grc) |

## Start here

Open the `.grc` files in GNU Radio Companion (target environment: GNU Radio 3.10.12.0 / Python 3.12.9). Generate and run the Python code from Companion after setting the correct device URI on each laptop. The supplied audio RX Python file is also included in `AM_Audio/flowgraphs/`.

The experiments use different sample-rate settings. Follow the guide belonging to the flowgraphs you open.

## Tone power experiment

The eight supplied power-experiment files are in `Tone_Power/`: flowgraphs, generated RX Python, two standalone checks, their supplied output logs, and the Arabic guide.

- Hardware: configure `pluto_uri` in each flowgraph, start RX first, record the TX-OFF baseline, then start TX. Compare attenuation 30 → 40 → 30 while keeping RX gain and the antenna positions fixed.
- Generate `tx_tone_atten.py` from its GRC file; that Python file was not supplied. Regenerate RX after changing its GRC settings too. Run either GRC Execute or the generated Python for each radio, one instance at a time.
- Standalone checks, from the `Tone_Power` directory in the GNU Radio environment:

```sh
python scripts/averaging_order_check.py
python scripts/gnuradio_headless_test.py
```

The first check requires NumPy. The second also requires GNU Radio but no Pluto or GUI. Files in `results/` are the supplied software-test outputs, not hardware measurements. Power is relative digital dB, not calibrated dBm. The eight added source files were preserved unchanged; Python syntax and GRC YAML parsing were checked during this upload. No new radio or GUI test was performed during the upload.

## Generate the audio file

The WAV file was not supplied. From the `AM_Audio` directory, with NumPy installed, run:

```sh
mkdir assets
python scripts/make_test_audio.py
```

This creates `assets/test_audio_48k.wav`. In the audio TX flowgraph, set `wav_path` to this file's absolute path, or copy the WAV into `flowgraphs/` and select it there. For analysis, install SciPy too (Matplotlib is optional), then run from `AM_Audio`:

```sh
python scripts/compare_audio.py assets/test_audio_48k.wav recovered_audio.f32
```

Set the RX recording path to the intended file location before recording.

## Initial AM material and validation

All ten initially supplied AM files are preserved without content changes; download suffixes were removed from the tone filenames and the two README files were placed with their experiments. The original guides refer to some generated Python files, reference images, and `results/` logs that were not supplied. Generate the tone Python files in Companion; the other referenced artifacts are not included in this upload. Statements about earlier calculations or tests in the supplied guides describe their original preparation, not a new hardware test.

For the initial AM upload, the four `.grc` files were parsed as YAML and the three Python scripts were checked for syntax. GNU Radio execution, radio communication, and audio quality have not been verified in this upload.

The previous repository contents were replaced in the current revision and remain available in Git history.
