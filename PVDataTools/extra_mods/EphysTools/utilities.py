__author__ = 'Dan'

import numpy as np


def baseline(df, start_time, end_time):
    """Function to baseline a currvent or voltage trace. Average value between start and end
    times are subtracted from Primary data column. Returns modified dataframe"""
    
    df_sub = df.Primary[(df.Time >= start_time) & (df.Time <= end_time)]
    avg = df_sub.mean()
    df.Primary -= avg

    return df


def simple_smoothing(data, n):
    
    if np.isnan(np.sum(data)):
        starting_nans = data[np.isnan(data)]
        data_no_nan = data[len(starting_nans):]

        smoothed = simple_smoothing(data_no_nan, n)

        return np.append(starting_nans, smoothed)

    else:
        cum_sum = np.cumsum(data, dtype=float)
        cum_sum[n:] = cum_sum[n:] - cum_sum[:-n]

        nan_array = np.full(n-1, np.nan)
        smoothed = cum_sum[n - 1:] / n

        return np.append(nan_array, smoothed)
