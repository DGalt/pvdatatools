__author__ = 'Dan'


class Model(object):

    def __init__(self):
        self.checked = {}

        self.df = None
        self.vr_headers = []
        self.ls_headers = []

        #set in FilePlotController as the current plot name (comes from the different
        # comboboxes in FilePlotCotroller)
        self.current_name = ""

        #values are set in calc_marker_diff in FilePlotController - used by calc_marker_diff
        #for plot markers
        self.selected_plot_a = None
        self.selected_plot_b = None
        self.selected_marker_a = None
        self.selected_marker_b = None

        #value set in subtract_constant in FilePlotController
        self.constant = 0.0

        #values set in Profiles tab in FilePlotController. Set by set_model_ratio_values in FilePlotController
        self.profile_ratio = True
        self.profile_a = None
        self.profile_b = None
        self.f0_from_txt = True
        self.f0_txt = 1
        self.f0_eq1 = True

        #values set / modified when data is imported (import function is in MainWindow)
        self.data = {}
        self.vr_headers = {}
        self.ls_headers = {}
        self.sweeps = {}

        self.checked_dict = {}

    def clear_model(self):
        self.checked = {}

        self.df = None
        self.vr_headers = []
        self.ls_headers = []

        #set in FilePlotController as the current plot name (comes from the different
        # comboboxes in FilePlotCotroller)
        self.current_name = ""

        #values are set in calc_marker_diff in FilePlotController - used by calc_marker_diff
        #for plot markers
        self.selected_plot_a = None
        self.selected_plot_b = None
        self.selected_marker_a = None
        self.selected_marker_b = None

        #value set in subtract_constant in FilePlotController
        self.constant = 0.0

        #values set in Profiles tab in FilePlotController. Set by set_model_ratio_values in FilePlotController
        self.profile_ratio = True
        self.profile_a = None
        self.profile_b = None
        self.f0_from_txt = True
        self.f0_txt = 1
        self.f0_eq1 = True

        #values set / modified when data is imported (import function is in MainWindow)
        self.data = {}
        self.vr_headers = {}
        self.ls_headers = {}
        self.sweeps = {}

        self.checked_dict = {}