from collections import deque
from math import sqrt

import scipy.special as sps


def sign(n, b, threshold):
    if n > b + threshold * sqrt(b):
        # poisson partition function
        pvalue = sps.pdtrc(n, b)
        # sqrt(2) * erfinv(1 - 2 * pvalue)
        stdevs = -sps.ndtri(pvalue)
        return stdevs
    return 0.0


def init(threshold, b, hmax=None, skip=0):
    def run(xs):
        assert (hmax is None) or isinstance(hmax, int) and hmax > 0
        assert isinstance(skip, int) and skip >= 0

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
        return 0, t + 1, t

    return run
