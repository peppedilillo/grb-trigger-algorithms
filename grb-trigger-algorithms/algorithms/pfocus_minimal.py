"""
A minimal functional implementation of Poisson-FOCuS with no optimization.
"""

from math import log, sqrt
from typing import NamedTuple


class Curve(NamedTuple):
    x: int
    b: float
    t: int


def curve_update(c: Curve, x: int, b: float):
    return Curve(c.x + x, c.b + b, c.t + 1)


def curve_max(c: Curve):
    return c.x * log(c.x / c.b) - (c.x - c.b)


def dominates(c: Curve, k: Curve):
    """Returns if curve 'c' dominates 'k'."""
    return c.x / c.b > k.x / k.b


def focus_maximize(cs: list[Curve]) -> tuple[float, int]:
    return max([(c.x and curve_max(c) or 0, c.t) for c in cs])


def focus_update(cs: list[Curve], x_t: int, lambda_t: float, c: Curve):
    if cs and dominates(k := curve_update(cs[0], x_t, lambda_t), c):
        return [k] + focus_update(cs[1:], x_t, lambda_t, k)
    return [Curve(0, 0.0, 0)]


def focus(xs: list[int], bs: list[float], threshold: float):
    """
    runs Poisson-FOCuS and returns a changepoint.

    Args:
        xs: a list of count data
        bs: a list of background values
        threshold: in loglikelihood ratio units (not std. devs.)

    Returns:
        A 3-tuple: significance value (standard deviations), changepoint,  and
        stopping iteration (trigger time).

    Raises:
        ValueError: if zero background is passed to the update function.
    """
    threshold_llr = threshold * threshold / 2
    cs = [Curve(0, 0.0, 0)]
    for t, (x_t, b_t) in enumerate(zip(xs, bs)):
        if b_t <= 0:
            raise ValueError("background rate must be greater than zero.")
        cs = focus_update(cs, x_t, b_t, Curve(1, 1.0, 0))
        global_max, time_offset = focus_maximize(cs)
        if global_max > threshold_llr:
            return sqrt(2 * global_max), t - time_offset + 1, t
    return 0.0, len(xs) + 1, len(xs)
