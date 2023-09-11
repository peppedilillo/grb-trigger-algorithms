from collections import deque
from functools import reduce
from itertools import islice
from math import log, sqrt


def sign(n, b):
    if n > b:
        return n * log(n / b) - (n - b)
    return 0.0


# no slice for deques. equivalent to sum(d[n - h:n]])
sumdq = lambda d, n, h: sum(islice(d, n - h, n))

# a min function which support None as infinity
nmin = lambda a, b: min(map((lambda x: float("inf") if x is None else x), (a, b)))


def init(threshold, bg_len, fg_len, hs, gs):
    def run(X):
        obsbuf = deque(maxlen=buflen)  # observation buffer
        global_max = 0
        time_offset = 0

        for t, x_t in enumerate(X):
            obsbuf.append(x_t)
            if t >= bg_len:
                bkg_rate = sumdq(obsbuf, bg_len, bg_len) / bg_len
                for h, g in [(h, g) for (h, g) in zip(hs, gs) if h <= t - bg_len + 1]:
                    if (t + 1) % h == g:
                        S = sign(sumdq(obsbuf, min(buflen, t + 1), h), bkg_rate * h)
                        if S > global_max:
                            global_max = S
                            time_offset = -h

                if global_max > threshold**2 / 2:
                    return sqrt(2 * global_max), t + time_offset + 1, t
        return 0, t + 1, t  # no change found by end of signal

    assert len(hs) == len(gs)
    # check all gs are smaller than respective hs
    assert reduce((lambda x, y: x * y), [g < h for (h, g) in zip(hs, gs)])
    buflen = fg_len + bg_len
    return run


def init_gbm(threshold):
    f = init(
        threshold,
        bg_len=1062,
        fg_len=250,
        hs=[1, 2, 2, 4, 4, 8, 8, 16, 16, 32, 32, 64, 64, 128, 128, 256, 256],
        gs=[0, 0, 1, 0, 2, 0, 4, 0, 8, 0, 16, 0, 32, 0, 64, 0, 128],
    )
    return f


def init_batse(threshold):
    f = init(
        threshold,
        bg_len=1062,
        fg_len=250,
        hs=[4, 16, 64],
        gs=[0, 0, 0],
    )
    return f
