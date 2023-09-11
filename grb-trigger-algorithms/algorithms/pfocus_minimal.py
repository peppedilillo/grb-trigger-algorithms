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


def _focus(xs, bs, threshold):
    cs = [(0, 0.0, 0)]

    for t, (x_t, b_t) in enumerate(zip(xs, bs)):
        cs = focus_update(cs, x_t, b_t, (1, 1.0, 0))
        global_max, time_offset = focus_maximize(cs)
        if global_max > threshold:
            return global_max, t - time_offset + 1, t
    return 0.0, len(xs) + 1, len(xs)
