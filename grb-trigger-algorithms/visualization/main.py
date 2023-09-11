import checkers
import matplotlib.pyplot as plt
from data import data
from focus import focus

if __name__ == "__main__":
    from pathlib import Path

    Path("outputs/").mkdir(parents=True, exist_ok=True)
    mc = checkers.make_count_matrix(data.counts)

    # GBM-like
    mp = checkers.make_gbm_matrix(
        data.bins,
        data.counts,
        data.bkg,
        params=[1, 2, 4, 8, 16, 32, 64],
        offsets=True,
    )
    fig, ax = checkers.plot(
        mp,
        data.bins,
        data.counts,
        data.bkg,
        data.transient_time,
        data.transient_len,
        print_significance=True,
    )
    fig.savefig("outputs/checkers_gbm.png", dpi=300)
    plt.close()

    # BATSE-like
    mp = checkers.make_gbm_matrix(
        data.bins,
        data.counts,
        data.bkg,
        params=[4, 16, 64],
        offsets=True,
    )
    fig, ax = checkers.plot(
        mp,
        data.bins,
        data.counts,
        data.bkg,
        data.transient_time,
        data.transient_len,
        print_significance=True,
    )
    fig.savefig("outputs/checkers_batse.png", dpi=300)
    plt.close()

    # FOCuS
    _, _, _, curves, maxima = focus(data.counts, data.bkg, 5.0, mu_min=1.05)
    ms = checkers.make_snr_matrix(mc, data.bkg)
    curves_matrix = checkers.make_focus_curve_matrix(curves, ms)
    max_matrix = checkers.make_focus_max_matrix(maxima, ms)
    fig, ax = checkers.plot(
        curves_matrix,
        data.bins,
        data.counts,
        data.bkg,
        data.transient_time,
        data.transient_len,
        maxima_matrix=max_matrix,
    )
    fig.savefig("outputs/checkers_focus.png", dpi=300)
    plt.close()
