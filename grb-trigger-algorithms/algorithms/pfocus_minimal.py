from math import log


def curve_update(c, x_t, lambda_t):
    return c[0] + x_t, c[1] + lambda_t, c[2] + 1


def curve_max(c):
    return c[0] * log(c[0] / c[1]) - (c[0] - c[1])


def dominates(c, k):
    return c[0] / c[1] > k[0] / k[1]


def focus_maximize(cs):
    return max([(c[0] and curve_max(c) or 0, c[2]) for c in cs])


def focus_update(cs, x_t, lambda_t, c):
    if cs and dominates(k := curve_update(cs[0], x_t, lambda_t), c):
        return [k] + focus_update(cs[1:], x_t, lambda_t, k)
    return [(0, 0.0, 0)]


def _focus(X, lambda_t, threshold, debug=None):
    cs = [(0, 0.0, 0)]

    for t, x_t in enumerate(X):
        cs = focus_update(cs, x_t, lambda_t, (1, 1.0, 0))
        global_max, time_offset = focus_maximize(cs)
        if debug:
            print(
                debug(
                    t,
                    x_t,
                    lambda_t,
                    interpret(cs),
                    global_max,
                    -time_offset,
                )
            )
        if global_max > threshold:
            return global_max, t - time_offset + 1, t, cs
    return 0.0, len(X) + 1, len(X), cs


def interpret(cs):
    if cs[:-1]:
        return [(c[0], -c[1], -c[2]) for c in cs[:-1]]
    return []


def dbgstring_pois(
    t,
    x,
    lambda_t,
    curve_list,
    global_max,
    time_offset,
    print_maximum=True,
    print_curves=True,
):
    s = "t = {}, x = {:.0f}, b = {:.2f}".format(
        t,
        x,
        lambda_t,
    )

    if print_maximum:
        s += ", max = {:.2f}, toff = {}".format(
            global_max,
            time_offset,
        )

    if print_curves:
        s += ", curves: "
        for curve in curve_list:
            s += "({:.0f}, {:.2f}, {:.0f}) ".format(
                curve[0],
                curve[1],
                curve[2],
            )
    return s


def focus(xs, lambdas, threshold, verbosity=1):
    from math import sqrt

    if verbosity == 0:
        debug_fun = None
    elif verbosity == 1:
        debug_fun = lambda *x: dbgstring_pois(
            *x,
            print_curves=True,
            print_maximum=False,
        )
    elif verbosity == 2:
        debug_fun = lambda *x: dbgstring_pois(
            *x,
            print_curves=True,
            print_maximum=True,
        )
    else:
        raise ValueError("bad verbosity")

    corrected_threshold = threshold**2 / 2
    global_max, offset, time, cs = _focus(
        xs, lambdas, corrected_threshold, debug=debug_fun
    )
    for c in reversed(cs[:-1]):
        if curve_max(c) > corrected_threshold:
            global_max = curve_max(c)
            offset = time - c[2] + 1
            break
    significance = sqrt(2 * global_max)
    print(
        "significance: {:.2f}, change time: {:d}, trigger time: {:d}".format(
            significance,
            offset,
            time,
        )
    )
    return significance, offset, time


if __name__ == "__main__":
    import sys

    file = sys.argv[1]
    with open(file) as f:
        content = f.readlines()
        header = content[0]
        body = content[1:]
        lambda_ = float(header.strip("#"))
        X = [int(value) for value in body]
    focus(X, lambda_, threshold=5)
