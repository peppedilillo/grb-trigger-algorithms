"""
A wrapper to Poisson-FOCuS implementing background estimate via double
exponential smoothing.
"""

from collections import deque
from math import sqrt

from algorithms.pfocus import Focus, ymax


class FOCuSDES:
    def __init__(
        self,
        threshold: float,
        alpha: float,
        beta: float,
        m: int,
        mu_min: float = 1.0,
        t_max: int | None = None,
        sleep: int | None = None,
        s_0: float | None = None,
        b_0: float | None = None,
    ):
        """
        Args:
            threshold:  in standard deviation units.
            alpha: DES alpha (value) parameter.
            beta: DES beta (slope) parameter
            m: background estimate delay and forecast length.
            t_max:  maximum changepoint duration, quality control.
            disabled by default.
            mu_min: FOCuS mu_min parameter. defaults to 1.
            sleep: dead time for automated s_0 initialization.
            if provided, it must be greater than m; else, defaults to m.
            s_0: DES init count parameter.
            must be greater than 0.
            defaults to averaged over first `sleep - m` counts.
            b_0: DES init slope parameter. must be greater or equal than 0.
            defaults to 0.
        """
        if alpha < 0.0:
            raise ValueError("alpha must be non negative.")
        if beta < 0.0:
            raise ValueError("beta must be non negative.")

        self.focus = Focus(threshold, mu_min=mu_min)
        self.buffer = deque([])
        self.s_t = None
        self.b_t = None
        self.lambda_t = None
        self.t = None
        self.m = m
        self.t_max = t_max
        self.sleep = m if sleep is None else sleep
        self.alpha = alpha
        self.beta = beta
        self.s_0 = s_0
        self.b_0 = b_0

    def des_initialize(self):
        if self.s_0 is None:
            counts_sum = sum([self.buffer[i] for i in range(self.sleep - self.m)])
            delta_t = self.sleep - self.m
            self.s_t = counts_sum / delta_t
        else:
            self.s_t = self.s_0
        if self.b_0 is None:
            self.b_t = 0.0
        else:
            self.b_t = self.b_0
        return

    def des_update(self, x):
        s_t_1 = self.s_t
        b_t_1 = self.b_t
        self.s_t = self.alpha * x + (1 - self.alpha) * (s_t_1 + b_t_1)
        self.b_t = self.beta * (self.s_t - s_t_1) + (1 - self.beta) * b_t_1
        return

    def qc(self):
        """
        quality control.
        called only if focus is over threshold and t_max is given.
        it recomputes the curve stack maximum, skipping curves earlier than
        t_max. useful with delayed background estimate.
        TODO: this can be improved but for the purpose of the paper is ok.
        """
        if self.t_max is None:
            return sqrt(2 * self.focus.global_max), self.focus.time_offset
        max_significance = 0.0
        offset = 0
        acc = self.focus.curve_list.pop(-1)
        for q in self.focus.curve_list[::-1][:-1]:
            if acc.t - q.t > self.t_max:
                break
            q_max = ymax(q, acc)
            if q_max > max_significance:
                offset = acc.t - q.t
                max_significance = ymax(q, acc)
        self.focus.curve_list.append(acc)
        return sqrt(2 * max_significance), offset

    def step(self, x):
        self.t = 0 if self.t is None else self.t + 1
        self.buffer.append(x)
        if self.t <= self.sleep:
            if self.t != self.sleep:
                return 0.0, 0
            # initialize des
            if self.t == self.sleep:
                self.des_initialize()
                for i in range(self.sleep - self.m):
                    self.buffer.popleft()

        x_t_m = self.buffer.popleft()
        self.des_update(x_t_m)
        self.lambda_t = self.s_t + self.m * self.b_t
        self.focus.update(x, self.lambda_t)
        if self.focus.global_max:
            significance, offset = self.qc()
            return significance, offset
        return 0.0, 0


def init(**kwargs):
    """
    For compatibility with exhaustive and conventional algorithms.
    """

    def run(xs):
        """
        Args:
            xs: a list of count data

        Returns:
            A 3-tuple: significance value (std. devs), changepoint,  and
            stopping iteration (trigger time).
        """
        focus_des = FOCuSDES(**init_parameters)
        for t, x_t in enumerate(xs):
            significance, offset = focus_des.step(x_t)
            if significance:
                return significance, t - offset + 1, t
        return 0.0, t + 1, t

    init_parameters = kwargs
    return run
