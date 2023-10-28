"""
Generate some poisson distributed data with an anomaly for visualization.
"""

import numpy as np
import scipy.stats as sts

np.random.seed(1)


def make_data(length, b_rate, t_rate, t_time, t_len):
    assert length >= t_time + t_len
    indeces = np.arange(length)
    counts = np.concatenate(
        (
            sts.poisson(b_rate).rvs(t_time),
            sts.poisson(t_rate).rvs(t_len),
            sts.poisson(b_rate).rvs(length - (t_time + t_len)),
        )
    )
    return indeces, counts


class Data:
    def __init__(self, bkg_rate, transient_time, transient_len, transient_intensity):
        ts, counts = make_data(
            length=64,
            b_rate=bkg_rate,
            t_rate=bkg_rate * transient_intensity,
            t_time=transient_time,
            t_len=transient_len,
        )

        self.bkg = bkg_rate
        self.transient_time = transient_time
        self.transient_len = transient_len
        self.bins = ts
        self.counts = counts


data = Data(bkg_rate=4.5, transient_time=42, transient_len=5, transient_intensity=2.0)
