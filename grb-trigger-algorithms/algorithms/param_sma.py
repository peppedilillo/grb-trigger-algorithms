"""
Conventional algorithms with simple moving average background estimate.
"""

from collections import deque
from functools import reduce
from itertools import islice
from math import log, sqrt


def sign(n, b):
    if n > b:
        return n * log(n / b) - (n - b)
    return 0.0


def sumdq(d, n, h):
    """
    no slice for deques. equivalent to sum(d[n - h:n]])
    """
    return sum(islice(d, n - h, n))


def init(
    threshold: float,
    bg_len: int,
    fg_len: int,
    hs: list[int],
    gs: list[int],
):
    """
    A conventional algorithm computing background via simple moving average.

    Args:
        threshold: a threshold value in units of standard deviations.
        bg_len: number of past data used for background computation.
        fg_len: number of recent data. these are not used for background estimate.
        hs: interval lengths to check. must have same length than gs.
        gs: interval offsets to check. must have same length than hs.
            all values in gs must be smaller than respective values in hs.

    Returns:
        a trigger function. you run this on your data.
    """

    def run(xs: list[int]):
        """
        Args:
            xs: a list of count data

        Returns:
            A 3-tuple: significance value (std. devs), trigger interval's length,
            and stopping iteration (trigger time).
        """
        observations_buffer = deque(maxlen=buflen)
        global_max = 0
        time_offset = 0

        for t, x_t in enumerate(xs):
            observations_buffer.append(x_t)
            if t >= bg_len:
                bkg_rate = sumdq(observations_buffer, bg_len, bg_len) / bg_len
                scheduled_tests = [
                    (h, g) for (h, g) in zip(hs, gs) if h <= t - bg_len + 1
                ]
                for h, g in scheduled_tests:
                    if (t + 1) % h == g:
                        x = sumdq(observations_buffer, min(buflen, t + 1), h)
                        b = bkg_rate * h
                        significance = sign(x, b)
                        if significance > global_max:
                            global_max = significance
                            time_offset = -h

                if global_max > threshold**2 / 2:
                    return sqrt(2 * global_max), t + time_offset + 1, t
        return 0, t + 1, t  # no change found by end of signal

    if len(hs) != len(gs):
        raise ValueError("hs and gs must have same length")
    # check all gs are smaller than respective hs
    if not reduce((lambda x, y: x * y), [g < h for (h, g) in zip(hs, gs)]):
        raise ValueError("offsets must be smaller then respective timescales")
    buflen = fg_len + bg_len
    return run


def init_gbm(threshold: float):
    """
    Initializes a conventional algorithms with GBM-like parameters.

    Args:
        threshold: a threshold value in units of standard deviations.

    Returns:
        a trigger function.
    """
    f = init(
        threshold,
        bg_len=1062,
        fg_len=250,
        hs=[1, 2, 2, 4, 4, 8, 8, 16, 16, 32, 32, 64, 64, 128, 128, 256, 256],
        gs=[0, 0, 1, 0, 2, 0, 4, 0, 8, 0, 16, 0, 32, 0, 64, 0, 128],
    )
    return f


def init_batse(threshold: float):
    """
    Initializes a conventional algorithms with BATSE-like parameters.

    Args:
        threshold: a threshold value in units of standard deviations.

    Returns:
        a trigger function.
    """
    f = init(
        threshold,
        bg_len=1062,
        fg_len=250,
        hs=[4, 16, 64],
        gs=[0, 0, 0],
    )
    return f
