"""Summarize the course logger's CSV using Python's standard library.

Usage: python summarize_log.py tx_on.csv --baseline tx_off.csv
The means are computed in linear power units before logarithmic conversion.
"""
import argparse
import csv
import json
import math
import statistics

SETTING_KEYS = ('sample_rate_sps', 'rf_center_hz', 'channel_offset_hz',
                'rx_gain_db', 'gain_mode', 'channel_cutoff_hz',
                'transition_width_hz', 'window_s')


def summarize(path):
    with open(path, newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        needed = set(SETTING_KEYS) | {'valid', 'power_linear_digital',
                                      'sample_start', 'sample_end_exclusive'}
        if not needed.issubset(reader.fieldnames or []):
            raise ValueError('Missing required CSV columns: ' + ', '.join(sorted(needed-set(reader.fieldnames or []))))
        rows = list(reader)
    if not rows:
        raise ValueError('CSV has no data windows')
    settings = {}
    for key in SETTING_KEYS:
        values = {row[key] if key == 'gain_mode' else float(row[key]) for row in rows}
        if len(values) != 1:
            raise ValueError('Settings change inside the run: ' + key)
        settings[key] = values.pop()
        if key != 'gain_mode' and not math.isfinite(settings[key]):
            raise ValueError('Nonfinite setting: ' + key)
    if settings['sample_rate_sps'] <= 0 or settings['window_s'] <= 0:
        raise ValueError('Sample rate and window duration must be positive')
    if settings['gain_mode'] != 'manual':
        raise ValueError('This comparison expects manual gain')
    expected_count = settings['sample_rate_sps'] * settings['window_s']
    previous_end = None
    powers = []
    rejected = 0
    for row in rows:
        begin, end = int(row['sample_start']), int(row['sample_end_exclusive'])
        if end <= begin or not math.isclose(end-begin, expected_count, abs_tol=1e-7):
            raise ValueError('Invalid sample window length')
        if previous_end is not None and begin != previous_end:
            raise ValueError('Gap or overlap in saved sample indices')
        previous_end = end
        try:
            p = float(row['power_linear_digital'])
        except ValueError:
            p = float('nan')
        if row['valid'] != '1' or not math.isfinite(p) or p < 0:
            rejected += 1
            continue
        powers.append(p)
    if not powers:
        raise ValueError('No valid finite nonnegative power windows')
    mean = statistics.fmean(powers)
    result = dict(file=str(path), settings=settings, total_windows=len(rows),
                  valid_windows=len(powers), rejected_windows=rejected,
                  mean_linear_digital=mean,
                  db_of_mean_re_1=10*math.log10(mean) if mean > 0 else None,
                  stddev_linear=statistics.pstdev(powers),
                  min_linear=min(powers),max_linear=max(powers))
    return result


def compare(on, off):
    mismatches = [key for key in SETTING_KEYS if on['settings'][key] != off['settings'][key]]
    if mismatches:
        raise ValueError('Incompatible baseline settings: ' + ', '.join(mismatches))
    excess = on['mean_linear_digital'] - off['mean_linear_digital']
    return dict(excess_linear_digital=excess,
                excess_db_re_1=10*math.log10(excess) if excess > 0 else None,
                status='positive excess above baseline' if excess > 0 else 'no positive excess above this baseline',
                note='Operator must also verify comparable environment, antennas, TX state and frequency drift. This is not calibrated dBm or distance.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file')
    parser.add_argument('--baseline')
    args = parser.parse_args()
    try:
        report = summarize(args.csv_file)
        if args.baseline:
            baseline = summarize(args.baseline)
            report['baseline'] = baseline
            report['comparison'] = compare(report, baseline)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, 'Cannot summarize: ' + str(exc) + '\n')
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
