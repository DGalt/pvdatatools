__author__ = 'Dan'

import sys
import os
sys.path.append(os.path.abspath("../"))
from PyQt4 import QtGui
from Model import Model
from MainWindow import MainWindow


class PVDataTools(QtGui.QApplication):

    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.model = Model()
        self.main_window = MainWindow(self.model)
        self.main_window.show()
        self.main_window.new_dataviewer()


if __name__ == '__main__':
    app = PVDataTools(sys.argv)
    sys.exit(app.exec_())