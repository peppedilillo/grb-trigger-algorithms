"""
An exhaustive search algorithm.
"""

from collections import deque
from math import sqrt

import scipy.special as sps


def sign(n, b, threshold):
    if n > b + threshold * sqrt(b):
        # compute poisson partition function
        pvalue = sps.pdtrc(n, b)
        return -sps.ndtri(pvalue)
    return 0.0


def init(
    threshold: float,
    b: float,
    hmax: int | None = None,
    skip: int = 0,
):
    """
    An exhaustive search algorithm. This is for testing purpose only: the
    algorithm is not feasibile in real scendario due to complexity N^2.
    Assumes background to be constant.

    Args:
        threshold: a threshold value in units of standard deviations.
        b: the background rate.
        hmax: maximum interval length tested. must be greater than 0.
        skip: number of initial iterations to skip. must be greater or equal 0.

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
        buffer = deque(maxlen=hmax + 1) if hmax else deque()
        buffer.append(0)
        global_max = 0
        time_offset = 0
        t = 0
        for t, x_t in enumerate(xs):
            if t < skip:
                continue
            buffer.append(x_t + buffer[-1])
            for h in range(1, t + 1 - skip):
                if (hmax is not None) and (h > hmax):
                    break
                S = sign(buffer[-1] - buffer[-h - 1], b * h, threshold)
                if S > global_max:
                    global_max = S
                    time_offset = -h
            if global_max > threshold:
                return global_max, t + time_offset + 1, t
        return 0.0, t + 1, t

    if (hmax is not None) and hmax <= 0:
        raise ValueError("hmax must be either None or a positive integer.")
    if skip < 0:
        raise ValueError("skip must be a non negative integer.")
    return run
