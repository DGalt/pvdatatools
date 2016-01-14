__author__ = 'Dan'

from PyQt4 import QtCore, QtGui
import sys
import os


class FilePlotController(QtGui.QWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        desktop = QtGui.QDesktopWidget()
        width = desktop.screenGeometry().width()
        ratio = width / 1920

        self.current_focus = None

        self.tree_widget = QtGui.QTreeWidget(self)
        self.tree_widget.headerItem().setText(0, "Data Files")
        self.tree_widget.itemChanged.connect(self.update_checked_dict)
        self.tree_widget.setMaximumWidth(230*ratio)

        self.tab_widget = QtGui.QTabWidget(self)
        tab_widget_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.tab_widget.setSizePolicy(tab_widget_size_policy)
        self.tab_widget.setMinimumSize(QtCore.QSize(230*ratio, 210))
        self.tab_widget.setMaximumWidth(230*ratio)

        self.tab_widget.addTab(self.create_import_and_plot_tab(), "Plot")
        self.tab_widget.addTab(self.create_markers_tab(), "Markers")
        self.tab_widget.addTab(self.create_profiles_tab(), "Profiles")
        #self.tabWidget.setTabEnabled(2, False)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.tab_widget)

    def create_import_and_plot_tab(self):
        self.Import_and_Plot_tab = QtGui.QWidget()
        self.Import_and_Plot_tab.setObjectName("Import_and_Plot_tab")

        import_plot_layout = QtGui.QVBoxLayout(self.Import_and_Plot_tab)
        import_plot_layout.setObjectName("import_plot_layout")

        clearChecked_btn = QtGui.QPushButton("Clear Check Boxes")
        clearChecked_btn.setObjectName("clearChecked_btn")
        clearChecked_btn.clicked.connect(self.clear_checked)

        self.createPlot_btn = QtGui.QPushButton("New Plot")
        self.createPlot_btn.setObjectName("createPlot_btn")

        self.addToPlot_btn = QtGui.QPushButton("Add plot to:")
        self.addToPlot_btn.setObjectName("addToPlot_btn_btn")

        self.plotNum_dropdown = QtGui.QComboBox()
        self.plotNum_dropdown.setObjectName("plotNum_dropdown")

        self.plot_new_axis_box = QtGui.QCheckBox()
        self.plot_new_axis_box.setText("Create axis")

        add_plot_axis_layout = QtGui.QVBoxLayout()
        add_plot_axis_layout.addWidget(self.plotNum_dropdown)
        add_plot_axis_layout.addWidget(self.plot_new_axis_box)

        self.clearPlot_dropdown = QtGui.QComboBox()
        self.clearPlot_dropdown.setObjectName("clearPlot_dropdown")
        self.clearPlot_dropdown.addItem("All")

        addPlotLayout = QtGui.QHBoxLayout()
        addPlotLayout.setObjectName("addPlotLayout")
        addPlotLayout.addWidget(self.addToPlot_btn)
        addPlotLayout.addLayout(add_plot_axis_layout)

        self.clearPlot_btn = QtGui.QPushButton("Clear:")
        self.clearPlot_btn.setObjectName("clearPlot_btn")

        clearPlotLayout = QtGui.QHBoxLayout()
        clearPlotLayout.setObjectName("clearPlotLayout")
        clearPlotLayout.addWidget(self.clearPlot_btn)
        clearPlotLayout.addWidget(self.clearPlot_dropdown)

        import_plot_layout.addWidget(clearChecked_btn)
        import_plot_layout.addWidget(self.createPlot_btn)
        import_plot_layout.addLayout(addPlotLayout)
        import_plot_layout.addLayout(clearPlotLayout)

        return self.Import_and_Plot_tab

    def create_markers_tab(self):
        self.Markers_tab = QtGui.QWidget()
        self.Markers_tab.setObjectName("Markers_tab")

        self.markers_tab_layout = QtGui.QVBoxLayout(self.Markers_tab)
        self.markers_tab_layout.setObjectName("markers_tab_layout")

        self.markers_top_half_layout = QtGui.QHBoxLayout()
        self.markers_top_half_layout.setObjectName("markers_top_half_layout")

        self.markers_add_clear_layout = QtGui.QVBoxLayout()
        self.markers_add_clear_layout.setObjectName("markers_add_clear_layout")

        self.markers_dropdown_layout = QtGui.QVBoxLayout()
        self.markers_dropdown_layout.setObjectName("markers_dropdown_layout)")

        self.addMarker_btn = QtGui.QPushButton("Add Markers")
        self.addMarker_btn.setObjectName("addMarker_btn")

        self.clearMarker_btn = QtGui.QPushButton("Clear Markers")
        self.clearMarker_btn.setObjectName("clearMarker_btn")

        self.markersPlot_dropdown = QtGui.QComboBox()
        self.markersPlot_dropdown.setObjectName("markersPlot_dropdown")
        self.markersPlot_dropdown.addItem("All")

        self.markers_add_clear_layout.addWidget(self.addMarker_btn)
        self.markers_add_clear_layout.addWidget(self.clearMarker_btn)
        self.markers_dropdown_layout.addWidget(self.markersPlot_dropdown)

        self.markers_top_half_layout.addLayout(self.markers_add_clear_layout)
        self.markers_top_half_layout.addLayout(self.markers_dropdown_layout)

        self.marker_line = QtGui.QFrame()
        self.marker_line.setFrameShape(QtGui.QFrame.HLine)
        self.marker_line.setFrameShadow(QtGui.QFrame.Sunken)
        self.marker_line.setObjectName("marker_line")

        self.markerCalc_btn = QtGui.QPushButton("Calculate Difference")
        self.markerCalc_btn.setObjectName("marker_calc_button")

        self.markers_bottom_half_layout = QtGui.QHBoxLayout()
        self.markers_bottom_col_one = QtGui.QVBoxLayout()
        self.markers_bottom_col_two = QtGui.QVBoxLayout()

        self.calc_plot_dropdown1 = QtGui.QComboBox()
        self.calc_plot_dropdown2 = QtGui.QComboBox()
        self.calc_marker_dropdown1 = QtGui.QComboBox()
        self.calc_marker_dropdown2 = QtGui.QComboBox()

        self.markers_bottom_col_one.addWidget(self.calc_plot_dropdown1)
        self.markers_bottom_col_one.addWidget(self.calc_marker_dropdown1)
        self.markers_bottom_col_two.addWidget(self.calc_plot_dropdown2)
        self.markers_bottom_col_two.addWidget(self.calc_marker_dropdown2)

        self.markers_bottom_half_layout.addLayout(self.markers_bottom_col_one)
        self.markers_bottom_half_layout.addLayout(self.markers_bottom_col_two)

        self.output_layout = QtGui.QHBoxLayout()
        self.x_label = QtGui.QLabel()
        self.x_label.setText("X: ")
        self.y_label = QtGui.QLabel()
        self.y_label.setText("Y: ")

        self.x_text = QtGui.QTextBrowser()
        self.y_text = QtGui.QTextBrowser()

        text_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.x_text.setSizePolicy(text_size_policy)
        self.x_text.setMaximumSize(QtCore.QSize(95, 25))
        self.y_text.setSizePolicy(text_size_policy)
        self.y_text.setMaximumSize(QtCore.QSize(95, 25))

        self.output_layout.addWidget(self.x_label)
        self.output_layout.addWidget(self.x_text)
        self.output_layout.addWidget(self.y_label)
        self.output_layout.addWidget(self.y_text)

        self.markers_tab_layout.addLayout(self.markers_top_half_layout)
        self.markers_tab_layout.addWidget(self.marker_line)
        self.markers_tab_layout.addWidget(self.markerCalc_btn)
        self.markers_tab_layout.addLayout(self.markers_bottom_half_layout)
        self.markers_tab_layout.addLayout(self.output_layout)

        return self.Markers_tab

    def create_profiles_tab(self):
        self.Profiles_tab = QtGui.QWidget()
        self.Profiles_tab.setObjectName("Ratio_tab")

        self.profiles_tab_layout = QtGui.QVBoxLayout(self.Profiles_tab)

        text_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

        self.profile_label = QtGui.QLabel()
        self.profile_label.setText("Currently selected: ")
        self.profile_label.setMaximumSize(QtCore.QSize(220, 15))

        self.back_subtract_layout = QtGui.QHBoxLayout()

        self.back_subtract_btn = QtGui.QPushButton("Subtract constant: ")
        self.back_subtract_text = QtGui.QLineEdit("0.0")
        self.back_subtract_text.setSizePolicy(text_size_policy)
        self.back_subtract_text.setMaximumSize(QtCore.QSize(75, 25))

        self.back_subtract_layout.addWidget(self.back_subtract_btn)
        self.back_subtract_layout.addWidget(self.back_subtract_text)

        self.profile_line = QtGui.QFrame()
        self.profile_line.setFrameShape(QtGui.QFrame.HLine)
        self.profile_line.setFrameShadow(QtGui.QFrame.Sunken)
        self.profile_line.setObjectName("marker_line")

        self.ratio_selection_dropdown = QtGui.QComboBox()
        self.ratio_selection_dropdown.setEditable(True)
        self.ratio_selection_dropdown.lineEdit().setReadOnly(True)
        self.ratio_selection_dropdown.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.ratio_selection_dropdown.addItems(["Ratio Profiles", "Ratio F/F0"])
        self.ratio_selection_dropdown.currentIndexChanged.connect(self.switch_ratio_layout)

        self.ratio_add_layout = QtGui.QHBoxLayout()
        self.ratio_add_layout.setObjectName("ratio_add_to_plot_layout")

        self.new_ratio_btn = QtGui.QPushButton("New Plot")

        self.add_ratio_to_plot_btn = QtGui.QPushButton("Add to: ")

        self.plotNum_ratio_dropdown = QtGui.QComboBox()
        self.plotNum_ratio_dropdown.setObjectName("plotNum_ratio_dropdown")

        self.ratio_new_axis_box = QtGui.QCheckBox()
        self.ratio_new_axis_box.setText("Create \naxis")

        add_ratio_axis_layout = QtGui.QVBoxLayout()
        add_ratio_axis_layout.addWidget(self.plotNum_ratio_dropdown)
        add_ratio_axis_layout.addWidget(self.ratio_new_axis_box)

        self.ratio_add_layout.addWidget(self.new_ratio_btn)
        self.ratio_add_layout.addWidget(self.add_ratio_to_plot_btn)
        self.ratio_add_layout.addLayout(add_ratio_axis_layout)

        self.profiles_tab_layout.addWidget(self.profile_label)
        self.profiles_tab_layout.addLayout(self.back_subtract_layout)
        self.profiles_tab_layout.addWidget(self.profile_line)
        self.profiles_tab_layout.addWidget(self.ratio_selection_dropdown)
        self.profiles_tab_layout.addLayout(self.create_profile_ratio_layout())
        self.profiles_tab_layout.addLayout(self.ratio_add_layout)

        return self.Profiles_tab

    def create_profile_ratio_layout(self):
        self.profile_ratio_layout = QtGui.QHBoxLayout()

        self.ratio_dropdown1 = QtGui.QComboBox()
        self.ratio_dropdown2 = QtGui.QComboBox()

        self.profile_ratio_layout.addWidget(self.ratio_dropdown1)
        self.profile_ratio_layout.addWidget(self.ratio_dropdown2)

        return self.profile_ratio_layout

    def create_f0_ratio_layout(self):
        self.f0_ratio_layout = QtGui.QVBoxLayout()

        text_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

        self.f0_value_groupbox = QtGui.QGroupBox()
        self.f0_equation_groupbox = QtGui.QGroupBox()

        self.f0_value_layout = QtGui.QHBoxLayout(self.f0_value_groupbox)

        self.f0_markers_radio = QtGui.QRadioButton("F0 Markers", self.f0_value_groupbox)
        self.f0_input_radio = QtGui.QRadioButton("F0 =", self.f0_value_groupbox)
        self.f0_input_radio.setChecked(True)
        self.f0_input_radio.setSizePolicy(text_size_policy)
        self.f0_input_radio.setMaximumSize(QtCore.QSize(40, 25))

        self.f0_text = QtGui.QLineEdit("1", self.f0_value_groupbox)
        self.f0_text.setSizePolicy(text_size_policy)
        self.f0_text.setMaximumSize(QtCore.QSize(50, 25))

        self.f0_value_layout.addWidget(self.f0_input_radio)
        self.f0_value_layout.addWidget(self.f0_text)
        self.f0_value_layout.addWidget(self.f0_markers_radio)

        self.f0_equation_layout = QtGui.QHBoxLayout(self.f0_equation_groupbox)

        self.f0_eq1_radio = QtGui.QRadioButton("(F-F0)/F0", self.f0_equation_groupbox)
        self.f0_eq1_radio.setChecked(True)
        self.f0_eq2_radio = QtGui.QRadioButton("F/F0", self.f0_equation_groupbox)

        self.f0_equation_layout.addWidget(self.f0_eq1_radio)
        self.f0_equation_layout.addWidget(self.f0_eq2_radio)

        self.f0_ratio_layout.addWidget(self.f0_value_groupbox)
        self.f0_ratio_layout.addWidget(self.f0_equation_groupbox)

        return self.f0_ratio_layout

    def update_focus(self, subwindow):
        """Updates focus to current active window in the main application's MdiArea. Also changes comboboxes
        to show correct plot numbers for the window selected, and connects the buttons in the UI to the appropriate
        slots for the current active window.

        If subwindow is None, comboboxes will basically reset to default and all buttons will be disconnected
        """

        self.current_focus = subwindow

        #have to wrap this in a try:except statement because if signal is not currently connected to any slots
        #then SIGNAL.disconnect() returns a TypeError. Might be better to check if SIGNAL is connected to anything
        #but I'm not sure how to do that
        try:
            self.createPlot_btn.clicked.disconnect()
            self.clearPlot_btn.clicked.disconnect()
            self.addToPlot_btn.clicked.disconnect()
            self.addMarker_btn.clicked.disconnect()
            self.clearMarker_btn.clicked.disconnect()
            self.markerCalc_btn.clicked.disconnect()
            self.back_subtract_btn.clicked.disconnect()
            self.new_ratio_btn.clicked.disconnect()
            self.add_ratio_to_plot_btn.disconnect()
            self.current_focus.update_plotLists.disconnect()
        except TypeError:
            pass

        if self.current_focus is not None:
            self.createPlot_btn.clicked.connect(self.add_new_plot)
            self.clearPlot_btn.clicked.connect(self.clear_plot)
            self.addToPlot_btn.clicked.connect(self.add_to_plot)
            self.addMarker_btn.clicked.connect(self.add_marker)
            self.clearMarker_btn.clicked.connect(self.clear_markers)
            self.markerCalc_btn.clicked.connect(self.calc_marker_diff)
            self.back_subtract_btn.clicked.connect(self.subtract_constant)
            self.new_ratio_btn.clicked.connect(self.add_new_ratio_plot)
            self.add_ratio_to_plot_btn.clicked.connect(self.add_ratio_to_plot)
            self.current_focus.update_plotLists.connect(self.update_dropdowns)

            self.update_dropdowns()

        else:
            self.plotNum_dropdown.clear()
            self.plotNum_ratio_dropdown.clear()
            self.clearPlot_dropdown.clear()
            self.markersPlot_dropdown.clear()
            self.calc_marker_dropdown1.clear()
            self.calc_marker_dropdown2.clear()
            self.calc_plot_dropdown1.clear()
            self.calc_plot_dropdown2.clear()
            self.x_text.clear()
            self.y_text.clear()

            self.clearPlot_dropdown.addItem("All")
            self.markersPlot_dropdown.addItem("All")

    def update_dropdowns(self):
        plot_list = sorted(self.current_focus.plot_objects.keys())

        self.plotNum_dropdown.clear()
        self.plotNum_dropdown.addItems(plot_list)

        self.plotNum_ratio_dropdown.clear()
        self.plotNum_ratio_dropdown.addItems(plot_list)

        self.clearPlot_dropdown.clear()
        self.clearPlot_dropdown.addItem("All")
        self.clearPlot_dropdown.addItems(plot_list)

        self.markersPlot_dropdown.clear()
        self.markersPlot_dropdown.addItem("All")
        self.markersPlot_dropdown.addItems(plot_list)

        self.calc_marker_dropdown1.clear()
        self.calc_marker_dropdown2.clear()
        self.calc_plot_dropdown1.clear()
        self.calc_plot_dropdown2.clear()
        self.x_text.clear()
        self.y_text.clear()

        marker_plot_list = sorted(self.current_focus.plot_markers.keys())
        if any(marker_plot_list):
            marker_list = ["Marker One", "Marker Two"]
            self.calc_marker_dropdown1.addItems(marker_list)
            self.calc_marker_dropdown2.addItems(marker_list)
            self.calc_marker_dropdown2.setCurrentIndex(1)

            self.calc_plot_dropdown1.addItems(marker_plot_list)
            self.calc_plot_dropdown2.addItems(marker_plot_list)

    def update_tree_widget(self):
        self.tree_widget.clear()
        self.model.checked_dict = {}

        for folder in sorted(self.model.data.keys()):
            folder_split = os.path.split(folder)
            child_folder = folder_split[1]
            parent_folder = os.path.split(folder_split[0])[1]
            folder = os.path.join(parent_folder, child_folder)

            grandparent_item = QtGui.QTreeWidgetItem(self.tree_widget)
            grandparent_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
            grandparent_item.setText(0, folder)

            all_headers = []

            if folder in self.model.vr_headers.keys():
                all_headers += self.model.vr_headers[folder]

            if folder in self.model.ls_headers.keys():
                all_headers += self.model.ls_headers[folder]

            for header in all_headers:
                parent_item = QtGui.QTreeWidgetItem(grandparent_item)
                parent_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                parent_item.setCheckState(0, QtCore.Qt.Unchecked)
                parent_item.setText(0, header)

                for sweep in self.model.sweeps[folder]:
                    child_item = QtGui.QTreeWidgetItem(parent_item)
                    child_item.setCheckState(0, QtCore.Qt.Unchecked)
                    child_item.setText(0, sweep)

    def update_checked_dict(self, item):
        if item.checkState(0) == QtCore.Qt.Unchecked:
            self.remove_from_checked_dict(item)

        else:
            self.add_to_checked_dict(item)

    def add_to_checked_dict(self, item):
        #If item has no children, then it is bottom of tree - i.e. it is a sweep
        #Since adding a parent (or grandparent) adds all children (or grandchildren), signals will be emitted not only
        #for that checkbox, but also the switching of all the children/grandchildren to checked.
        if item.childCount() == 0:
            folder = item.parent().parent().text(0)
            signal = item.parent().text(0)

            #if folder is in dict keys, then some child of folder is already in dict
            if folder in self.model.checked_dict.keys():
                #if signal is in the dictionary contained within folder, then a list of sweeps already exists, so just
                #need to append to that list
                if signal in self.model.checked_dict[folder].keys():
                    self.model.checked_dict[folder][signal].append(item.text(0))
                #otherwise need to create that list for that signal, with this sweep as the first item
                else:
                    self.model.checked_dict[folder][signal] = [item.text(0), ]

            #if folder is not in dict, then simply add the folder with the nested dictionary "signal" with sweep as the
            #first element in the list
            else:
                self.model.checked_dict[folder] = {signal: [item.text(0), ]}

    def remove_from_checked_dict(self, item):

        if self.model.checked_dict:
            if item.text(0) in self.model.checked_dict.keys():
                del self.model.checked_dict[item.text(0)]

            elif item.childCount() == 0:
                folder = item.parent().parent().text(0)
                signal = item.parent().text(0)
                self.model.checked_dict[folder][signal].remove(item.text(0))

            else:
                folder = item.parent().text(0)
                del self.model.checked_dict[folder][item.text(0)]

    def clear_checked(self):
        root = self.tree_widget.invisibleRootItem()
        folder_count = root.childCount()

        for i in range(folder_count):
            folder = root.child(i)

            folder.setCheckState(0, QtCore.Qt.Unchecked)
            """
                num_signal = folder.childCount()
                for n in range(num_signal):
                    signal = folder.child(i)
                    if signal.checkState(0) != QtCore.Qt.Unchecked:
                        signal.setCheckState(0, QtCore.Qt.Unchecked)

                        num_children = signal.childCount()
                        for m in range(num_children):
                            child = signal.child(m)
                            child.setCheckState(0, QtCore.Qt.Unchecked)
                            """

        self.model.checked = {}

    def switch_ratio_layout(self, index):
        if index == 0:
            for i in reversed(range(self.f0_ratio_layout.count())):
                self.f0_ratio_layout.itemAt(i).widget().setParent(None)
            self.profiles_tab_layout.removeItem(self.f0_ratio_layout)

            self.profiles_tab_layout.insertLayout(4, self.create_profile_ratio_layout())

            for profile in self.model.ls_headers:
                self.ratio_dropdown1.addItem(profile)
                self.ratio_dropdown2.addItem(profile)

        elif index == 1:
            for i in reversed(range(self.profile_ratio_layout.count())):
                self.profile_ratio_layout.itemAt(i).widget().setParent(None)
            self.profiles_tab_layout.removeItem(self.profile_ratio_layout)

            self.profiles_tab_layout.insertLayout(4, self.create_f0_ratio_layout())

    def add_new_plot(self):
        name = "Plot%s" % self.current_focus.counter

        self.plotNum_dropdown.addItem(name)
        self.plotNum_ratio_dropdown.addItem(name)
        self.clearPlot_dropdown.addItem(name)
        self.markersPlot_dropdown.addItem(name)

        self.current_focus.add_new_plot()

    def add_to_plot(self):
        self.model.current_name = self.plotNum_dropdown.currentText()

        if self.plot_new_axis_box.checkState() == QtCore.Qt.Checked:
            self.current_focus.add_to_plot(new_axis=True)
        else:
            self.current_focus.add_to_plot()

    def clear_plot(self):
        name = self.clearPlot_dropdown.currentText()
        index = self.clearPlot_dropdown.currentIndex()

        self.model.current_name = name
        self.current_focus.clear_plot()

        if name == "All":
            self.plotNum_dropdown.clear()
            self.plotNum_ratio_dropdown.clear()
            self.clearPlot_dropdown.clear()
            self.clearPlot_dropdown.addItem("All")
            self.markersPlot_dropdown.clear()
            self.markersPlot_dropdown.addItem("All")
            self.calc_plot_dropdown1.clear()
            self.calc_plot_dropdown2.clear()
            self.calc_marker_dropdown1.clear()
            self.calc_marker_dropdown2.clear()

        elif name:
            self.clearPlot_dropdown.removeItem(index)
            self.plotNum_dropdown.removeItem(index-1)
            self.plotNum_ratio_dropdown.removeItem(index-1)

            marker_index = self.markersPlot_dropdown.findText(name)
            self.markersPlot_dropdown.removeItem(marker_index)

            if name in self.current_focus.plot_markers.keys():
                calc_plot_index1 = self.calc_plot_dropdown1.findText(name)
                calc_plot_index2 = self.calc_plot_dropdown2.findText(name)
                self.calc_plot_dropdown1.removeItem(calc_plot_index1)
                self.calc_plot_dropdown2.removeItem(calc_plot_index2)

                if len(self.plot_markers) == 1:
                    self.calc_marker_dropdown1.clear()
                    self.calc_marker_dropdown2.clear()

    def add_marker(self):
        name = self.markersPlot_dropdown.currentText()

        self.model.current_name = name
        if self.calc_marker_dropdown1.count() < 2 and self.current_focus.plot_objects:
            marker_list = ["Marker One", "Marker Two"]
            self.calc_marker_dropdown1.addItems(marker_list)
            self.calc_marker_dropdown2.addItems(marker_list)
            self.calc_marker_dropdown2.setCurrentIndex(1)

        if name == "All":
            for plot_name in sorted(self.current_focus.plot_objects.keys()):
                if plot_name not in self.current_focus.plot_markers.keys():

                    self.calc_plot_dropdown1.addItem(plot_name)
                    self.calc_plot_dropdown2.addItem(plot_name)

        elif name:
            if name not in self.current_focus.plot_markers.keys():

                self.calc_plot_dropdown1.addItem(name)
                self.calc_plot_dropdown2.addItem(name)

        self.current_focus.add_marker()

    def clear_markers(self):
        name = self.markersPlot_dropdown.currentText()

        self.model.current_name = name
        self.current_focus.clear_markers()

        if name == "All":
            self.calc_plot_dropdown1.clear()
            self.calc_plot_dropdown2.clear()
            self.calc_marker_dropdown1.clear()
            self.calc_marker_dropdown2.clear()

        elif name:
            if len(self.current_focus.plot_markers) == 0:
                    self.calc_marker_dropdown1.clear()
                    self.calc_marker_dropdown2.clear()

            index1 = self.calc_plot_dropdown1.findText(name)
            index2 = self.calc_plot_dropdown2.findText(name)
            self.calc_plot_dropdown1.removeItem(index1)
            self.calc_plot_dropdown2.removeItem(index2)

    def calc_marker_diff(self):
        self.model.selected_plot_a = self.calc_plot_dropdown1.currentText()
        self.model.selected_plot_b = self.calc_plot_dropdown2.currentText()
        self.model.selected_marker_a = self.calc_marker_dropdown1.currentText()
        self.model.selected_marker_b = self.calc_marker_dropdown2.currentText()

        x_diff, y_diff = self.current_focus.calc_marker_diff()

        self.x_text.setText("%0.3f" % x_diff)
        self.y_text.setText("%0.3f" % y_diff)

    def subtract_constant(self):
        self.model.constant = self.back_subtract_text.text()

        self.current_focus.subtract_constant()

    def set_model_ratio_values(self):
        if self.ratio_selection_dropdown.currentIndex() == 0:
            self.model.profile_ratio = True
            self.model.profile_a = self.ratio_dropdown1.currentText()
            self.model.profile_b = self.ratio_dropdown2.currentText()

        else:
            self.model.profile_ratio = False

            if self.f0_input_radio.isChecked():
                self.model.f0_from_txt = True
                self.model.f0_txt = self.f0_text.text()
            else:
                self.model.f0_from_txt = False

            if self.f0_eq1_radio.isChecked():
                self.model.f0_eq1 = True
            else:
                self.model.f0_eq1 = False

    def add_new_ratio_plot(self):
        self.set_model_ratio_values()

        name = "Plot%s" % self.current_focus.counter

        self.plotNum_dropdown.addItem(name)
        self.plotNum_ratio_dropdown.addItem(name)
        self.clearPlot_dropdown.addItem(name)
        self.markersPlot_dropdown.addItem(name)

        self.current_focus.add_new_plot(ratio_plot=True)

    def add_ratio_to_plot(self):
        self.model.current_name = self.plotNum_ratio_dropdown.currentText()
        self.set_model_ratio_values()

        if self.ratio_new_axis_box.checkState() == QtCore.Qt.Checked:
            self.current_focus.add_ratio_to_plot(new_axis=True)
        else:
            self.current_focus.add_ratio_to_plot()

if __name__ == '__main__':
    from Model import Model
    app = QtGui.QApplication(sys.argv)
    ex = FilePlotController(Model())
    ex.show()
    sys.exit(app.exec_())