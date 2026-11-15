# Pluto SDR Learning Kit

GNU Radio AM learning files for two ADALM-PLUTO devices, organized from the supplied files.

| Experiment | Files and guide |
|---|---|
| AM modulation and demodulation with a sinusoidal message | [AM tone guide](AM_Mod_Demod/pluto/README.md) · [TX](AM_Mod_Demod/pluto/am_tx_pluto.grc) · [RX](AM_Mod_Demod/pluto/am_rx_pluto.grc) |
| AM audio transmission and recovery | [Audio guide](AM_Audio/README.md) · [Report](AM_Audio/REPORT.md) · [TX](AM_Audio/flowgraphs/am_audio_tx_pluto.grc) · [RX](AM_Audio/flowgraphs/am_audio_rx_pluto.grc) |

## Start here

Open the `.grc` files in GNU Radio Companion (target environment: GNU Radio 3.10.12.0 / Python 3.12.9). Generate and run the Python code from Companion after setting the correct device URI on each laptop. The supplied audio RX Python file is also included in `AM_Audio/flowgraphs/`.

The two experiments use different sample-rate settings. Follow the guide belonging to the flowgraphs you open.

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

## Included material and validation

All ten supplied files are preserved without content changes; download suffixes were removed from the tone filenames and the two README files were placed with their experiments. The original guides refer to some generated Python files, reference images, and `results/` logs that were not supplied. Generate the tone Python files in Companion; the other referenced artifacts are not included in this upload. Statements about earlier calculations or tests in the supplied guides describe their original preparation, not a new hardware test.

For this upload, the four `.grc` files were parsed as YAML and the three Python scripts were checked for syntax. GNU Radio execution, radio communication, and audio quality have not been verified in this upload.

The previous repository contents were replaced in the current revision and remain available in Git history.
