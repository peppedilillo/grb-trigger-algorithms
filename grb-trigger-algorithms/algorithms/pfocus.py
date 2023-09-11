from math import inf, log, sqrt


class Curve:
    def __init__(self, a: float, b: int, t: int, m: float):
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
        if area > 0:
            return +1
        return -1


class Focus:
    def __init__(self, threshold_std, mu_min=1.0):
        assert mu_min >= 1
        assert threshold_std > 0

        self.ab_crit = 1 if mu_min == 1 else (mu_min - 1) / log(mu_min)
        self.threshold_llr = threshold_std**2 / 2  # loglikelihood-ratio threshold
        self.global_max = None
        self.time_offset = None
        self.curve_list = []
        self.curve_list.append(Curve(inf, 0.0, 0, 0.0))
        self.curve_list.append(Curve(0, 0.0, 0, 0.0))

    def __call__(self, xs, bs):
        assert len(xs) > 1

        self.global_max = 0.0
        self.time_offset = 0
        for t, (x_t, b_t) in enumerate(zip(xs, bs)):
            self.update(x_t, b_t)
            if self.global_max > self.threshold_llr:
                return sqrt(2 * self.global_max), -self.time_offset + t + 1, t
        return 0.0, len(xs) + 1, len(xs)

    def update(self, x, b):
        p = self.curve_list.pop(-1)
        acc = Curve(p.a + x, p.b + b, p.t + 1, p.m)
        while p.dominate(self.curve_list[-1], acc) <= 0:
            p = self.curve_list.pop(-1)

        if (acc.a - p.a) > self.ab_crit * (acc.b - p.b):
            acc.m = p.m + p.ymax(acc)
            self.maximize(p, acc)
            self.curve_list.append(p)
            self.curve_list.append(acc)
        else:
            self.curve_list = self.curve_list[:1]
            self.curve_list.append(Curve(0, 0.0, 0, 0.0))
        return

    def maximize(self, p, acc):
        m = acc.m - p.m
        i = len(self.curve_list)
        while m + p.m >= self.threshold_llr:
            if m >= self.threshold_llr:
                self.global_max = m
                self.time_offset = acc.t - p.t
                break
            i -= 1
            p = self.curve_list[i]
            m = p.ymax(acc)
        return


if __name__ == "__main__":
    from math import pi

    import matplotlib.pyplot as plt
    import numpy as np
    import scipy.stats as stats

    print("generating data")
    samples_per_second = 64
    num_samples = 90 * 60 * samples_per_second
    ts = np.linspace(0, 1, num_samples + 1)[:-1] * 90 * 60  # seconds
    true_background = 4 + 2 * np.sin(
        2 * pi * np.linspace(0, 1, num_samples) + 2 * pi * stats.uniform().rvs(1)
    )
    anomaly_duration = int(stats.uniform().rvs(1) * 10 * 64) + 1
    anomaly_start = int(stats.uniform().rvs(1) * (num_samples - anomaly_duration))
    print("simulated anomaly starts at {}".format(anomaly_start))
    background_counts = stats.poisson(mu=true_background).rvs(size=num_samples)
    anomaly_counts = (
        1.0
        * true_background
        * np.concatenate(
            (
                np.zeros(anomaly_start),
                np.ones(anomaly_duration),
                np.zeros(num_samples - anomaly_start - anomaly_duration),
            )
        )
    )
    counts = background_counts + anomaly_counts

    print("running focus")
    f = Focus(threshold_std=5.5, mu_min=1.1)
    s, cp, st = f(counts, true_background)
    print("sign {:.2f}, change {}, stop {}.".format(s, cp, st))

    plt.step(ts, counts)
    plt.plot(ts, true_background, color="black", label="background")
    plt.axvline(ts[cp], color="orange", label="changepoint")
    plt.axvline(
        ts[anomaly_start], color="black", linestyle="dashed", label="true anomaly"
    )
    plt.legend()
    plt.show()
