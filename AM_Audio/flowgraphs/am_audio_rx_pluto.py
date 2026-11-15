#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: AM audio receiver for ADALM-PLUTO (Laptop 2)
# Description: PlutoSDR Source -> channel select -> envelope -> DC removal -> 4 kHz filter -> 48 kS/s audio
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import audio
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



class am_audio_rx_pluto(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "AM audio receiver for ADALM-PLUTO (Laptop 2)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("AM audio receiver for ADALM-PLUTO (Laptop 2)")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "am_audio_rx_pluto")

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
        self.volume = volume = 1
        self.rx_gain = rx_gain = 30
        self.rf_bw = rf_bw = 1000000
        self.rec_path = rec_path = "recovered_audio.f32"
        self.pluto_uri = pluto_uri = "usb:1.9.5"
        self.lo_freq = lo_freq = 2450000000
        self.if_rate = if_rate = int(samp_rate/10)
        self.fc_rx = fc_rx = 100000
        self.audio_rate = audio_rate = 48000

        ##################################################
        # Blocks
        ##################################################

        self.tabs = Qt.QTabWidget()
        self.tabs_widget_0 = Qt.QWidget()
        self.tabs_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_0)
        self.tabs_grid_layout_0 = Qt.QGridLayout()
        self.tabs_layout_0.addLayout(self.tabs_grid_layout_0)
        self.tabs.addTab(self.tabs_widget_0, '1 Raw I/Q (clipping check)')
        self.tabs_widget_1 = Qt.QWidget()
        self.tabs_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_1)
        self.tabs_grid_layout_1 = Qt.QGridLayout()
        self.tabs_layout_1.addLayout(self.tabs_grid_layout_1)
        self.tabs.addTab(self.tabs_widget_1, '2 Wide spectrum (find carrier)')
        self.tabs_widget_2 = Qt.QWidget()
        self.tabs_layout_2 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_2)
        self.tabs_grid_layout_2 = Qt.QGridLayout()
        self.tabs_layout_2.addLayout(self.tabs_grid_layout_2)
        self.tabs.addTab(self.tabs_widget_2, '3 Selected channel')
        self.tabs_widget_3 = Qt.QWidget()
        self.tabs_layout_3 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_3)
        self.tabs_grid_layout_3 = Qt.QGridLayout()
        self.tabs_layout_3.addLayout(self.tabs_grid_layout_3)
        self.tabs.addTab(self.tabs_widget_3, '4 Recovered audio')
        self.top_grid_layout.addWidget(self.tabs, 1, 0, 1, 3)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = qtgui.Range(0, 70, 1, 30, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "RX gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._fc_rx_range = qtgui.Range(50000, 150000, 250, 100000, 200)
        self._fc_rx_win = qtgui.RangeWidget(self._fc_rx_range, self.set_fc_rx, "Carrier position (Hz) - tune to the peak", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._fc_rx_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.xlate = filter.freq_xlating_fir_filter_ccc(10, firdes.low_pass(1, samp_rate, 15e3, 5e3), fc_rx, samp_rate)
        self._volume_range = qtgui.Range(0, 30, 0.1, 1, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume (start low!)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._volume_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.vol = blocks.multiply_const_ff(volume)
        self.t_rec = qtgui.time_sink_f(
            4096, #size
            audio_rate, #samp_rate
            "Recovered audio vs time (s)", #name
            1, #number of inputs
            None # parent
        )
        self.t_rec.set_update_time(0.10)
        self.t_rec.set_y_axis(-2, 2)

        self.t_rec.set_y_label('Amplitude', "")

        self.t_rec.enable_tags(True)
        self.t_rec.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.t_rec.enable_autoscale(True)
        self.t_rec.enable_grid(True)
        self.t_rec.enable_axis_labels(True)
        self.t_rec.enable_control_panel(False)
        self.t_rec.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.t_rec.set_line_label(i, "Data {0}".format(i))
            else:
                self.t_rec.set_line_label(i, labels[i])
            self.t_rec.set_line_width(i, widths[i])
            self.t_rec.set_line_color(i, colors[i])
            self.t_rec.set_line_style(i, styles[i])
            self.t_rec.set_line_marker(i, markers[i])
            self.t_rec.set_line_alpha(i, alphas[i])

        self._t_rec_win = sip.wrapinstance(self.t_rec.qwidget(), Qt.QWidget)
        self.tabs_grid_layout_3.addWidget(self._t_rec_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_3.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_3.setColumnStretch(c, 1)
        self.t_iq = qtgui.time_sink_c(
            512, #size
            samp_rate, #samp_rate
            "Raw I (blue) and Q (red): flat tops = clipping", #name
            1, #number of inputs
            None # parent
        )
        self.t_iq.set_update_time(0.10)
        self.t_iq.set_y_axis(-1.2, 1.2)

        self.t_iq.set_y_label('Amplitude', "")

        self.t_iq.enable_tags(True)
        self.t_iq.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.t_iq.enable_autoscale(False)
        self.t_iq.enable_grid(True)
        self.t_iq.enable_axis_labels(True)
        self.t_iq.enable_control_panel(False)
        self.t_iq.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.t_iq.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.t_iq.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.t_iq.set_line_label(i, labels[i])
            self.t_iq.set_line_width(i, widths[i])
            self.t_iq.set_line_color(i, colors[i])
            self.t_iq.set_line_style(i, styles[i])
            self.t_iq.set_line_marker(i, markers[i])
            self.t_iq.set_line_alpha(i, alphas[i])

        self._t_iq_win = sip.wrapinstance(self.t_iq.qwidget(), Qt.QWidget)
        self.tabs_grid_layout_0.addWidget(self._t_iq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.spk = audio.sink(audio_rate, '', True)
        self.pluto_rx = iio.fmcomms2_source_fc32(pluto_uri if pluto_uri else iio.get_pluto_uri(), [True, True], 32768)
        self.pluto_rx.set_len_tag_key('packet_len')
        self.pluto_rx.set_frequency(int(lo_freq))
        self.pluto_rx.set_samplerate(int(samp_rate))
        self.pluto_rx.set_gain_mode(0, 'slow_attack')
        self.pluto_rx.set_gain(0, rx_gain)
        self.pluto_rx.set_quadrature(True)
        self.pluto_rx.set_rfdc(True)
        self.pluto_rx.set_bbdc(True)
        self.pluto_rx.set_filter_params('Auto', '', 0, 0)
        self.mag = blocks.complex_to_mag(1)
        self.lpf = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                if_rate,
                4000,
                1000,
                window.WIN_HAMMING,
                6.76))
        self.f_wide = qtgui.freq_sink_c(
            8192, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            lo_freq, #fc
            samp_rate, #bw
            "Wide spectrum, RF centre = lo_freq: carrier near +100 kHz, DC spike at centre", #name
            1,
            None # parent
        )
        self.f_wide.set_update_time(0.10)
        self.f_wide.set_y_axis((-120), 0)
        self.f_wide.set_y_label('Relative Gain', 'dB')
        self.f_wide.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.f_wide.enable_autoscale(False)
        self.f_wide.enable_grid(True)
        self.f_wide.set_fft_average(0.2)
        self.f_wide.enable_axis_labels(True)
        self.f_wide.enable_control_panel(False)
        self.f_wide.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.f_wide.set_line_label(i, "Data {0}".format(i))
            else:
                self.f_wide.set_line_label(i, labels[i])
            self.f_wide.set_line_width(i, widths[i])
            self.f_wide.set_line_color(i, colors[i])
            self.f_wide.set_line_alpha(i, alphas[i])

        self._f_wide_win = sip.wrapinstance(self.f_wide.qwidget(), Qt.QWidget)
        self.tabs_grid_layout_1.addWidget(self._f_wide_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_1.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_1.setColumnStretch(c, 1)
        self.f_sel = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            if_rate, #bw
            "Selected channel: carrier at 0 Hz, audio sidebands within +-4 kHz", #name
            1,
            None # parent
        )
        self.f_sel.set_update_time(0.10)
        self.f_sel.set_y_axis((-120), 0)
        self.f_sel.set_y_label('Relative Gain', 'dB')
        self.f_sel.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.f_sel.enable_autoscale(False)
        self.f_sel.enable_grid(True)
        self.f_sel.set_fft_average(0.2)
        self.f_sel.enable_axis_labels(True)
        self.f_sel.enable_control_panel(False)
        self.f_sel.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.f_sel.set_line_label(i, "Data {0}".format(i))
            else:
                self.f_sel.set_line_label(i, labels[i])
            self.f_sel.set_line_width(i, widths[i])
            self.f_sel.set_line_color(i, colors[i])
            self.f_sel.set_line_alpha(i, alphas[i])

        self._f_sel_win = sip.wrapinstance(self.f_sel.qwidget(), Qt.QWidget)
        self.tabs_grid_layout_2.addWidget(self._f_sel_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_2.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_2.setColumnStretch(c, 1)
        self.f_rec = qtgui.freq_sink_f(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            audio_rate, #bw
            "Recovered audio spectrum (compare with TX tab 2)", #name
            1,
            None # parent
        )
        self.f_rec.set_update_time(0.10)
        self.f_rec.set_y_axis((-120), 0)
        self.f_rec.set_y_label('Relative Gain', 'dB')
        self.f_rec.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.f_rec.enable_autoscale(False)
        self.f_rec.enable_grid(True)
        self.f_rec.set_fft_average(0.2)
        self.f_rec.enable_axis_labels(True)
        self.f_rec.enable_control_panel(False)
        self.f_rec.set_fft_window_normalized(False)


        self.f_rec.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.f_rec.set_line_label(i, "Data {0}".format(i))
            else:
                self.f_rec.set_line_label(i, labels[i])
            self.f_rec.set_line_width(i, widths[i])
            self.f_rec.set_line_color(i, colors[i])
            self.f_rec.set_line_alpha(i, alphas[i])

        self._f_rec_win = sip.wrapinstance(self.f_rec.qwidget(), Qt.QWidget)
        self.tabs_grid_layout_3.addWidget(self._f_rec_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_3.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_3.setColumnStretch(c, 1)
        self.down = filter.rational_resampler_fff(
                interpolation=1,
                decimation=2,
                taps=[],
                fractional_bw=0)
        self.dcb = filter.dc_blocker_ff(1920, True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.dcb, 0), (self.lpf, 0))
        self.connect((self.down, 0), (self.f_rec, 0))
        self.connect((self.down, 0), (self.t_rec, 0))
        self.connect((self.down, 0), (self.vol, 0))
        self.connect((self.lpf, 0), (self.down, 0))
        self.connect((self.mag, 0), (self.dcb, 0))
        self.connect((self.pluto_rx, 0), (self.f_wide, 0))
        self.connect((self.pluto_rx, 0), (self.t_iq, 0))
        self.connect((self.pluto_rx, 0), (self.xlate, 0))
        self.connect((self.vol, 0), (self.spk, 0))
        self.connect((self.xlate, 0), (self.f_sel, 0))
        self.connect((self.xlate, 0), (self.mag, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "am_audio_rx_pluto")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_if_rate(int(self.samp_rate/10))
        self.f_wide.set_frequency_range(self.lo_freq, self.samp_rate)
        self.pluto_rx.set_samplerate(int(self.samp_rate))
        self.t_iq.set_samp_rate(self.samp_rate)
        self.xlate.set_taps(firdes.low_pass(1, self.samp_rate, 15e3, 5e3))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.vol.set_k(self.volume)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.pluto_rx.set_gain(0, self.rx_gain)

    def get_rf_bw(self):
        return self.rf_bw

    def set_rf_bw(self, rf_bw):
        self.rf_bw = rf_bw

    def get_rec_path(self):
        return self.rec_path

    def set_rec_path(self, rec_path):
        self.rec_path = rec_path

    def get_pluto_uri(self):
        return self.pluto_uri

    def set_pluto_uri(self, pluto_uri):
        self.pluto_uri = pluto_uri

    def get_lo_freq(self):
        return self.lo_freq

    def set_lo_freq(self, lo_freq):
        self.lo_freq = lo_freq
        self.f_wide.set_frequency_range(self.lo_freq, self.samp_rate)
        self.pluto_rx.set_frequency(int(self.lo_freq))

    def get_if_rate(self):
        return self.if_rate

    def set_if_rate(self, if_rate):
        self.if_rate = if_rate
        self.f_sel.set_frequency_range(0, self.if_rate)
        self.lpf.set_taps(firdes.low_pass(1, self.if_rate, 4000, 1000, window.WIN_HAMMING, 6.76))

    def get_fc_rx(self):
        return self.fc_rx

    def set_fc_rx(self, fc_rx):
        self.fc_rx = fc_rx
        self.xlate.set_center_freq(self.fc_rx)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.f_rec.set_frequency_range(0, self.audio_rate)
        self.t_rec.set_samp_rate(self.audio_rate)




def main(top_block_cls=am_audio_rx_pluto, options=None):

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
