__author__ = 'Dan'

import numpy as np
from PyQt4 import QtGui
from .AnalysisWidget import AnalysisWidget
import pyqtgraph as pg


class PhasePlotWidget(AnalysisWidget):

    def __init__(self, model):
        super().__init__(model)
        self.setWindowTitle("Phase Plot")
        self.tab_widget.tabBar().setVisible(False)

        self.setup_groupbox()

    def setup_groupbox(self):
        layout = QtGui.QHBoxLayout(self.analysis_groupbox)

        #radio_layout = QtGui.QVBoxLayout()
        self.full_radio = QtGui.QRadioButton("Entire sweep")
        self.full_radio.setChecked(True)
        self.subregion_radio = QtGui.QRadioButton("Subregion with markers")
        #radio_layout.addWidget(full_radio)
        #radio_layout.addWidget(subregion_radio)

        phaseplot_btn = QtGui.QPushButton("Create Phase Plot")
        phaseplot_btn.setMinimumWidth(200)
        phaseplot_btn.clicked.connect(self.plot_phaseplot)

        layout.addStretch()
        layout.addWidget(self.full_radio)
        layout.addWidget(self.subregion_radio)
        layout.addWidget(phaseplot_btn)
        layout.addStretch()

    def get_phaseplot_vals(self):
        y_data = []
        x_data = []
        checked = self.model.checked_dict

        if self.full_radio.isChecked():
            for folder in checked.keys():
                current_df = self.model.data[folder]
                for key in checked[folder].keys():
                    if key in self.model.vr_headers[folder]:
                        for sweep in checked[folder][key]:
                            data = current_df['voltage recording'][key][sweep].values
                            diff = np.diff(data)

                            x_data.append(data[1:])
                            y_data.append(diff)

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
                                data = current_df['voltage recording'][key][sweep].values

                            if index1 < index2:
                                sub_data = data[index1:index2]
                            elif index2 < index1:
                                sub_data = data[index2:index1]
                            else:
                                QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\nSet baseline region with markers")

                            diff = np.diff(sub_data)
                            y_data.append(diff)
                            x_data.append(sub_data[1:])

            except (KeyError, UnboundLocalError):
                pass

        return x_data, y_data

    def plot_phaseplot(self):
        curves = []
        x_data, y_data = self.get_phaseplot_vals()

        if len(x_data) > 0:
            name = "Plot" + str(self.counter)
            title = name + " - Phase Plot"
            plt = self.plotWidget.addPlot(row=self.counter, col=0, name=name, title=title)
            for i in range(len(x_data)):
                curve = plt.plot(x_data[i], y_data[i], pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                curves.append(curve)

            self.curves[name] = curves
            self.add_analysis_plot(plt, name)

if __name__ == '__main__':
    import sys
    from Model import Model
    app = QtGui.QApplication(sys.argv)
    ex = AnalysisWidget(Model())
    ex.show()
    sys.exit(app.exec_())