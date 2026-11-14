"""GNU Radio embedded measurement sink. No files are opened during GRC inspection."""
import csv
from datetime import datetime, timezone
from pathlib import Path
import time
import uuid
import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    """Log nonoverlapping channel-power windows with host processing timestamps.

    The timestamps are NOT sample-synchronized radio timestamps. A run_label is
    manually assigned metadata; it is not an identity decoded from the beacon.
    Stop the graph before changing settings. Initial one second is discarded.
    """
    def __init__(self, sample_rate=48000, window_samples=4800,
                 output_file='beacon_log.csv', run_label='tx_off',
                 rf_center_hz=2450000000, channel_offset_hz=100000,
                 rx_gain_db=20):
        gr.sync_block.__init__(self, name='Timestamped channel-power logger',
                               in_sig=[np.complex64], out_sig=[])
        self._fs = int(sample_rate)
        self._window = int(window_samples)
        if self._fs <= 0 or self._window <= 0:
            raise ValueError('Sample rate and window size must be positive')
        self._filename = str(output_file)
        self._label = str(run_label)
        self._rf = float(rf_center_hz)
        self._offset = float(channel_offset_hz)
        self._gain = float(rx_gain_db)
        self._skip = self._fs
        self._next_start = self._fs
        self._pending = np.empty(0, dtype=np.complex64)
        self._handle = None
        self._writer = None
        self._seq = 0

    def _open(self):
        target = Path(self._filename).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                self._handle = target.open('x', newline='', encoding='utf-8')
                break
            except FileExistsError:
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
                target = target.with_name(target.stem + '_' + stamp + '_' + uuid.uuid4().hex[:6] + target.suffix)
        fields = ['host_processed_utc','host_monotonic_s','sequence','run_label',
                  'sample_start','sample_end_exclusive','stream_start_s','window_s',
                  'sample_rate_sps','rf_center_hz','channel_offset_hz','rx_gain_db',
                  'gain_mode','channel_cutoff_hz','transition_width_hz',
                  'power_linear_digital','power_db_re_1','valid']
        self._writer = csv.DictWriter(self._handle, fieldnames=fields)
        self._writer.writeheader()
        print('Power log:', target, flush=True)

    def work(self, input_items, output_items):
        original = input_items[0]
        data = original
        if self._skip:
            count = min(self._skip, len(data))
            data = data[count:]
            self._skip -= count
        if len(data):
            if self._handle is None:
                self._open()
            self._pending = np.concatenate((self._pending, data))
            n_complete = len(self._pending) // self._window
            for i in range(n_complete):
                z = self._pending[i*self._window:(i+1)*self._window].astype(np.complex128)
                valid = bool(np.all(np.isfinite(z)))
                p = float(np.mean(np.abs(z)**2)) if valid else float('nan')
                db = float(10*np.log10(p)) if valid and p > 0 else None
                self._writer.writerow(dict(
                    host_processed_utc=datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                    host_monotonic_s=f'{time.monotonic():.6f}', sequence=self._seq,
                    run_label=self._label, sample_start=self._next_start,
                    sample_end_exclusive=self._next_start+self._window,
                    stream_start_s=self._next_start/self._fs, window_s=self._window/self._fs,
                    sample_rate_sps=self._fs, rf_center_hz=self._rf,
                    channel_offset_hz=self._offset, rx_gain_db=self._gain,
                    gain_mode='manual',channel_cutoff_hz=5000, transition_width_hz=3000,
                    power_linear_digital=p if valid else '',
                    power_db_re_1=db if db is not None else '',valid=int(valid)))
                self._seq += 1
                self._next_start += self._window
            self._pending = self._pending[n_complete*self._window:].copy()
            self._handle.flush()
        return len(original)

    def stop(self):
        if self._handle is not None:
            self._handle.flush()
            self._handle.close()
            self._handle = None
        return True
