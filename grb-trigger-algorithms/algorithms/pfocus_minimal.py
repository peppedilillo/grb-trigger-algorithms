"""
A minimal implementation of Poisson-FOCuS with no optimiziation.
"""

from math import log


def curve_update(c, x_t, b_t):
    return c[0] + x_t, c[1] + b_t, c[2] + 1


def curve_max(c):
    return c[0] * log(c[0] / c[1]) - (c[0] - c[1])


def dominates(c, k):
    return c[0] / c[1] > k[0] / k[1]


def focus_maximize(cs):
    return max([(c[0] and curve_max(c) or 0, c[2]) for c in cs])


def focus_update(cs, x_t, b_t, c):
    if cs and dominates(k := curve_update(cs[0], x_t, b_t), c):
        return [k] + focus_update(cs[1:], x_t, b_t, k)
    return [(0, 0.0, 0)]


def focus(xs: list[int], bs: list[float], threshold: float):
    """
    This is the simplest implementation of Poisson-FOCuS.
    Note that it does not convert loglikelihood ratio significance to std. devs.
    This implies that if you want to run at 5 sigma threshold you should call
    with threshold 12.5 and should expect triggers with significance > 12.5.

    Args:
        xs: a list of count data
        bs: a list of background values
        threshold: as a loglikelihood ratio, not std. devs.

    Returns:
        A 3-tuple: significance value (loglikelihood ratio), changepoint,  and
        stopping iteration (trigger time).
    """
    cs = [(0, 0.0, 0)]

    for t, (x_t, b_t) in enumerate(zip(xs, bs)):
        cs = focus_update(cs, x_t, b_t, (1, 1.0, 0))
        global_max, time_offset = focus_maximize(cs)
        if global_max > threshold:
            return global_max, t - time_offset + 1, t
    return 0.0, len(xs) + 1, len(xs)
