__author__ = 'Dan'

import pyqtgraph as pg
import pandas as pd
from PyQt4 import QtGui, QtCore
from ..extra_mods.EphysTools import synaptics as syn
from ..extra_mods.EphysTools import utilities as util
from .AnalysisWidget import AnalysisWidget


class PPRWidget(AnalysisWidget):

    def __init__(self, model):
        super().__init__(model)
        self.setWindowTitle("Paired-Pulse Ratio")

        self.bsl_start = 0.0
        self.bsl_end = 0.0
        self.stim_start = 0.0
        self.stim_interval = 0.0
        self.peak_sign = "min"

        headers = ["Peak 1", "Peak 2", "PPR"]

        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(headers)

        self.setup_groupbox()

    def setup_groupbox(self):
        layout = QtGui.QVBoxLayout(self.analysis_groupbox)
        sub_layout = QtGui.QHBoxLayout()

        radio_layout = QtGui.QHBoxLayout()
        radio_label = QtGui.QLabel("Peak direction: ")
        self.min_radio = QtGui.QRadioButton("Min")
        self.min_radio.setChecked(True)
        self.max_radio = QtGui.QRadioButton("Max")
        radio_layout.addWidget(radio_label)
        radio_layout.addWidget(self.min_radio)
        radio_layout.addWidget(self.max_radio)
        radio_layout.addStretch()

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

        stim_start_layout = QtGui.QHBoxLayout()
        stim_start_label = QtGui.QLabel("Stimulus start (s):")
        self.stim_start_txt = QtGui.QLineEdit("0.0")
        self.stim_start_txt.setMaximumSize(QtCore.QSize(40, 25))
        stim_start_layout.addWidget(stim_start_label)
        stim_start_layout.addWidget(self.stim_start_txt)
        stim_start_layout.addStretch()

        stim_interval_layout = QtGui.QHBoxLayout()
        stim_interval_label = QtGui.QLabel("Stimulus Interval (s):")
        self.stim_interval_txt = QtGui.QLineEdit("0.02")
        self.stim_interval_txt.setMaximumSize(QtCore.QSize(40, 25))
        stim_interval_layout.addWidget(stim_interval_label)
        stim_interval_layout.addWidget(self.stim_interval_txt)
        stim_interval_layout.addStretch()

        self.min_radio.clicked.connect(self.set_peak_sign)
        self.max_radio.clicked.connect(self.set_peak_sign)
        self.bsl_start_txt.editingFinished.connect(lambda: self.set_protocol_params(label="bsl_start"))
        self.bsl_end_txt.editingFinished.connect(lambda: self.set_protocol_params(label="bsl_end"))
        self.stim_start_txt.editingFinished.connect(lambda: self.set_protocol_params(label="stim_start"))
        self.stim_interval_txt.editingFinished.connect(lambda: self.set_protocol_params(label="stim_interval"))

        sub_layout.addStretch()
        sub_layout.addLayout(radio_layout)
        sub_layout.addLayout(bsl_start_layout)
        sub_layout.addLayout(bsl_end_layout)
        sub_layout.addLayout(stim_start_layout)
        sub_layout.addLayout(stim_interval_layout)
        sub_layout.addStretch()

        analysis_btn = QtGui.QPushButton("Run Analysis")
        analysis_btn.setMinimumWidth(200)
        analysis_btn.clicked.connect(self.run_analysis)
        self.plot_checkbox = QtGui.QCheckBox()
        self.plot_checkbox.setText("Plot PPR values")
        self.avg_checkbox = QtGui.QCheckBox()
        self.avg_checkbox.setText("Average sweeps first")
        self.avg_checkbox.stateChanged.connect(self.toggle_plot_check)

        btn_layout = QtGui.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(analysis_btn)
        btn_layout.addWidget(self.plot_checkbox)
        btn_layout.addWidget(self.avg_checkbox)
        btn_layout.addStretch()

        layout.addLayout(sub_layout)
        layout.addLayout(btn_layout)

    def set_peak_sign(self):
        if self.min_radio.isChecked():
            self.peak_sign = "min"
        else:
            self.peak_sign = "max"

    def toggle_plot_check(self):
        if self.avg_checkbox.isChecked():
            self.plot_checkbox.setDisabled(True)
        else:
            self.plot_checkbox.setDisabled(False)

    def set_protocol_params(self, label):
        try:
            if label == "bsl_start":
                self.bsl_start = float(self.bsl_start_txt.text())
            elif label == "bsl_end":
                self.bsl_end = float(self.bsl_end_txt.text())
            elif label == "stim_start":
                self.stim_start = float(self.stim_start_txt.text())
            elif label == "stim_interval":
                self.stim_interval = float(self.stim_interval_txt.text())
        except ValueError:
            QtGui.QMessageBox.about(self, "Error", "Must enter a numeric value")

    def run_analysis(self):
        checked = self.model.checked_dict
        #sweep_list = []
        df_list = []
        folder_list = []
        """
        for folder in checked.keys():
            current_df = self.model.data[folder]
            for key in checked[folder].keys():
                    if key in self.model.vr_headers[folder]:
                        for sweep in checked[folder][key]:
                            df_list.append(current_df['voltage recording'].ix[sweep])
                            sweep_list.append(sweep)
        """

        for folder in checked.keys():
            current_df = self.model.data[folder]
            key = list(checked[folder].keys())[0]
            sweeps = checked[folder][key]
            df_list.append(current_df['voltage recording'].ix[sweeps])
            folder_list.append(folder)

        new_df = pd.concat(df_list, keys=folder_list)
        grouped = new_df.groupby(level="Sweep")
        data_bsl = grouped.apply(util.baseline, self.bsl_start, self.bsl_end)

        if self.avg_checkbox.isChecked():
            avg_data = data_bsl.groupby(level=2).mean()
            print(avg_data)

            ppr_df = syn.calc_ppr(avg_data, self.stim_start, self.stim_interval, sign=self.peak_sign)

            row_vals = [ppr_df["Peak 1"].values[0], ppr_df["Peak 2"].values[0], ppr_df["PPR"].values[0]]
            row_header = ("Analysis %s:" % self.analysis_counter) + " Average"
            self.add_table_row(row_header, row_vals)

        else:
            grouped_bsl = data_bsl.groupby(level=[0, 1])
            ppr_df = grouped_bsl.apply(syn.calc_ppr, self.stim_start, self.stim_interval, self.peak_sign)

            for folder in checked.keys():
                key = list(checked[folder].keys())[0]
                sweeps = checked[folder][key]

                for sweep in sweeps:
                    peak1 = ppr_df["Peak 1"].ix[folder].ix[sweep].values[0]
                    peak2 = ppr_df["Peak 2"].ix[folder].ix[sweep].values[0]
                    ppr = ppr_df["PPR"].ix[folder].ix[sweep].values[0]

                    row_vals = [peak1, peak2, ppr]
                    row_header = ("Analysis %s:" % self.analysis_counter) + " " + sweep
                    self.add_table_row(row_header, row_vals)

            peak1_avg = ppr_df["Peak 1"].mean()
            peak2_avg = ppr_df["Peak 2"].mean()
            ppr_avg = ppr_df["PPR"].mean()

            row_vals = [peak1_avg, peak2_avg, ppr_avg]
            row_header = ("Analysis %s:" % self.analysis_counter) + " Average"
            self.add_table_row(row_header, row_vals)

            if self.plot_checkbox.isChecked():
                name = "Plot" + str(self.counter)
                title = name + " - PPR Values"
                plt = self.plotWidget.addPlot(row=self.counter, col=0, name=name, title=title)
                x = list(range(1, len(ppr_df["PPR"])+1))
                self.curves[name] = [plt.plot(x, ppr_df["PPR"].tolist(), pen=None, symbol='o'), ]
                plt.setLabel('left', "Ra (MOhm)")

                self.add_analysis_plot(plt, name, add_to_curves=False)

        self.analysis_counter += 1
