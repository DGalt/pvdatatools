__author__ = 'Dan'

from PyQt4 import QtCore, QtGui
import pyqtgraph.exporters as exporters
import pandas as pd


def waiting_effects(function):
    def new_function(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        function(self)
        QtGui.QApplication.restoreOverrideCursor()
    return new_function


class ExportDialog(QtGui.QDialog):
    def __init__(self, parent=None, current_focus=None):
        super().__init__(parent)
        self.setWindowTitle("Export")
        self.resize(160, 250)

        self.current_focus = current_focus

        self.exporter = None

        layout = QtGui.QVBoxLayout(self)

        self.copy_data_btn = QtGui.QPushButton("Copy Plot Data")
        self.copy_data_btn.clicked.connect(self.copy_data)

        self.to_csv_btn = QtGui.QPushButton("Export Plot Data")
        self.to_csv_btn.clicked.connect(self.save_to_csv)

        self.copy_plot_btn = QtGui.QPushButton("Copy Plot")
        self.copy_plot_btn.clicked.connect(self.copy_plot)

        self.export_plot_btn = QtGui.QPushButton("Export as Image")
        self.export_plot_btn.clicked.connect(self.export_plot)

        self.export_svg_btn = QtGui.QPushButton("Export as SVG")
        self.export_svg_btn.clicked.connect(self.export_svg)

        layout.addWidget(self.copy_data_btn)
        layout.addWidget(self.to_csv_btn)
        layout.addWidget(self.copy_plot_btn)
        layout.addWidget(self.export_plot_btn)
        layout.addWidget(self.export_svg_btn)

    @waiting_effects
    def copy_data(self):
        all_series = []
        counter = 1
        try:
            item = self.current_focus.plot_objects[self.current_focus.current_selected]
            if any(item.curves):
                for curve in item.curves:
                    data = curve.getData()
                    x = pd.Series(data[0], name="x" + str(counter).zfill(4))
                    y = pd.Series(data[1], name='y' + str(counter).zfill(4))

                    all_series.append(x)
                    all_series.append(y)

                    counter += 1

                df = pd.concat(all_series, axis=1)
                df.to_clipboard(index=False)
        except (AttributeError, KeyError):
            pass

    def save_to_csv(self):
        try:
            item = self.current_focus.plot_objects[self.current_focus.current_selected]
            filename = QtGui.QFileDialog.getSaveFileName(filter="Comma Delimited (*.csv)")
            if filename:
                try:
                    self.exporter = exporters.CSVExporter.CSVExporter(item)
                    self.exporter.export(filename)
                except (ValueError, TypeError):
                    QtGui.QMessageBox.about(self, "Error", "No data in in plot to export")
        except (AttributeError, KeyError):
            pass

    def copy_plot(self):
        try:
            item = self.current_focus.plot_objects[self.current_focus.current_selected]
            self.exporter = exporters.ImageExporter.ImageExporter(item)
            self.exporter.export(copy=True)
        except (AttributeError, KeyError):
            pass

    def export_plot(self):
        try:
            item = self.current_focus.plot_objects[self.current_focus.current_selected]
            filter_list = ["*."+bytes(f).decode('utf-8')+";;" for f in QtGui.QImageWriter.supportedImageFormats()]
            preferred = ["*.png;;", "*.tif;;", "*.jpg;;"]
            for p in (reversed(preferred)):
                if p in filter_list:
                    filter_list.remove(p)
                    filter_list.insert(0, p)

            file_filter = "".join(filter_list)
            filename = QtGui.QFileDialog.getSaveFileName(filter=file_filter)

            if filename:
                self.exporter = exporters.ImageExporter.ImageExporter(item)
                self.exporter.export(filename)

        except (AttributeError, KeyError):
            pass

    def export_svg(self):
        try:
            item = self.current_focus.plot_objects[self.current_focus.current_selected]
            filename = QtGui.QFileDialog.getSaveFileName(filter="Scalable Vector Graphics (*.svg)")

            self.exporter = exporters.SVGExporter.SVGExporter(item)

            if filename:
                self.exporter.export(filename)
        except (AttributeError, KeyError):
            pass
