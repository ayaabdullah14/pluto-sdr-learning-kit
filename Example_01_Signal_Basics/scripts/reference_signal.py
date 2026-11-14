"""Independent numerical reference, not a GNU Radio or hardware test.

Run from any directory: python reference_signal.py
Needs NumPy and Matplotlib; writes only to this example's results folder.
"""

from pathlib import Path
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    results = Path(__file__).resolve().parents[1] / "results"
    results.mkdir(exist_ok=True)
    fs, f0, amplitude, fft_size, shown_samples = 48000, 1500, 0.5, 4096, 192
    n = np.arange(fft_size)
    x = amplitude * np.cos(2 * np.pi * f0 * n / fs)
    freq = np.fft.fftshift(np.fft.fftfreq(fft_size, d=1 / fs))
    coeff = np.abs(np.fft.fftshift(np.fft.fft(x))) / fft_size
    peak_indices = np.argsort(coeff)[-2:]
    peak_hz = sorted(float(freq[i]) for i in peak_indices)
    peak_coefficients = sorted(float(coeff[i]) for i in peak_indices)
    power = float(np.mean(x * x))
    half_amplitude_power = float(np.mean((x / 2) ** 2))
    relative_db = float(10 * np.log10(half_amplitude_power / power))
    aliased = amplitude * np.cos(2 * np.pi * 30000 * n / fs)
    expected_alias = amplitude * np.cos(2 * np.pi * 18000 * n / fs)

    checks = {
        "spectral_frequencies": bool(np.allclose(peak_hz, [-1500, 1500])),
        "two_sided_coefficients": bool(np.allclose(peak_coefficients, [0.25, 0.25])),
        "mean_square": bool(np.isclose(power, 0.125)),
        "half_amplitude_power": bool(np.isclose(half_amplitude_power, 0.03125)),
        "half_amplitude_relative_db": bool(np.isclose(relative_db, -6.020599913279624)),
        "period_32_samples": bool(np.allclose(x[:-32], x[32:])),
        "sample_extrema": bool(np.isclose(x.max(), 0.5) and np.isclose(x.min(), -0.5)),
        "alias_30k_equals_18k": bool(np.allclose(aliased, expected_alias, atol=1e-10)),
    }
    report = {
        "evidence_type": "Independent NumPy simulation; no GNU Radio execution or hardware test",
        "settings": {"sample_rate_sps": fs, "tone_hz": f0, "amplitude_digital_units": amplitude,
                     "fft_size": fft_size, "window": "Rectangular"},
        "computed_results": {
            "peak_frequencies_hz": peak_hz,
            "two_sided_coefficients_digital_units": peak_coefficients,
            "mean_square_digital_units_squared": power,
            "half_amplitude_mean_square": half_amplitude_power,
            "half_amplitude_relative_db": relative_db,
            "period_ms": 1000 / f0,
            "samples_per_cycle": fs / f0,
            "fft_bin_spacing_hz": fs / fft_size,
            "fft_record_ms": 1000 * fft_size / fs,
            "nominal_time_frame_ms": 1000 * shown_samples / fs,
            "last_displayed_sample_ms": 1000 * (shown_samples - 1) / fs,
        },
        "checks": checks,
        "all_checks_passed": all(checks.values()),
    }
    (results / "numerical_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (results / "reference_samples.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_index", "time_s", "amplitude_digital_units"])
        writer.writerows((int(i), float(i / fs), float(value)) for i, value in zip(n, x))

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), layout="constrained")
    fig.suptitle("Example 1 | Numerical reference simulation", fontsize=17, weight="bold")
    axes[0].plot(1000 * n[:shown_samples] / fs, x[:shown_samples], color="#126e82", linewidth=1.7)
    axes[0].set(xlabel="Time (ms)", ylabel="Amplitude (digital units)",
                title="Time: 1,500 Hz cosine | amplitude 0.5 | 48,000 samples/s",
                xlim=(0, 4), ylim=(-0.6, 0.6))
    axes[0].grid(alpha=0.2)
    axes[1].plot(freq, coeff, color="#a84d30", linewidth=1.2)
    axes[1].set(xlabel="Baseband frequency (Hz)", ylabel="Two-sided DFT magnitude / N\n(digital units)",
                title="Spectrum: rectangular window | N = 4,096 | bin spacing 11.71875 Hz",
                xlim=(-5000, 5000), ylim=(0, 0.30))
    axes[1].set_xticks([-4500, -3000, -1500, 0, 1500, 3000, 4500])
    for tone in (-1500, 1500):
        axes[1].annotate(f"{tone:+,} Hz", xy=(tone, 0.25), xytext=(tone, 0.275), ha="center", fontsize=10)
    axes[1].grid(alpha=0.2)
    fig.savefig(results / "reference_signal.png", dpi=170)
    plt.close(fig)
    if not all(checks.values()):
        raise AssertionError(report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
