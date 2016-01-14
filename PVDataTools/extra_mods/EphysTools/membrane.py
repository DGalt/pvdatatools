__author__ = 'Dan'

from . import utilities as util
import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import trapz


def calc_membrane_properties(df, baseline_start=0.5, baseline_end=0.8, pulse_start=1.0,
                             pulse_duration=0.15, pulse_amplitude=-10):
                                 
    #have to make copy of df to not modify original df with calculation
    data = df.copy()
    #nudge start over slightly so don't catch a data point prior to pulse
    pulse_start += 0.0001

    #conversions - pulse_amplitude is in mVs, ydata is in pAs
    pulse_amplitude *= 1e-3
    data.Primary *= 1e-12

    #baseline recording data
    data = util.baseline(data, baseline_start, baseline_end)

    #i_baseline is defined as average current over baseline region (defined in input)
    i_baseline = data.Primary[(data.Time >= baseline_start) & (data.Time <= baseline_end)].mean()

    #i_ss is the stead-state current during the pulse, taken between 70% and 90% of pulse duration
    i_ss = data.Primary[(data.Time >= pulse_start + pulse_duration *0.7) &
                        (data.Time <= pulse_start + pulse_duration *0.9)].mean()

    #calculate delta_i -- i.e. difference between baseline current amplitude and steady-state current amplitude
    delta_i = (i_ss-i_baseline)

    #select data in pulse range
    pulse_end = pulse_start + pulse_duration - 0.0001
    ydata_full = data.Primary[(data.Time >= pulse_start) & (data.Time <= pulse_end)]
    xdata_full = data.Time[(data.Time >= pulse_start) & (data.Time <= pulse_end)]

    #remove delta_i; this part of the capacitance charge is calculated later as q2
    ydata_full -= delta_i

    #find capacitance peak and take subset of transient based on peak (0% decay to 90% decay) for fitting
    if pulse_amplitude > 0:
        peak = ydata_full.max()
        ydata = ydata_full[(ydata_full <= peak*1) & (ydata_full >= peak * 0.1)]
        xdata = xdata_full[(ydata_full <= peak*1) & (ydata_full >= peak * 0.1)]
    elif pulse_amplitude < 0:
        peak = ydata_full.min()
        ydata = ydata_full[(ydata_full >= peak*1) & (ydata_full <= peak * 0.1)]
        xdata = xdata_full[(ydata_full >= peak*1) & (ydata_full <= peak * 0.1)]

    #shift time so first time point is time = 0
    x_zeroed = xdata - xdata.values[0]

    #function to define equation for exponential fit; doing bi-exponential fit
    def exp_decay(x, a, b, c, d):
        return a*np.exp(-b*x) + c*np.exp(-d*x)

    #guesses for amplitudes and taus
    guess = np.array([1e-12, 1e3, 1e-12, 1e3])

    #actual fit
    popt, pcov = curve_fit(exp_decay, x_zeroed, ydata, guess)
    #print(popt)

    #calculate weighted tau
    amp1 = popt[0]
    tau1 = 1/popt[1]
    amp2 = popt[2]
    tau2 = 1/popt[3]

    tau = ((tau1*amp1)+(tau2*amp2))/(amp1+amp2)

    #shift time for xdata_full so first time point is time = 0
    x_full_zeroed = xdata_full - xdata_full.values[0]

    #generate y values from curve fit
    y_curve = exp_decay(x_full_zeroed, *popt)

    #take integral of curve to get q1
    q1 = trapz(y_curve, x_full_zeroed)
    #print("q1: %s" %q1)

    #q2 is correction for charge from i_baseline to i_ss
    q2 = tau * delta_i
    #print("q2: %s" %q2)

    #total charge
    qt = q1 + q2
    #print("qt: %s" %qt)

    #resistance calculations
    ra = (tau*pulse_amplitude)/qt
    rt = (pulse_amplitude)/delta_i
    rm = rt - ra

    #capacitance calculation
    cm = (qt * rt) / (pulse_amplitude * rm)


    return ra*1e-6, rm*1e-6, cm*1e12, tau*1e3
