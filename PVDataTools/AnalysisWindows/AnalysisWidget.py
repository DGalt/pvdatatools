__author__ = 'Daniel'

import numpy as np
from PyQt4 import QtGui
from DataViewer import DataViewer
import pyqtgraph as pg


class AnalysisWidget(DataViewer):

    def __init__(self, model):
        super().__init__(model)

        self.model = model

        self.table_widget = QtGui.QTableWidget()
        self.table_widget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.tab_widget.addTab(self.table_widget, "Output")
        self.tab_widget.tabBar().setVisible(True)
        #self.tab_widget.setTabPosition(3)
        self.tab_widget.currentChanged.connect(self.toggle_groupbox)

        self.analysis_groupbox = QtGui.QGroupBox(self)
        #self.setup_groupbox()

        self.layout.addWidget(self.analysis_groupbox)

        self.analysis_counter = 1

    def setup_groupbox(self):
        raise Exception("Abstract method must be overridden in subclass.")

    def toggle_groupbox(self, index):
        if index == 0:
            self.analysis_groupbox.show()
        else:
            self.analysis_groupbox.hide()

    def add_table_column(self, column_header, values, avg=False):
        num_col = self.table_widget.columnCount()
        num_row = self.table_widget.rowCount()
        self.table_widget.insertColumn(num_col)
        self.table_widget.setHorizontalHeaderItem(num_col, QtGui.QTableWidgetItem(column_header))

        if avg:
            avg_val = values.mean()
            values = np.insert(values, 0, avg_val)

            if num_row < len(values):
                self.table_widget.setRowCount(len(values))

            for i in range(self.table_widget.rowCount()):
                self.table_widget.setVerticalHeaderItem((i+1), QtGui.QTableWidgetItem("%s" % (i+1)))

            if self.table_widget.verticalHeaderItem(0) != "Average":
                self.table_widget.setVerticalHeaderItem(0, QtGui.QTableWidgetItem("Average"))

        else:
            if num_row < len(values):
                self.table_widget.setRowCount(len(values))

        for i, val in enumerate(values):
            item = QtGui.QTableWidgetItem("%0.3f" % val)
            self.table_widget.setItem(i, num_col, item)



    def add_table_row(self, row_header, values):
        num_col = self.table_widget.columnCount()
        num_row = self.table_widget.rowCount()
        self.table_widget.insertRow(num_row)
        self.table_widget.setVerticalHeaderItem(num_row, QtGui.QTableWidgetItem(row_header))

        if num_col < len(values):
            self.table_widget.setColumnCount(len(values))

        for i, val in enumerate(values):
            item = QtGui.QTableWidgetItem("%0.3f" % val)
            self.table_widget.setItem(num_row, i, item)

    def plot_analysis_data(self):
        raise Exception("Abstract method must be overridden in subclass.")

    def add_analysis_plot(self, plt, name, add_to_curves=True):
        self.plot_objects[name] = plt
        self.axis2_curves[name] = []

        self.current_curve_index[name] = 0
        self.counter += 1

        if len(self.plot_objects) > 1 and self.current_selected == "Plot1":
            self.plot_objects["Plot1"].setTitle("Plot1 - SELECTED")

        if add_to_curves:
            try:
                self.curves[name][0].setPen(pg.mkPen('b'))
                self.selected_curve[name] = self.curves[name][0]
            except IndexError:
                pass

        self.update_plotLists.emit()

if __name__ == '__main__':
    import sys
    from Model import Model
    app = QtGui.QApplication(sys.argv)
    ex = AnalysisWidget(Model())
    ex.show()
    sys.exit(app.exec_())

