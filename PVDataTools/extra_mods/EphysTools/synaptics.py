__author__ = 'Dan'

import numpy as np
from scipy.optimize import curve_fit
import pandas as pd
from . import utilities as util


def find_current_vals(df, sign="min"):

    if sign == "min":
        peak = df.Primary.min()
    elif sign == "max":
        peak = df.Primary.max()

    peak_time = df.Time[df.Primary == peak]
    peak_index = peak_time.index.values.tolist()
    
    try:
        peak_index = [peak_index[0][-1], ]        
    except TypeError:
        peak_index = [peak_index[0], ]
        
    values = {"Peak Time": peak_time.values[0], "Peak": peak}
    values_df = pd.DataFrame(values, index=peak_index)

    return values_df


def find_peak(df, start_time, end_time, sign="min"):
    df_sub = df[(df.Time >= start_time) & (df.Time <= end_time)]
    peak = find_current_vals(df_sub, sign=sign)
    
    return peak
    
    
def find_peak_groupby(df, start_time, end_time, sign="min"):
    df_sub = df[(df.Time >= start_time) & (df.Time <= end_time)]
    grouped = df_sub.groupby(level="Sweep")
    peak = grouped.apply(find_current_vals, sign=sign)

    return peak


def calculate_synaptic_decay(df, peak, peak_time, return_plot_vals=False):
    peak_sub = df[df.Time >= peak_time]

    if peak < 0:
        fit_sub = peak_sub[(peak_sub.Primary >= peak * .90) & (peak_sub.Primary <= peak * 0.1)]
        guess = np.array([-1, 1e3, -1, 1e3, 0])

    else:
        fit_sub = peak_sub[(peak_sub.Primary <= peak * .90) & (peak_sub.Primary >= peak * 0.1)]
        guess = np.array([1, 1e3, 1, 1e3, 0])

    x_zeroed = fit_sub.Time - fit_sub.Time.values[0]

    def exp_decay(x, a, b, c, d, e):
        return a*np.exp(-b*x) + c*np.exp(-d*x) + e

    popt, pcov = curve_fit(exp_decay, x_zeroed, fit_sub.Primary, guess)

    x_full_zeroed = peak_sub.Time - peak_sub.Time.values[0]
    y_curve = exp_decay(x_full_zeroed, *popt)

    amp1 = popt[0]
    tau1 = 1/popt[1]
    amp2 = popt[2]
    tau2 = 1/popt[3]

    tau = ((tau1*amp1)+(tau2*amp2))/(amp1+amp2)

    if return_plot_vals:
        return tau, x_full_zeroed, peak_sub.Primary, y_curve
    else:
        return tau


def analyze_current(df, bsl_start, bsl_end, stim_start, stim_end, sign="min"):
    df_bsl = util.baseline(df, bsl_start, bsl_end)
    
    if df_bsl.index.nlevels == 1:
        current_vals = find_peak(df_bsl, stim_start, stim_end, sign=sign)
    else: 
        current_vals = find_peak_groupby(df_bsl, stim_start, stim_end, sign=sign)

    return current_vals


def calc_ppr(df, start_time, stim_interval, sign="min"):
    first_end = start_time + stim_interval

    df_sub1 = df[(df.Time >= start_time) & (df.Time < first_end)]
    df_sub2 = df[(df.Time >= first_end) & (df.Time <= first_end+0.5)]

    peak1 = find_current_vals(df_sub1, sign=sign)["Peak"].values
    peak2 = find_current_vals(df_sub2, sign=sign)["Peak"].values

    ppr = peak2 / peak1

    ppr_df = pd.DataFrame({"Peak 1" : peak1, "Peak 2" : peak2, "PPR" : ppr})

    return ppr_df

