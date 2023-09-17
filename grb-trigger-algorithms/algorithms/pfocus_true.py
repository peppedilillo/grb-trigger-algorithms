"""
A wrapper to Poisson-FOCuS for running over known, constant background.
"""

from math import sqrt

from algorithms.pfocus import Focus


def init(b: float, threshold: float, mu_min: float = 1, skip: int = 0):
    """
    Args:
        b: the background rate.
        threshold: a threshold value in units of standard deviations.
        mu_min: FOCuS mu_min parameter. defaults to 1.
        skip: number of initial iterations to skip. must be greater or equal 0.

    Returns:
        a trigger function. you run this on your data.
    """

    def run(xs: list[int]):
        """
        Args:
            xs: a list of count data

        Returns:
            A 3-tuple. If trigger condition is met the output consists of a
            significance value (std. devs), the changepoint, and
            the stopping iteration (trigger time). Else returns a triplet with
            first element equal 0.
        """
        focus = Focus(threshold, mu_min=mu_min)
        t = None
        for t, x_t in enumerate(xs):
            if t < skip:
                continue
            focus.update(x_t, b)
            if focus.global_max:
                return sqrt(2 * focus.global_max), t - focus.time_offset + 1, t
        return 0, t + 1, t

    assert mu_min >= 1.0
    return run
