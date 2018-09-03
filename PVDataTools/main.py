import sys
from PyQt4 import QtGui
from .PVDataTools import PVDataTools

def run_app():
    app = QtGui.QApplication.instance()
    if not app:
        app = PVDataTools(sys.argv)
    sys.exit(app.exec_())