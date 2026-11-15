#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tone receiver: spectrum and averaged channel power (Laptop 2)
# Description: PlutoSDR Source -> Frequency Sink (find the tone) and Xlating filter -> |x|^2 -> Moving Average -> 10*log10 -> Number Sink
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import sip
import threading



class rx_tone_power(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Tone receiver: spectrum and averaged channel power (Laptop 2)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Tone receiver: spectrum and averaged channel power (Laptop 2)")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rx_tone_power")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 960000
        self.decim = decim = 20
        self.chan_rate = chan_rate = int(samp_rate/decim)
        self.rx_gain = rx_gain = 30
        self.pluto_uri = pluto_uri = "ip:192.168.2.1"
        self.lo_freq = lo_freq = 2450000000
        self.fc_rx = fc_rx = 100000
        self.avg_len = avg_len = chan_rate

        ##################################################
        # Blocks
        ##################################################

        self._fc_rx_range = qtgui.Range(20000, 180000, 50, 100000, 200)
        self._fc_rx_win = qtgui.RangeWidget(self._fc_rx_range, self.set_fc_rx, "Measurement filter centre (Hz): set to the tone peak", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._fc_rx_win, 4, 0, 1, 3)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.xlate = filter.freq_xlating_fir_filter_ccc(decim, firdes.low_pass(1, samp_rate, 5e3, 2e3), fc_rx, samp_rate)
        self.todb = blocks.nlog10_ff(10, 1, 0)
        self.spec = qtgui.freq_sink_c(
            8192, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "RX spectrum (baseband Hz): find the tone peak", #name
            1,
            None # parent
        )
        self.spec.set_update_time(0.10)
        self.spec.set_y_axis((-120), 0)
        self.spec.set_y_label('Relative Gain', 'dB')
        self.spec.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.spec.enable_autoscale(False)
        self.spec.enable_grid(True)
        self.spec.set_fft_average(0.2)
        self.spec.enable_axis_labels(True)
        self.spec.enable_control_panel(True)
        self.spec.set_fft_window_normalized(False)



        labels = ["RX", '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.spec.set_line_label(i, "Data {0}".format(i))
            else:
                self.spec.set_line_label(i, labels[i])
            self.spec.set_line_width(i, widths[i])
            self.spec.set_line_color(i, colors[i])
            self.spec.set_line_alpha(i, alphas[i])

        self._spec_win = sip.wrapinstance(self.spec.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._spec_win, 0, 0, 4, 3)
        for r in range(0, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pluto_rx = iio.fmcomms2_source_fc32(pluto_uri if pluto_uri else iio.get_pluto_uri(), [True, True], 32768)
        self.pluto_rx.set_len_tag_key('packet_len')
        self.pluto_rx.set_frequency(int(lo_freq))
        self.pluto_rx.set_samplerate(int(samp_rate))
        self.pluto_rx.set_gain_mode(0, 'manual')
        self.pluto_rx.set_gain(0, rx_gain)
        self.pluto_rx.set_quadrature(True)
        self.pluto_rx.set_rfdc(True)
        self.pluto_rx.set_bbdc(True)
        self.pluto_rx.set_filter_params('Auto', '', 0, 0)
        self.num = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.num.set_update_time(0.25)
        self.num.set_title("Relative digital power of selected channel")

        labels = ["Power (dB, relative digital)", '', '', '', '',
            '', '', '', '', '']
        units = ["dB", '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.num.set_min(i, -120)
            self.num.set_max(i, 0)
            self.num.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.num.set_label(i, "Data {0}".format(i))
            else:
                self.num.set_label(i, labels[i])
            self.num.set_unit(i, units[i])
            self.num.set_factor(i, factor[i])

        self.num.enable_autoscale(False)
        self._num_win = sip.wrapinstance(self.num.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._num_win, 5, 0, 1, 3)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mag2 = blocks.complex_to_mag_squared(1)
        self.avg = blocks.moving_average_ff(avg_len, (1.0/avg_len), 4000, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.avg, 0), (self.todb, 0))
        self.connect((self.mag2, 0), (self.avg, 0))
        self.connect((self.pluto_rx, 0), (self.spec, 0))
        self.connect((self.pluto_rx, 0), (self.xlate, 0))
        self.connect((self.todb, 0), (self.num, 0))
        self.connect((self.xlate, 0), (self.mag2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rx_tone_power")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_chan_rate(int(self.samp_rate/self.decim))
        self.pluto_rx.set_samplerate(int(self.samp_rate))
        self.xlate.set_taps(firdes.low_pass(1, self.samp_rate, 5e3, 2e3))
        self.spec.set_frequency_range(0, self.samp_rate)

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.set_chan_rate(int(self.samp_rate/self.decim))

    def get_chan_rate(self):
        return self.chan_rate

    def set_chan_rate(self, chan_rate):
        self.chan_rate = chan_rate
        self.set_avg_len(self.chan_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.pluto_rx.set_gain(0, self.rx_gain)

    def get_pluto_uri(self):
        return self.pluto_uri

    def set_pluto_uri(self, pluto_uri):
        self.pluto_uri = pluto_uri

    def get_lo_freq(self):
        return self.lo_freq

    def set_lo_freq(self, lo_freq):
        self.lo_freq = lo_freq
        self.pluto_rx.set_frequency(int(self.lo_freq))

    def get_fc_rx(self):
        return self.fc_rx

    def set_fc_rx(self, fc_rx):
        self.fc_rx = fc_rx
        self.xlate.set_center_freq(self.fc_rx)

    def get_avg_len(self):
        return self.avg_len

    def set_avg_len(self, avg_len):
        self.avg_len = avg_len
        self.avg.set_length_and_scale(self.avg_len, (1.0/self.avg_len))




def main(top_block_cls=rx_tone_power, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
