# Validation and honest limits

Target reported by the user: **GNU Radio 3.10.12.0 / Python 3.12.9**. The development environment has Python numerical tools but does not have an installed GNU Radio DSP runtime or connected Pluto devices.

## Checks performed

| Check | Method | Result / practical limit |
| --- | --- | --- |
| 16 `.grc` files | Official v3.10.12.0 GRC core parser, block definitions, port/parameter checks and Python generator | All files parsed, validated structurally and generated Python with valid syntax |
| Runtime stand-ins used during generation | Minimal stand-ins supplied enum constants and the Embedded Python base-class/port interface; FIR tap evaluation used a placeholder for code generation | This is **not** an installed GNU Radio run and does not execute DSP, Qt, audio, IIO or hardware drivers |
| Example 1 mathematics | Independent NumPy samples/FFT/power checks | 8 checks passed; see Example 1 results/numerical_checks.json |
| Signal/AM/audio/filter mathematics | Independent NumPy/SciPy models; low-pass formula reimplemented from official Hamming-window design | 9 checks passed; see validation/numerical_model_checks.json |
| CSV logger and summary | Direct Python work/stop calls with deliberately uneven chunks and a minimal base-class stand-in | 12 checks passed: startup discard, complete/nonoverlapping windows, power, invalid/zero values, file preservation and incompatible baseline rejection |
| API/source review | Exact-version Pluto source/sink templates, receiver public API, bindings and implementation | Avoided a nonexistent receiver bandwidth setter; documented native RX bandwidth behavior in COMPATIBILITY.md |
| Figures and layout guides | Reference plots generated from stated models; circuit guide images generated from saved coordinates and visually inspected | They are illustrations/simulations, not GRC screenshots or hardware captures |
| Audio asset | Generated mono 16-bit PCM WAV at 48000 samples/s | 7.5 s known tone sequence; no received or voice recording claimed |

The generation checks catch missing block IDs, structural/port/parameter mistakes and Python syntax problems. They cannot establish that a Windows installation has all native modules, that a radio accepts the settings, that Qt rendering/audio works, or that real-time throughput is stable. The independent numerical models test the stated mathematics; they are not executions of GNU Radio's C++ kernels. The isolated logger tests do not run the GNU Radio scheduler.

## What you must verify locally

1. Both radios are recognized and the native GNU Radio IIO module is available in the environment you use.
2. Example 1 generates and executes in your GRC, with the expected time period and spectrum.
3. Local USB/network URIs, actual radio settings, approved RF conditions and attenuation arrangement are correct.
4. TX-off/on and deliberate frequency-change checks prove reception.
5. The measured carrier is inside the selected channel; clipping and overrun/underrun problems are resolved before collecting measurements.
6. The known audio sequence has the expected recovered pitch, and log files contain plausible complete windows with the right settings.

There are no invented received-power levels, measured screenshots, localization errors or successful hardware-test claims in this package. Blank measurement worksheets are intentional. Console overrun/underrun errors can indicate lost data that a simple finite-value CSV flag cannot detect; annotate or discard affected runs rather than assuming valid numerical samples prove gap-free acquisition.
