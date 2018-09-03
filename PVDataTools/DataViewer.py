__author__ = 'Dan'

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import sys
from .extra_mods.PrairieAnalysis import pv_import as pvi
from .extra_mods.EphysTools import utilities as util


class DataViewer(QtGui.QWidget):
    update_plotLists = QtCore.pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("Data Viewer")
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.plotWidget = pg.GraphicsLayoutWidget(self)
        self.plotWidget.setObjectName("plotWidget")
        self.plotWidget.scene().sigMouseClicked.connect(self.onClick)

        plot_tab = QtGui.QWidget()
        self.plot_layout = QtGui.QVBoxLayout(plot_tab)
        self.plot_layout.addWidget(self.plotWidget)
        self.plot_layout.addLayout(self.create_plot_buttons_layout(self))

        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.addTab(plot_tab, "Plot")
        self.tab_widget.tabBar().setVisible(False)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.tab_widget)

        self.model = model
        self.df = None
        self.sweeps = []
        self.plot_index_list = []
        self.counter = 1
        self.curves = {}
        self.axis2_curves = {}
        self.current_curve_index = {}
        self.plot_objects = {}
        self.current_selected = 'Plot1'
        self.current_x_link = 'Plot1'
        self.selected_curve = {}
        self.plot_markers = {}
        self.plot_marker_labels = {}
        self.extra_axes = {}
        self.dbl_click = False

    def create_plot_buttons_layout(self, form):
        text_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

        self.plot_btns_layout = QtGui.QHBoxLayout()
        self.plot_btns_layout.setObjectName("plot_btns_layout")

        self.center_markers_btn = QtGui.QPushButton("Center Markers", form)
        self.center_markers_btn.setObjectName("center_markers_btn")
        self.center_markers_btn.clicked.connect(self.center_markers)

        self.baseline_btn = QtGui.QPushButton("Baseline Plot", form)
        self.baseline_btn.setObjectName("baseline_btn")
        self.baseline_btn.clicked.connect(self.baseline_plot)

        self.average_btn = QtGui.QPushButton("Average and:", form)
        self.average_btn.setObjectName("average_btn")
        self.average_btn.clicked.connect(self.average_plots)

        self.avg_option_dropdown = QtGui.QComboBox(form)
        self.avg_option_dropdown.setObjectName("avg_option_dropdown")
        self.avg_option_dropdown.addItem("Clear Plot")
        self.avg_option_dropdown.addItem("Create New Plot")
        self.avg_option_dropdown.addItem("Add to Current Plot")

        self.auto_axis_btn = QtGui.QPushButton("Auto All Plots", form)
        self.auto_axis_btn.setObjectName("auto_axis_btn")
        self.auto_axis_btn.clicked.connect(self.auto_all_plots)

        self.smoothing_btn = QtGui.QPushButton("Smooth:")
        self.smoothing_btn.clicked.connect(self.smooth_data)
        self.smoothing_text = QtGui.QLineEdit("1")
        self.smoothing_text.setSizePolicy(text_size_policy)
        self.smoothing_text.setMaximumSize(QtCore.QSize(50, 25))

        self.region_avg_btn = QtGui.QPushButton("Region Average:")
        self.region_avg_btn.clicked.connect(self.get_region_average)
        self.region_avg_text = QtGui.QTextBrowser()
        self.region_avg_text.setSizePolicy(text_size_policy)
        self.region_avg_text.setMaximumSize(QtCore.QSize(75, 25))

        self.plot_btns_layout.addWidget(self.auto_axis_btn)
        self.plot_btns_layout.addWidget(self.center_markers_btn)
        self.plot_btns_layout.addWidget(self.baseline_btn)
        self.plot_btns_layout.addWidget(self.average_btn)
        self.plot_btns_layout.addWidget(self.avg_option_dropdown)
        self.plot_btns_layout.addWidget(self.smoothing_btn)
        self.plot_btns_layout.addWidget(self.smoothing_text)
        self.plot_btns_layout.addWidget(self.region_avg_btn)
        self.plot_btns_layout.addWidget(self.region_avg_text)

        return self.plot_btns_layout

    def plot_data(self, plt, curves=None):
        checked = self.model.checked_dict
        if curves is None:
            curves = []

        for folder in checked.keys():
            current_df = self.model.data[folder]

            for key in checked[folder].keys():
                if key in self.model.vr_headers[folder]:
                    for sweep in checked[folder][key]:
                        x = current_df['voltage recording']['Time'][sweep]
                        y = current_df['voltage recording'][key][sweep]
                        curve = plt.plot(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                        curves.append(curve)

                elif key in self.model.ls_headers[folder]:
                    for sweep in checked[folder][key]:
                        x = current_df['linescan'][key + ' Time'][sweep]
                        y = current_df['linescan'][key][sweep]
                        curve = plt.plot(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                        curves.append(curve)

                channel = list(checked[folder])[0]
                if folder in self.model.ls_headers.keys():
                    if channel in self.model.ls_headers[folder]:
                        plt.setLabel('left', channel)
                        plt.setLabel('bottom', 'Time (s)')
                else:
                    if channel == 'Primary':
                        label = channel + ' (' + current_df['file attributes']['File1']['primary']['unit'] + ')'
                    elif key == 'Secondary':
                        label = channel + ' (' + current_df['file attributes']['File1']['secondary']['unit'] + ')'
                    else:
                        label = channel + ' (V)'
                    plt.setLabel('left', label)
                    plt.setLabel('bottom', 'Time (s)')

            plt.autoRange()

        return curves

    def add_new_plot(self, average_plot=False, ratio_plot=False):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        name = "Plot" + str(self.counter)
        plt = self.plotWidget.addPlot(row=self.counter, col=0, name=name, title=name)
        plt.setXLink(self.current_x_link)
        self.plot_objects[name] = plt
        self.axis2_curves[name] = []

        self.current_curve_index[name] = 0
        self.counter += 1

        if average_plot:
            x_data, y_data = self.get_average_data()

            if x_data is None and y_data is None:
                self.curves[name] = None
                self.clear_plot(name)
                self.counter -= 1
                self.update_plotLists.emit()
            else:
                self.curves[name] = [plt.plot(x_data, y_data), ]
                self.update_plotLists.emit()
                try:
                    self.curves[name][0].setPen(pg.mkPen('r'))
                    self.selected_curve[name] = self.curves[name][0]
                except IndexError:
                    pass

        elif ratio_plot:
            self.curves[name] = self.plot_ratio(plt)

            if self.curves[name] == "error":
                self.clear_plot(name)
                self.counter -= 1
                self.update_plotLists.emit()
            else:
                try:
                    self.curves[name][0].setPen(pg.mkPen('b'))
                    self.selected_curve[name] = self.curves[name][0]
                except IndexError:
                    pass

        else:
            self.curves[name] = self.plot_data(plt)

            try:
                self.curves[name][0].setPen(pg.mkPen('b'))
                self.selected_curve[name] = self.curves[name][0]
            except IndexError:
                pass

        if len(self.plot_objects) > 1 and self.current_selected == "Plot1":
            self.plot_objects["Plot1"].setTitle("Plot1 - SELECTED")

        QtGui.QApplication.restoreOverrideCursor()

    def add_to_plot(self, new_axis=False):
        name = self.model.current_name
        try:
            plt = self.plot_objects[name]
            if new_axis:
                self.create_new_axis(plt, name)

            else:
                if any(self.curves[name]):
                    self.plot_data(plt, curves=self.curves[name])
                else:
                    self.curves[name] = self.plot_data(plt)
                    self.selected_curve[name] = self.curves[name][0]
                    self.selected_curve[name].setPen('b')
        except KeyError:
            pass
        except IndexError:
            pass

    def create_new_axis(self, plt, name, ratio=False):
        if name in self.extra_axes.keys():
            QtGui.QMessageBox.about(self, "Error %s" % self.current_selected,
                                        "Limited to one additional axis per plot")

        else:
            new_vb = pg.ViewBox()
            self.extra_axes[name] = new_vb
            plt.showAxis('right')
            plt.scene().addItem(new_vb)
            plt.getAxis('right').linkToView(new_vb)
            new_vb.setXLink(plt)

            def updateViews(plt, new_vb):
                new_vb.setGeometry(plt.vb.sceneBoundingRect())
                new_vb.linkedViewChanged(plt.vb, new_vb.XAxis)

            updateViews(plt, new_vb)
            plt.vb.sigResized.connect(lambda: updateViews(plt, new_vb))

            if ratio:
                self.axis2_curves[name], label = self.plot_ratio_new_axis(new_vb)
            else:
                self.axis2_curves[name], label = self.plot_data_new_axis(new_vb)

            plt.getAxis('right').setLabel(label)
            try:
                self.axis2_curves[name][0].setPen(pg.hsvColor(0.8, sat=1.0, val=0.8, alpha=1.0))
            except IndexError:
                pass

    def plot_data_new_axis(self, new_vb):
        checked = self.model.checked_dict
        curves = []
        label = ""
        for folder in checked.keys():
            current_df = self.model.data[folder]

            for key in checked[folder].keys():
                if key in self.model.vr_headers[folder]:
                    for sweep in checked[folder][key]:
                        x = current_df['voltage recording']['Time'][sweep]
                        y = current_df['voltage recording'][key][sweep]
                        curve = pg.PlotDataItem(x, y, pen=pg.hsvColor(0.8, sat=1.0, val=0.8, alpha=0.08))
                        new_vb.addItem(curve)

                        curves.append(curve)

                elif key in self.model.ls_headers[folder]:
                    for sweep in checked[folder][key]:
                        x = current_df['linescan'][key + ' Time'][sweep]
                        y = current_df['linescan'][key][sweep]
                        curve = pg.PlotDataItem(x, y, pen=pg.hsvColor(0.8, sat=1.0, val=0.8, alpha=0.08))
                        new_vb.addItem(curve)

                        curves.append(curve)

                channel = list(checked[folder])[0]
                if channel in self.model.ls_headers[folder]:
                    label = channel
                else:
                    if channel == 'Primary':
                        label = channel + ' (' + current_df['file attributes']['File1']['primary']['unit'] + ')'
                    elif key == 'Secondary':
                        label = channel + ' (' + current_df['file attributes']['File1']['secondary']['unit'] + ')'
                    else:
                        label = channel + ' (V)'

        new_vb.autoRange()

        return curves, label

    def clear_plot(self, name=None):
        if name is None:
            name = self.model.current_name

        if name == "All" or len(self.plot_objects) == 1:
            self.plotWidget.clear()
            self.curves = {}
            self.current_curve_index = {}
            self.plot_objects = {}
            self.plot_markers = {}
            self.plot_marker_labels = {}
            self.current_selected = "Plot1"
            self.counter = 1

            for item in self.extra_axes.values():
                item.clear()

            self.extra_axes = {}

        elif name:
            self.plotWidget.removeItem(self.plot_objects[name])
            self.plot_objects[name].setXLink("")

            if name in self.curves.keys():
                del self.curves[name]
            del self.current_curve_index[name]
            del self.plot_objects[name]

            if name == self.current_x_link and self.plot_objects:

                self.current_x_link = sorted(self.plot_objects.keys())[0]
                for plt in self.plot_objects.values():
                    plt.setXLink(self.current_x_link)

            if name == self.current_selected and self.plot_objects:
                self.current_selected = sorted(self.plot_objects.keys())[0]
                self.plot_objects[self.current_selected].setTitle(self.current_selected + " - SELECTED")

            if name in self.plot_markers.keys():

                del self.plot_markers[name]
                del self.plot_marker_labels[name]

            if name in self.extra_axes.keys():
                self.extra_axes[name].setXLink("")
                self.extra_axes[name].clear()
                del self.extra_axes[name]

    def create_marker_pair(self, plt, name):
            x_range = (plt.viewRange()[0][0]+plt.viewRange()[0][1])

            marker_one = plt.addLine(x=x_range/2, pen=pg.mkPen('g', width=2.0), movable=True)
            marker_two = plt.addLine(x=x_range/2, pen=pg.mkPen('g', width=2.0), movable=True)

            try:
                marker_one_vals = self.get_marker_vals(marker_one)
                marker_two_vals = self.get_marker_vals(marker_two)

            except KeyError as error:
                print("KeyError: " + str(error))

            label_one = pg.TextItem()
            label_one_x = marker_one.getXPos()
            label_one_y = plt.viewRange()[1][1]
            label_one.setPos(label_one_x, label_one_y)
            try:
                label_one.setText("Marker One\n[%0.3f, %0.3f]" % (marker_one_vals[0], marker_one_vals[1]), color='k')
            except TypeError:
                label_one.setText("Marker One", color='k')
            plt.addItem(label_one)

            label_two = pg.TextItem()
            label_two_x = marker_two.getXPos()
            label_two_y = plt.viewRange()[1][1]
            label_two.setPos(label_two_x, label_two_y)
            try:
                label_two.setText("Marker Two\n[%0.3f, %0.3f]" % (marker_two_vals[0], marker_two_vals[1]), color='k')
            except TypeError:
                label_two.setText("Marker Two", color='k')
            plt.addItem(label_two)

            marker_one.sigDragged.connect(lambda: self.update_marker_vals(marker_one, "Marker One", label_one))
            marker_two.sigDragged.connect(lambda: self.update_marker_vals(marker_two, "Marker Two", label_two))

            self.plot_marker_labels[name] = {"Label One": label_one, "Label Two": label_two}

            return marker_one, marker_two

    def add_marker(self):
        name = self.model.current_name

        if name == "All":
            for plot_name in sorted(self.plot_objects.keys()):
                if plot_name not in self.plot_markers.keys():
                    plt = self.plot_objects[plot_name]
                    marker_one, marker_two = self.create_marker_pair(plt, plot_name)

                    self.plot_markers[plot_name] = {"Marker One": marker_one, "Marker Two": marker_two}

        elif name:
            if name not in self.plot_markers.keys():
                plt = self.plot_objects[name]
                marker_one, marker_two = self.create_marker_pair(plt, name)
                self.plot_markers[name] = {"Marker One": marker_one, "Marker Two": marker_two}

    def get_marker_vals(self, marker, get_index=False):
        plt = marker.parentItem().parentItem().parentItem()
        plot_name = list(self.plot_objects.keys())[list(self.plot_objects.values()).index(plt)]

        try:
            sampling_divisor = self.selected_curve[plot_name].getData()[0][1] - \
                               self.selected_curve[plot_name].getData()[0][0]

            index = int(marker.getXPos() / sampling_divisor)

            if 0 <= index <= len(self.selected_curve[plot_name].getData()[0])-1:
                x_val = self.selected_curve[plot_name].getData()[0][index]
                y_val = self.selected_curve[plot_name].getData()[1][index]
            else:
                x_val = marker.getXPos()
                y_val = 0

            if get_index:
                return index
            else:
                return x_val, y_val

        except KeyError:
            x_val = marker.getXPos()
            y_val = 0
            return x_val, y_val

    def update_marker_vals(self, marker, marker_num, label):
        plt = marker.parentItem().parentItem().parentItem()
        y_range = plt.viewRange()[1][1]
        x_val, y_val = self.get_marker_vals(marker)

        if marker_num == "Marker One":
            #print(x_val, y_val)
            label.setPos(x_val, y_range)
            label.setText("Marker One\n[%0.3f, %0.3f]" % (x_val, y_val), color='k')

        elif marker_num == "Marker Two":
            #print(x_val, y_val)
            label.setPos(x_val, y_range)
            label.setText("Marker Two\n[%0.3f, %0.3f]" % (x_val, y_val), color='k')

    def calc_marker_diff(self):
        selected_plot_a = self.model.selected_plot_a
        selected_plot_b = self.model.selected_plot_b
        selected_marker_a = self.model.selected_marker_a
        selected_marker_b = self.model.selected_marker_b
        try:
            x_val_a, y_val_a = self.get_marker_vals(self.plot_markers[selected_plot_a][selected_marker_a])
            x_val_b, y_val_b = self.get_marker_vals(self.plot_markers[selected_plot_b][selected_marker_b])

            x_diff = x_val_a - x_val_b
            y_diff = y_val_a - y_val_b
        except KeyError as e:
            #print("KeyError: " + str(e))
            x_diff = "NA"
            y_diff = "NA"

        return x_diff, y_diff

    def clear_markers(self):
        name = self.model.current_name

        if name == "All":
            for plot_name, plt in self.plot_objects.items():
                try:
                    plt.removeItem(self.plot_markers[plot_name]["Marker One"])
                    plt.removeItem(self.plot_markers[plot_name]["Marker Two"])
                    plt.removeItem(self.plot_marker_labels[plot_name]["Label One"])
                    plt.removeItem(self.plot_marker_labels[plot_name]["Label Two"])

                    del self.plot_markers[plot_name]
                    del self.plot_marker_labels[plot_name]

                except KeyError:
                    pass

        elif name:
            try:
                plt = self.plot_objects[name]
                plt.removeItem(self.plot_markers[name]["Marker One"])
                plt.removeItem(self.plot_markers[name]["Marker Two"])
                plt.removeItem(self.plot_marker_labels[name]["Label One"])
                plt.removeItem(self.plot_marker_labels[name]["Label Two"])

                del self.plot_markers[name]
                del self.plot_marker_labels[name]

            except KeyError:
                pass

    def plot_ratio(self, plt, curves=None):
        checked = self.model.checked_dict

        if curves is None:
                curves = []

        for folder in checked.keys():
            current_df = self.model.data[folder]

            if self.model.profile_ratio:
                profile_a = self.model.profile_a
                profile_b = self.model.profile_b
                label = profile_a + '/' + profile_b

                try:
                    if len(checked[folder][profile_a]) != len(checked[folder][profile_b]):
                        QtGui.QMessageBox.about(self, "Error",
                                                "Number of selected sweeps must be equal for each profile")
                        return "error"
                    else:
                        for sweep in checked[folder][profile_a]:
                            x = current_df['linescan'][profile_a + ' Time'][sweep]
                            y = current_df['linescan'][profile_a][sweep] / current_df['linescan'][profile_b][sweep]
                            curve = plt.plot(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                            curves.append(curve)
                except KeyError as e:
                    QtGui.QMessageBox.about(self, "Error", "No sweeps for %s selected" % e)
                    return "error"

            else:
                label = 'F/F0'

                if self.model.f0_from_txt:
                    try:
                        f0 = float(self.model.f0_txt)
                        if self.model.f0_eq1:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = (current_df['linescan'][key][sweep] - f0) / f0
                                        curve = plt.plot(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        curves.append(curve)
                        else:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = current_df['linescan'][key][sweep] / f0
                                        curve = plt.plot(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        curves.append(curve)
                    except ValueError:
                        QtGui.QMessageBox.about(self, "Error", "F0 must be a numeric value")
                        return "error"
                else:
                    try:
                        index1 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker One"],
                                                      get_index=True)
                        index2 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker Two"],
                                                      get_index=True)

                        if self.model.f0_eq1:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        if index1 < index2:
                                            f0 = current_df['linescan'][key][sweep][index1:index2].mean()
                                        elif index2 < index1:
                                            f0 = current_df['linescan'][key][sweep][index2:index1].mean()
                                        else:
                                            print(index1, index2)
                                            QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\n"
                                                                    "Set baseline region with markers")
                                            return "error"

                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = (current_df['linescan'][key][sweep] - f0) / f0
                                        curve = plt.plot(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        curves.append(curve)
                        else:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        if index1 < index2:
                                            f0 = current_df['linescan'][key][sweep][index1:index2].mean()
                                        elif index2 < index1:
                                            f0 = current_df['linescan'][key][sweep][index2:index1].mean()
                                        else:
                                            QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\n"
                                                                    "Set baseline region with markers")
                                            return "error"

                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = current_df['linescan'][key][sweep] / f0
                                        curve = plt.plot(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        curves.append(curve)
                    except KeyError:
                        QtGui.QMessageBox.about(self, "Error", "Add markers to %s to set F0 region"
                                                % self.current_selected)
                        return "error"

        plt.setLabel('left', label)
        plt.setLabel('bottom', 'Time (s)')
        plt.autoRange()

        return curves

    def plot_ratio_new_axis(self, new_vb):
        checked = self.model.checked_dict

        curves = []
        label = ""

        for folder in checked.keys():
            current_df = self.model.data[folder]

            if self.model.profile_ratio:
                profile_a = self.model.profile_a
                profile_b = self.model.profile_b
                label = profile_a + '/' + profile_b

                try:
                    if len(checked[folder][profile_a]) != len(checked[folder][profile_b]):
                        QtGui.QMessageBox.about(self, "Error",
                                                "Number of selected sweeps must be equal for each profile")
                        return "error"
                    else:
                        for sweep in checked[folder][profile_a]:
                            x = current_df['linescan'][profile_a + ' Time'][sweep]
                            y = current_df['linescan'][profile_a][sweep] / current_df['linescan'][profile_b][sweep]
                            curve = pg.PlotDataItem(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                            new_vb.addItem(curve)
                            curves.append(curve)
                except KeyError as e:
                    QtGui.QMessageBox.about(self, "Error", "No sweeps for %s selected" % e)
                    return "error"

            else:
                label = 'F/F0'

                if self.model.f0_from_txt:
                    try:
                        f0 = float(self.model.f0_txt)
                        if self.model.f0_eq1:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = (current_df['linescan'][key][sweep] - f0) / f0
                                        curve = pg.PlotDataItem(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        new_vb.addItem(curve)
                                        curves.append(curve)
                        else:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = current_df['linescan'][key][sweep] / f0
                                        curve = pg.PlotDataItem(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        new_vb.addItem(curve)
                                        curves.append(curve)
                    except ValueError:
                        QtGui.QMessageBox.about(self, "Error", "F0 must be a numeric value")
                        return "error"
                else:
                    try:
                        index1 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker One"],
                                                      get_index=True)
                        index2 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker Two"],
                                                      get_index=True)

                        if self.model.f0_eq1:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        if index1 < index2:
                                            f0 = current_df['linescan'][key][sweep][index1:index2].mean()
                                        elif index2 < index1:
                                            f0 = current_df['linescan'][key][sweep][index2:index1].mean()
                                        else:
                                            print(index1, index2)
                                            QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\n"
                                                                    "Set baseline region with markers")
                                            return "error"

                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = (current_df['linescan'][key][sweep] - f0) / f0
                                        curve = pg.PlotDataItem(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        new_vb.addItem(curve)
                                        curves.append(curve)
                        else:
                            for key in checked[folder].keys():
                                if key in self.model.ls_headers[folder]:
                                    for sweep in checked[folder][key]:
                                        if index1 < index2:
                                            f0 = current_df['linescan'][key][sweep][index1:index2].mean()
                                        elif index2 < index1:
                                            f0 = current_df['linescan'][key][sweep][index2:index1].mean()
                                        else:
                                            QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\n"
                                                                    "Set baseline region with markers")
                                            return "error"

                                        x = current_df['linescan'][key + ' Time'][sweep]
                                        y = current_df['linescan'][key][sweep] / f0
                                        curve = pg.PlotDataItem(x, y, pen=pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                                        new_vb.addItem(curve)
                                        curves.append(curve)
                    except KeyError:
                        QtGui.QMessageBox.about(self, "Error", "Add markers to %s to set F0 region"
                                                % self.current_selected)
                        return "error"

        new_vb.autoRange()

        return curves, label

    def add_ratio_to_plot(self, new_axis=False):
        try:
            name = self.model.current_name
            plt = self.plot_objects[name]

            if new_axis:
                self.create_new_axis(plt, name, ratio=True)

            else:
                if any(self.curves[name]):
                    self.plot_ratio(plt, curves=self.curves[name])

                else:
                    curves = self.plot_ratio(plt)
                    if curves != "error":
                        self.curves[name] = curves
                        self.selected_curve[name] = self.curves[name][0]
        except KeyError:
            pass
        except IndexError:
            pass

    def smooth_data(self):
        try:
            smooth_factor = int(self.smoothing_text.text())
            for curve in self.curves[self.current_selected]:
                data = curve.getData()
                y_smoothed = util.simple_smoothing(data[1], smooth_factor)

                curve.setData(x=data[0], y=y_smoothed)

            self.plot_objects[self.current_selected].autoRange()

            if self.current_selected in self.plot_markers.keys():
                self.update_marker_vals(self.plot_markers[self.current_selected]["Marker One"], "Marker One",
                                        self.plot_marker_labels[self.current_selected]["Label One"])
                self.update_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], "Marker Two",
                                        self.plot_marker_labels[self.current_selected]["Label Two"])

        except ValueError:
            QtGui.QMessageBox.about(self, "Error", "Must enter a numeric value")
        except KeyError:
            pass

    def subtract_constant(self):
        try:
            constant = float(self.model.constant)
            for curve in self.curves[self.current_selected]:
                data = curve.getData()
                curve.setData(x=data[0], y=data[1]-constant)

            self.plot_objects[self.current_selected].autoRange()

            if self.current_selected in self.plot_markers.keys():
                self.update_marker_vals(self.plot_markers[self.current_selected]["Marker One"], "Marker One",
                                        self.plot_marker_labels[self.current_selected]["Label One"])
                self.update_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], "Marker Two",
                                        self.plot_marker_labels[self.current_selected]["Label Two"])
        except ValueError:
            QtGui.QMessageBox.about(self, "Error", "Must enter a numeric value")
        except KeyError:
            pass

    def center_markers(self):
        try:
            plt = self.plot_objects[self.current_selected]
            x_range = (plt.viewRange()[0][0]+plt.viewRange()[0][1])
            self.plot_markers[self.current_selected]["Marker One"].setValue(x_range/2)
            self.plot_markers[self.current_selected]["Marker Two"].setValue(x_range/2)
            self.update_marker_vals(self.plot_markers[self.current_selected]["Marker One"], "Marker One",
                                    self.plot_marker_labels[self.current_selected]["Label One"])
            self.update_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], "Marker Two",
                                    self.plot_marker_labels[self.current_selected]["Label Two"])
        except KeyError:
            pass

    def baseline_plot(self):
        try:
            index1 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker One"], get_index=True)
            index2 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], get_index=True)
        except KeyError:
            if self.plot_objects:
                QtGui.QMessageBox.about(self, "Error", "Add markers to %s set baseline region"
                                        % self.current_selected)
        try:
            for curve in self.curves[self.current_selected]:
                data = curve.getData()
                if index1 < index2:
                    mean = data[1][index1:index2].mean()
                elif index2 < index1:
                    mean = data[1][index2:index1].mean()
                else:
                    QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\nSet baseline region with markers")
                    mean = 0
                curve.setData(x=data[0], y=data[1]-mean)

            self.plot_objects[self.current_selected].autoRange()
            self.update_marker_vals(self.plot_markers[self.current_selected]["Marker One"], "Marker One",
                                    self.plot_marker_labels[self.current_selected]["Label One"])
            self.update_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], "Marker Two",
                                    self.plot_marker_labels[self.current_selected]["Label Two"])
        except (KeyError, UnboundLocalError):
            pass

    def get_average_data(self):
        all_y_data = []

        try:
            for curve in self.curves[self.current_selected]:
                data = curve.getData()
                all_y_data.append(data[1])

            y_data_array = np.array(all_y_data)
            y_mean = y_data_array.mean(axis=0)

            return data[0], y_mean

        except KeyError:
            return None, None

    def average_plots(self):
        choice_index = self.avg_option_dropdown.currentIndex()
        try:
            if any(self.curves[self.current_selected]):
                if choice_index == 0:
                    x_data, y_data = self.get_average_data()
                    self.plot_objects[self.current_selected].clearPlots()
                    curve = self.plot_objects[self.current_selected].plot(x=x_data, y=y_data, pen=pg.mkPen('r'))
                    self.curves[self.current_selected] = [curve, ]

                elif choice_index == 1:
                    self.add_new_plot(average_plot=True)

                elif choice_index == 2:
                    x_data, y_data = self.get_average_data()
                    self.selected_curve[self.current_selected].setPen(pg.hsvColor(0.0, sat=0.0, val=0.5, alpha=0.08))
                    curve = self.plot_objects[self.current_selected].plot(x=x_data, y=y_data, pen=pg.mkPen('r'))
                    self.curves[self.current_selected] = [curve, ]
        except KeyError:
            pass

    def auto_all_plots(self):
        for plt in self.plot_objects.values():
            plt.autoRange()

            if self.current_selected in self.plot_markers.keys():
                self.update_marker_vals(self.plot_markers[self.current_selected]["Marker One"], "Marker One",
                                        self.plot_marker_labels[self.current_selected]["Label One"])
                self.update_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], "Marker Two",
                                        self.plot_marker_labels[self.current_selected]["Label Two"])

    def get_region_average(self):
        try:
            index1 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker One"], get_index=True)
            index2 = self.get_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], get_index=True)
        except KeyError:
            if self.plot_objects:
                QtGui.QMessageBox.about(self, "Error", "Add markers to %s To select region"
                                        % self.current_selected)

        try:
            data = self.selected_curve[self.current_selected].getData()
            if index1 < index2:
                mean = data[1][index1:index2].mean()
            elif index2 < index1:
                mean = data[1][index2:index1].mean()
            else:
                QtGui.QMessageBox.about(self, "Error", "Baseline region is 0\nSet baseline region with markers")
                mean = 0

            self.region_avg_text.setText("%0.3f" % mean)

        except (KeyError, UnboundLocalError):
            pass

    def keyPressEvent(self, event):
        key = event.key()

        try:
            all_curves = self.curves[self.current_selected] + self.axis2_curves[self.current_selected]
            selected_index = self.current_curve_index[self.current_selected]

            if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_Left:
                try:
                    if selected_index-1 >= 0:
                        new_selected_curve = all_curves[selected_index-1]

                        if new_selected_curve in self.curves[self.current_selected]:
                            new_selected_curve.setPen(pg.mkPen('b'))

                        elif new_selected_curve in self.axis2_curves[self.current_selected]:
                            new_selected_curve.setPen(pg.hsvColor(0.8, sat=1.0, val=0.8, alpha=1.0))

                        if self.selected_curve[self.current_selected] in self.curves[self.current_selected]:
                            self.selected_curve[self.current_selected].setPen(pg.hsvColor(0.0, sat=0.0, val=0.5,
                                                                                          alpha=0.08))

                        elif self.selected_curve[self.current_selected] in self.axis2_curves[self.current_selected]:
                            self.selected_curve[self.current_selected].setPen(pg.hsvColor(0.8, sat=1.0, val=0.8,
                                                                                          alpha=0.08))
                        #if new_selected_curve == self.curves[self.current_selected][-1]:
                            #self.axis2_curves[self.current_selected][0].setPen(pg.hsvColor(0.8, sat=1.0, val=0.8, alpha=1.0))

                        self.selected_curve[self.current_selected] = new_selected_curve
                        self.current_curve_index[self.current_selected] -= 1
                except IndexError:
                    pass

                try:
                    self.update_marker_vals(self.plot_markers[self.current_selected]["Marker One"], "Marker One",
                                            self.plot_marker_labels[self.current_selected]["Label One"])
                    self.update_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], "Marker Two",
                                            self.plot_marker_labels[self.current_selected]["Label Two"])
                except KeyError:
                    pass

            elif key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_Right:
                try:
                    if selected_index+1 < len(all_curves):
                        new_selected_curve = all_curves[selected_index+1]

                        if new_selected_curve in self.curves[self.current_selected]:
                            new_selected_curve.setPen(pg.mkPen('b'))

                        elif new_selected_curve in self.axis2_curves[self.current_selected]:
                            new_selected_curve.setPen(pg.hsvColor(0.8, sat=1.0, val=0.8, alpha=1.0))

                        if self.selected_curve[self.current_selected] in self.curves[self.current_selected]:
                            self.selected_curve[self.current_selected].setPen(pg.hsvColor(0.0, sat=0.0, val=0.5,
                                                                                      alpha=0.08))

                        elif self.selected_curve[self.current_selected] in self.axis2_curves[self.current_selected]:
                            self.selected_curve[self.current_selected].setPen(pen=pg.hsvColor(0.8, sat=1.0, val=0.8,
                                                                                              alpha=0.08))
                        #if new_selected_curve == self.axis2_curves[self.current_selected][0]:
                            #self.curves[self.current_selected][-1].setPen(pg.mkPen('b'))

                        self.selected_curve[self.current_selected] = new_selected_curve
                        self.current_curve_index[self.current_selected] += 1
                except IndexError:
                    pass

                try:
                    self.update_marker_vals(self.plot_markers[self.current_selected]["Marker One"], "Marker One",
                                            self.plot_marker_labels[self.current_selected]["Label One"])
                    self.update_marker_vals(self.plot_markers[self.current_selected]["Marker Two"], "Marker Two",
                                            self.plot_marker_labels[self.current_selected]["Label Two"])
                except KeyError:
                    pass

        except KeyError:
            pass

    def onClick(self, event):
        if event.double():
            items = self.plotWidget.scene().items(event.scenePos())
            plot_item = [x for x in items if isinstance(x, pg.PlotItem)]
            try:
                name = list(self.plot_objects.keys())[list(self.plot_objects.values()).index(plot_item[0])]
                plot_item[0].setTitle(name + " - SELECTED")
            except IndexError:
                name = self.current_selected
            try:
                self.plot_objects[self.current_selected].setTitle(self.current_selected)
            except KeyError:
                pass
            self.current_selected = name

if __name__ == '__main__':
    from Model import Model
    app = QtGui.QApplication(sys.argv)
    ex = DataViewer(Model())
    ex.show()
    sys.exit(app.exec_())
