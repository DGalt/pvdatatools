from distutils.core import setup
import sys
import os
from glob import glob
import scipy.optimize
import scipy.sparse
import scipy.sparse.csgraph
import scipy.sparse.csgraph._validation
from scipy.sparse.csgraph import _validation
sys.path.append(os.path.abspath("../"))
import py2exe

#files = []
#sci_folder = os.path.abspath(r'C:\Anaconda3\Lib\site-packages\scipy\optimize')
#sci_pyd_files = glob(os.path.join(sci_folder, "*.pyd"))

#output_dir = r'D:\Desktop\Py2ExeOutput'
output_dir = r'C:\Users\Dan\Desktop\Py2ExeOutput'

includes = ["sip", "PyQt4.QtCore", "PyQt4.QtGui", "PVDataTools.extra_mods.PrairieAnalysis", "PVDataTools.extra_mods.EphysTools", "lxml._elementpath",
            "scipy.optimize", "scipy.sparse", "scipy.sparse.csgraph._validation", "scipy.special._ufuncs_cxx",
            "scipy.special._ufuncs"]
packages = ["PVDataTools.extra_mods.PrairieAnalysis", "PVDataTools.extra_mods.EphysTools"]

setup(windows=[{"script":'./PVDataTools/PVDataTools.py', "dest_base": "PVDataTools v0.02"}]
      , name="PVDataTools v0.01"
      , options={"py2exe": {"includes" : includes,
                            "packages": packages, "dist_dir": output_dir}})