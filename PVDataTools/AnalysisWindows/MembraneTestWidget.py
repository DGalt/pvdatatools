__author__ = 'Dan'

from PyQt4 import QtGui, QtCore
from extra_mods.EphysTools import membrane
from AnalysisWindows.AnalysisWidget import AnalysisWidget
import pyqtgraph as pg


class MembraneTestWidget(AnalysisWidget):

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        self.setWindowTitle("Membrane Test")

        headers = ["Ra (MOhm)", "Rm (MOhm)", "Cm (pF)", "tau (ms)"]
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(headers)

        self.setup_groupbox()

        self.bsl_start = 0.0
        self.bsl_end = 0.0
        self.pulse_start = 0.0
        self.pulse_dur = 0.0
        self.pulse_amp = 0.0

    def setup_groupbox(self):
        layout = QtGui.QVBoxLayout(self.analysis_groupbox)
        sub_layout = QtGui.QHBoxLayout()

        bsl_start_layout = QtGui.QHBoxLayout()
        bsl_start_label = QtGui.QLabel("Baseline start (s):")
        self.bsl_start_txt = QtGui.QLineEdit("0.0")
        self.bsl_start_txt.setMaximumSize(QtCore.QSize(40, 25))
        bsl_start_layout.addWidget(bsl_start_label)
        bsl_start_layout.addWidget(self.bsl_start_txt)
        bsl_start_layout.addStretch()

        bsl_end_layout = QtGui.QHBoxLayout()
        bsl_end_label = QtGui.QLabel("Baseline end (s):")
        self.bsl_end_txt = QtGui.QLineEdit("0.0")
        self.bsl_end_txt.setMaximumSize(QtCore.QSize(40, 25))
        bsl_end_layout.addWidget(bsl_end_label)
        bsl_end_layout.addWidget(self.bsl_end_txt)
        bsl_end_layout.addStretch()

        pulse_start_layout = QtGui.QHBoxLayout()
        pulse_start_label = QtGui.QLabel("Pulse start (s):")
        self.pulse_start_txt = QtGui.QLineEdit("0.0")
        self.pulse_start_txt.setMaximumSize(QtCore.QSize(40, 25))
        pulse_start_layout.addWidget(pulse_start_label)
        pulse_start_layout.addWidget(self.pulse_start_txt)
        pulse_start_layout.addStretch()

        pulse_dur_layout = QtGui.QHBoxLayout()
        pulse_dur_label = QtGui.QLabel("Pulse duration (s):")
        self.pulse_dur_txt = QtGui.QLineEdit("0.0")
        self.pulse_dur_txt.setMaximumSize(QtCore.QSize(40, 25))
        pulse_dur_layout.addWidget(pulse_dur_label)
        pulse_dur_layout.addWidget(self.pulse_dur_txt)
        pulse_dur_layout.addStretch()

        pulse_amp_layout = QtGui.QHBoxLayout()
        pulse_amp_label = QtGui.QLabel("Pulse Amplitude (mV):")
        self.pulse_amp_txt = QtGui.QLineEdit("0.0")
        self.pulse_amp_txt.setMaximumSize(QtCore.QSize(40, 25))
        pulse_amp_layout.addWidget(pulse_amp_label)
        pulse_amp_layout.addWidget(self.pulse_amp_txt)
        pulse_amp_layout.addStretch()

        self.bsl_start_txt.editingFinished.connect(lambda: self.set_protocol_params(label="bsl_start"))
        self.bsl_end_txt.editingFinished.connect(lambda: self.set_protocol_params(label="bsl_end"))
        self.pulse_start_txt.editingFinished.connect(lambda: self.set_protocol_params(label="pulse_start"))
        self.pulse_dur_txt.editingFinished.connect(lambda: self.set_protocol_params(label="pulse_dur"))
        self.pulse_amp_txt.editingFinished.connect(lambda: self.set_protocol_params(label="pulse_amp"))

        sub_layout.addStretch()
        sub_layout.addLayout(bsl_start_layout)
        sub_layout.addLayout(bsl_end_layout)
        sub_layout.addLayout(pulse_start_layout)
        sub_layout.addLayout(pulse_dur_layout)
        sub_layout.addLayout(pulse_amp_layout)
        sub_layout.addStretch()

        analysis_btn = QtGui.QPushButton("Run Analysis")
        analysis_btn.setMinimumWidth(200)
        analysis_btn.clicked.connect(self.run_analysis)
        self.plot_checkbox = QtGui.QCheckBox()
        self.plot_checkbox.setText("Plot Ra values")

        btn_layout = QtGui.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(analysis_btn)
        btn_layout.addWidget(self.plot_checkbox)
        btn_layout.addStretch()

        layout.addLayout(sub_layout)
        layout.addLayout(btn_layout)

    def set_protocol_params(self, label):
        try:
            if label == "bsl_start":
                self.bsl_start = float(self.bsl_start_txt.text())
            elif label == "bsl_end":
                self.bsl_end = float(self.bsl_end_txt.text())
            elif label == "pulse_start":
                self.pulse_start = float(self.pulse_start_txt.text())
            elif label == "pulse_dur":
                self.pulse_dur = float(self.pulse_dur_txt.text())
            elif label == "pulse_amp":
                self.pulse_amp = float(self.pulse_amp_txt.text())
        except ValueError:
            QtGui.QMessageBox.about(self, "Error", "Must enter a numeric value")

    def run_analysis(self):
        checked = self.model.checked_dict
        ra_list = []
        for folder in checked.keys():
            current_df = self.model.data[folder]
            for key in checked[folder].keys():
                    if key in self.model.vr_headers[folder]:
                        for sweep in checked[folder][key]:
                            mem_vals = membrane.calc_membrane_properties(current_df['voltage recording'].ix[sweep],
                                                                         self.bsl_start, self.bsl_end,
                                                                         self.pulse_start, self.pulse_dur,
                                                                         self.pulse_amp)
                            row_header = ("Analysis %s:" % self.analysis_counter) + " " + sweep
                            self.add_table_row(row_header, mem_vals)
                            ra_list.append(mem_vals[0])

        if self.plot_checkbox.isChecked():
            name = "Plot" + str(self.counter)
            title = name + " - Ra Values"
            plt = self.plotWidget.addPlot(row=self.counter, col=0, name=name, title=title)
            x = list(range(1, len(ra_list)+1))
            self.curves[name] = [plt.plot(x, ra_list, pen=None, symbol='o'), ]
            plt.setLabel('left', "Ra (MOhm)")

            self.add_analysis_plot(plt, name, add_to_curves=False)

        self.analysis_counter += 1
