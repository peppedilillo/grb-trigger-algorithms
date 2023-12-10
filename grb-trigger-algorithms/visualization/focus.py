"""
This is a specialized implementation for visualization purposes.
Might be outdated when compared to the implementation in ../algorithms/pfocus.py.
Do not use this implementation for serious use cases!!
"""

from math import inf, log, sqrt


class Curve:
    def __init__(self, a: float, b: float, t: int, m: float):
        self.a = a  # counts
        self.b = b  # background
        self.t = t  # age
        self.m = m

    def __repr__(self):
        return "({}, {:.2f}, {})".format(
            self.a,
            self.b,
            self.t,
        )

    def ymax(self, acc):
        a = acc.a - self.a
        b = acc.b - self.b
        assert a > b > 0
        return a * log(a / b) - (a - b)

    def dominate(self, q, acc):
        """if dominates q, returns +1"""
        area = (acc.a - self.a) * (acc.b - q.b) - (acc.a - q.a) * (acc.b - self.b)
        return +1 if area > 0 else -1


class Focus:
    def __init__(self, threshold, mu_min=1.0):
        assert mu_min >= 1
        assert threshold > 0

        self.ab_crit = 1 if mu_min == 1 else (mu_min - 1) / log(mu_min)
        self.corrected_threshold = threshold**2 / 2
        self.global_max = 0.0
        self.time_offset = 0
        self.curve_list = [Curve(inf, 0.0, 0, 0.0)]
        self.curve_list.append(Curve(0, 0.0, 0, 0.0))

    def __call__(self, xs, bs):
        assert len(xs) > 1

        self.global_max = 0.0
        self.time_offset = 0
        for t, (x_t, b_t) in enumerate(zip(xs, bs)):
            self.step(x_t, b_t)
            if self.global_max > self.corrected_threshold:
                return sqrt(2 * self.global_max), -self.time_offset + t + 1, t
        return 0.0, len(xs) + 1, len(xs)

    def step(self, x, b):
        checked_maxima = []
        p = self.curve_list.pop(-1)
        acc = Curve(p.a + x, p.b + b, p.t + 1, p.m)
        while p.dominate(self.curve_list[-1], acc) <= 0:
            p = self.curve_list.pop(-1)

        if (acc.a - p.a) > self.ab_crit * (acc.b - p.b):
            acc.m = p.m + p.ymax(acc)
            checked_maxima = self.maximize(p, acc)
            self.curve_list.append(p)
            self.curve_list.append(acc)
        else:
            self.curve_list = self.curve_list[:1]
            self.curve_list.append(Curve(0, 0.0, 0, 0.0))
        return checked_maxima

    def maximize(self, p, acc):
        checked_maxima = [p]
        m = acc.m - p.m
        i = len(self.curve_list)
        while m + p.m >= self.corrected_threshold:
            if m >= self.corrected_threshold:
                self.global_max = m
                self.time_offset = acc.t - p.t
            i -= 1
            p = self.curve_list[i]
            m = p.ymax(acc)
            checked_maxima.append(p)
        return checked_maxima


def focus(X, lambda_1, threshold, mu_min=None):
    assert mu_min >= 1
    _focus = Focus(threshold, mu_min)
    output_curves = []
    output_maxima = []
    for T in range(len(X)):
        checked_maxima = _focus.step(X[T], lambda_1)
        acc = _focus.curve_list[-1]
        curves_info = [(acc.t - c.t, T + 1) for c in _focus.curve_list[1:-1]]
        maxima_info = [(acc.t - c.t - 1, T) for c in checked_maxima]
        output_curves.append(curves_info)
        output_maxima.append(maxima_info)
    return (
        0,
        len(X) + 1,
        len(X),
        output_curves,
        output_maxima,
    )  # no change found by end of signal
