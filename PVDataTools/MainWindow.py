__author__ = 'Dan'


import os
from PyQt4 import QtCore, QtGui
from extra_mods.PrairieAnalysis import pv_import as pvi
from FilePlotController import FilePlotController
from DataViewer import DataViewer
from ExportDialog import ExportDialog
from AnalysisWindows.MembraneTestWidget import MembraneTestWidget
from AnalysisWindows.SynEventDetectWidget import SynEventDetectWidget
from AnalysisWindows.PPRWidget import PPRWidget
from AnalysisWindows.PhasePlotWidget import PhasePlotWidget
from AnalysisWindows.FrequencyWidget import FrequencyWidget


class MainWindow(QtGui.QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("PV Data Tools")
        desktop = QtGui.QDesktopWidget()
        width = desktop.screenGeometry().width()
        ratio = width / 1920
        self.resize(1400*ratio, 800*ratio)

        self.model = model

        self.menubar = self.menuBar()
        self.setup_file_menu()
        self.setup_analysis_menu()
        self.current_focus = None

        self.mdi = QtGui.QMdiArea()
        self.mdi.subWindowActivated.connect(self.set_current_focus)
        self.file_plt_ctrl = FilePlotController(self.model)

        central_widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout(central_widget)
        layout.addWidget(self.file_plt_ctrl)
        layout.addWidget(self.mdi, QtCore.Qt.AlignCenter)

        self.setCentralWidget(central_widget)

    def setup_file_menu(self):
        file_menu = self.menubar.addMenu("File")

        file_new_action = QtGui.QAction("New DataViewer", self)
        file_new_action.triggered.connect(self.new_dataviewer)
        file_menu.addAction(file_new_action)

        load_menu = file_menu.addMenu("Load")

        load_single_action = QtGui.QAction("Single Folder", self)
        load_single_action.triggered.connect(self.load_single_folder)
        load_multi_action = QtGui.QAction("Multiple Folders", self)
        load_multi_action.triggered.connect(self.load_multiple_folders)

        load_menu.addAction(load_single_action)
        load_menu.addAction(load_multi_action)

        export_action = QtGui.QAction("Export", self)
        export_action.triggered.connect(self.create_export_dialog)
        file_clear_action = QtGui.QAction("Clear workspace", self)
        file_clear_action.triggered.connect(self.clear_workspace)
        file_menu.addAction(export_action)
        file_menu.addAction(file_clear_action)

    def setup_analysis_menu(self):
        analysis_menu = self.menubar.addMenu("Analysis")

        intrinsic_menu = analysis_menu.addMenu("Intrinsic Properties")
        mem_test_action = QtGui.QAction("Membrane Test", self)
        mem_test_action.triggered.connect(lambda: self.new_analysis_window(window_type="MembraneTestWidget"))

        intrinsic_menu.addAction(mem_test_action)

        synaptics_menu = analysis_menu.addMenu("Synaptics")
        single_event_action = QtGui.QAction("Single Event Detection", self)
        single_event_action.triggered.connect(lambda: self.new_analysis_window(window_type="SynEventDetectWidget"))
        ppr_action = QtGui.QAction("Paired-Pulse Ratio", self)
        ppr_action.triggered.connect(lambda: self.new_analysis_window(window_type="PPRWidget"))

        synaptics_menu.addAction(single_event_action)
        synaptics_menu.addAction(ppr_action)

        pacemake_menu = analysis_menu.addMenu("Pacemaking")
        phaseplot_action = QtGui.QAction("Phase Plot", self)
        phaseplot_action.triggered.connect(lambda: self.new_analysis_window(window_type="PhasePlotWidget"))
        frequency_action = QtGui.QAction("Frequency Analysis", self)
        frequency_action.triggered.connect(lambda: self.new_analysis_window(window_type="FrequencyWidget"))

        pacemake_menu.addAction(phaseplot_action)
        pacemake_menu.addAction(frequency_action)

    def set_current_focus(self, subwindow):
        """Sets the current active subwindow to the focus window for the FilePlotController
        update_focus will set the focus window in FilePlotController, and update FilePlotController
        so the UI is correct and the buttons are connected to the correct methods for the window selected

        If None is pass, UI shows no current plots and the buttons are disconnected from all slots
        """

        if subwindow is not None:
            self.current_focus = subwindow.widget()
            self.file_plt_ctrl.update_focus(self.current_focus)

        else:
            self.current_focus = None
            self.file_plt_ctrl.update_focus(None)

    def load_single_folder(self):
        folder_list = [QtGui.QFileDialog.getExistingDirectory(self), ]

        self.load_data_folder(folder_list)

    def load_multiple_folders(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        dialog.setViewMode(QtGui.QFileDialog.Detail)
        dialog.setOption(QtGui.QFileDialog.DontUseNativeDialog, True)

        for view in dialog.findChildren((QtGui.QListView, QtGui.QTreeView)):
            if isinstance(view.model(), QtGui.QFileSystemModel):
                view.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        if dialog.exec_():
            folders_list = dialog.selectedFiles()

            dir_path = dialog.directory().path()
            if dir_path in folders_list:
                folders_list.remove(dir_path)

            self.load_data_folder(folders_list)

    def load_data_folder(self, folder_list):

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        QtGui.qApp.processEvents()

        for folder in folder_list:
            real_folder = folder
            folder_split = os.path.split(folder)
            child_folder = folder_split[1]
            parent_folder = os.path.split(folder_split[0])[1]
            folder = os.path.join(parent_folder, child_folder)

            if folder in self.model.data.keys():
                del self.model.data[folder]

            self.model.data[folder] = pvi.import_folder(real_folder)

            current_df = self.model.data[folder]

            if current_df['voltage recording'] is not None:
                self.model.vr_headers[folder] = current_df['voltage recording'].columns[1:].tolist()
                self.model.sweeps[folder] = current_df['voltage recording'].index.levels[0]

            if current_df['linescan'] is not None:
                self.model.ls_headers[folder] = current_df['linescan'].columns[1::2].tolist()

                if current_df['voltage recording'] is None:
                    self.model.sweeps[folder] = current_df['linescan'].index.levels[0]

                ratio_items1 = [self.file_plt_ctrl.ratio_dropdown1.itemText(i)
                                for i in range(self.file_plt_ctrl.ratio_dropdown1.count())]
                ratio_items2 = [self.file_plt_ctrl.ratio_dropdown2.itemText(i)
                                for i in range(self.file_plt_ctrl.ratio_dropdown2.count())]

                for profile in self.model.ls_headers[folder]:
                    if profile not in ratio_items1:
                        self.file_plt_ctrl.ratio_dropdown1.addItem(profile)

                    if profile not in ratio_items2:
                        self.file_plt_ctrl.ratio_dropdown2.addItem(profile)

                self.file_plt_ctrl.tab_widget.setTabEnabled(2, True)

            elif self.file_plt_ctrl.tab_widget.isTabEnabled(2):
                self.file_plt_ctrl.tab_widget.setTabEnabled(2, False)

        if any(folder_list):
            self.file_plt_ctrl.update_tree_widget()

        QtGui.QApplication.restoreOverrideCursor()

    def new_dataviewer(self):
        """Creates a new DataViewer window"""

        dataviewer = DataViewer(self.model)

        dataviewer_window = QtGui.QMdiSubWindow()
        dataviewer_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dataviewer_window.setWidget(dataviewer)

        self.mdi.addSubWindow(dataviewer_window)
        dataviewer_window.resize(self.mdi.size()*0.5)
        dataviewer_window.show()

    def new_analysis_window(self, window_type):

        if window_type == "MembraneTestWidget":
            new_widget = MembraneTestWidget(self.model)
        elif window_type == "SynEventDetectWidget":
            new_widget = SynEventDetectWidget(self.model)
        elif window_type == "PPRWidget":
            new_widget = PPRWidget(self.model)
        elif window_type == "PhasePlotWidget":
            new_widget = PhasePlotWidget(self.model)
        elif window_type == "FrequencyWidget":
            new_widget = FrequencyWidget(self.model)

        new_window = QtGui.QMdiSubWindow()
        new_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        new_window.setWidget(new_widget)

        self.mdi.addSubWindow(new_window)
        new_window.resize(self.mdi.size()*0.5)
        new_window.show()

    def create_export_dialog(self):
        if self.current_focus is not None:
            export_dialog = ExportDialog(parent=self, current_focus=self.current_focus)
            export_dialog.exec()

    def clear_workspace(self):
        self.file_plt_ctrl.tree_widget.clear()

        for window in self.mdi.subWindowList():
            window.close()

        self.model.clear_model()


if __name__ == '__main__':
    from Model import Model
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow(Model())
    ex.show()
    sys.exit(app.exec_())
