from math import sqrt

from algorithms.pfocus import Focus


def init(b, threshold, mu_min=1, skip=-1):
    def run(xs):
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
