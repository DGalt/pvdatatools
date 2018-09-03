__author__ = 'Dan'

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from ..extra_mods.EphysTools import pacemaking as pace
from .AnalysisWidget import AnalysisWidget


class FrequencyWidget(AnalysisWidget):

    def __init__(self, model):
        super().__init__(model)
        self.setWindowTitle("Frequency Analysis")

        self.setup_groupbox()

        self.min_height = -20.0

    def setup_groupbox(self):
        layout = QtGui.QVBoxLayout(self.analysis_groupbox)
        sublayout = QtGui.QHBoxLayout()

        #radio_layout = QtGui.QVBoxLayout()
        units_label = QtGui.QLabel("Units:")
        units_group = QtGui.QGroupBox()
        units_group.setStyleSheet("border:0;")
        unit_layout = QtGui.QHBoxLayout(units_group)
        self.hz_radio = QtGui.QRadioButton("Hz", units_group)
        self.hz_radio.setChecked(True)
        self.isi_radio = QtGui.QRadioButton("ISI (s)", units_group)
        unit_layout.addWidget(units_label)
        unit_layout.addWidget(self.hz_radio)
        unit_layout.addWidget(self.isi_radio)

        select_label = QtGui.QLabel("Select: ")
        select_group = QtGui.QGroupBox()
        select_group.setStyleSheet("border:0;")
        select_layout = QtGui.QHBoxLayout(select_group)
        self.full_radio = QtGui.QRadioButton("Entire sweep")
        self.full_radio.setChecked(True)
        self.subregion_radio = QtGui.QRadioButton("Subregion with markers")
        select_layout.addWidget(select_label)
        select_layout.addWidget(self.full_radio)
        select_layout.addWidget(self.subregion_radio)

        min_height_label = QtGui.QLabel("Min. AP height (mV):")
        self.min_height_txt = QtGui.QLineEdit("-20")
        self.min_height_txt.setMaximumSize(QtCore.QSize(40, 25))
        self.min_height_txt.editingFinished.connect(lambda : self.set_protocol_params(label="min_height"))

        analysis_btn = QtGui.QPushButton("Run Analysis")
        analysis_btn.setMinimumWidth(200)
        analysis_btn.clicked.connect(self.run_analysis)

        self.spike_plot_check = QtGui.QCheckBox("Plot detected spikes")
        self.spike_plot_check.setChecked(True)
        self.freq_plot_check = QtGui.QCheckBox("Plot frequency vs. time")
        #self.freq_plot_check.setChecked(True)

        sublayout.addStretch()
        #sublayout.addWidget(units_label)
        sublayout.addWidget(units_group)
        #sublayout.addWidget(select_label)
        sublayout.addWidget(select_group)
        sublayout.addWidget(min_height_label)
        sublayout.addWidget(self.min_height_txt)
        sublayout.addStretch()

        btn_layout = QtGui.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(analysis_btn)
        btn_layout.addWidget(self.spike_plot_check)
        btn_layout.addWidget(self.freq_plot_check)
        btn_layout.addStretch()

        layout.addLayout(sublayout)
        layout.addLayout(btn_layout)
        #layout.addStretch()

    def set_protocol_params(self, label):
        try:
            if label == "min_height":
                self.min_height = float(self.min_height_txt.text())
        except ValueError:
            QtGui.QMessageBox.about(self, "Error", "Must enter a numeric value")

    def get_freq_vals(self):
        checked = self.model.checked_dict
        times_list = []
        freqs_list = []
        indexes_list = []

        if self.full_radio.isChecked():
            for folder in checked.keys():
                current_df = self.model.data[folder]
                for key in checked[folder].keys():
                    if key in self.model.vr_headers[folder]:
                        for sweep in checked[folder][key]:
                            time_array = current_df['voltage recording']['Time'][sweep].values
                            data = current_df['voltage recording'][key][sweep].values

                            indexes = pace.detect_peaks(data, mph=self.min_height, mpd=100)
                            indexes_list.append(indexes)

                            if self.hz_radio.isChecked():
                                unit = "Hz"
                                times, freqs = pace.calc_frequency(time_array, indexes)
                                times_list.append(times)
                                freqs_list.append(freqs)


                                col_header = ("Analysis %s:" % self.analysis_counter) + " " + sweep + " (Hz)"
                                self.add_table_column(col_header, freqs, avg=True)
                            else:
                                unit = "ISI (s)"
                                times, freqs = pace.calc_frequency(time_array, indexes, hz=False)

                                times_list.append(times)
                                freqs_list.append(freqs)

                                col_header = ("Analysis %s:" % self.analysis_counter) + " " + sweep + " (s)"
                                self.add_table_column(col_header, freqs, avg=True)
        else:
            try:
                index1 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker One"], get_index=True)
                index2 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], get_index=True)
            except KeyError:
                if self.plot_objects:
                    QtGui.QMessageBox.about(self, "Error", "Add markers to %s set baseline region"
                                            % self.current_selected)

            try:
                for folder in checked.keys():
                    current_df = self.model.data[folder]
                    for key in checked[folder].keys():
                        if key in self.model.vr_headers[folder]:
                            for sweep in checked[folder][key]:
                                time_array = current_df['voltage recording']['Time'][sweep].values
                                data = current_df['voltage recording'][key][sweep]

                            if index1 < index2:
                                sub_time_array = time_array[index1:index2]
                                sub_data = data[index1:index2]
                            elif index2 < index1:
                                sub_time_array = time_array[index2:index1]
                                sub_data = data[index2:index1]
                            else:
                                QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\n"
                                                                       "Set baseline region with markers")

                            indexes = pace.detect_peaks(sub_data.values, mph=self.min_height, mpd=100)

                            real_index = sub_data.index[indexes].tolist()
                            indexes_list.append(real_index)

                            if self.hz_radio.isChecked():
                                unit = "Hz"
                                times, freqs = pace.calc_frequency(sub_time_array, indexes)

                                times_list.append(times)
                                freqs_list.append(freqs)

                                col_header = ("Analysis %s:" % self.analysis_counter) + " " + sweep + " (Hz)"
                                self.add_table_column(col_header, freqs, avg=True)
                            else:
                                unit = "ISI (s)"
                                times, freqs = pace.calc_frequency(sub_time_array, indexes, hz=False)

                                times_list.append(times)
                                freqs_list.append(freqs)

                                col_header = ("Analysis %s:" % self.analysis_counter) + " " + sweep + " (s)"
                                self.add_table_column(col_header, freqs, avg=True)

            except (KeyError, UnboundLocalError):
                pass

        return times_list, freqs_list, indexes_list, unit

    def run_analysis(self):
        times_list, freqs_list, indexes_list, unit = self.get_freq_vals()

        if len(times_list) > 0:
            if self.spike_plot_check.isChecked():
                name = "Plot" + str(self.counter)
                title = name + " - Detected spikes"
                plt = self.plotWidget.addPlot(row=self.counter, col=0, name=name, title=title)
                plt.setXLink(self.current_x_link)

                self.curves[name] = self.plot_data(plt)
                self.add_analysis_plot(plt, name)

                for i, curve in enumerate(self.curves[name]):
                    data = curve.getData()
                    x = data[0]
                    y = data[1]
                    plt.plot(x[indexes_list[i]], y[indexes_list[i]], pen=None, symbolBrush=pg.mkColor('r'),
                             symbolPen=pg.mkPen('r'), symbol="d")

            if self.freq_plot_check.isChecked():
                curves = []
                name = "Plot" + str(self.counter)
                title = name + " - Frequency vs. Time"
                plt = self.plotWidget.addPlot(row=self.counter, col=0, name=name, title=title)
                plt.setXLink(self.current_x_link)

                for i in range(len(times_list)):
                    curve = plt.plot(times_list[i], freqs_list[i], pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                    curves.append(curve)

                self.curves[name] = curves
                self.add_analysis_plot(plt, name)

                plt.setLabel('left', unit)

        self.analysis_counter += 1

