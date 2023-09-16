import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy.special as sps
import scipy.stats as sts

warnings.filterwarnings("ignore")
import seaborn as sns

sns.set_context("talk")

CMAP_BW = "binary"
CMAP = "plasma"


def make_data(length, b_rate, t_rate, t_time, t_len):
    assert length >= t_time + t_len

    indeces = np.arange(length)
    counts = np.concatenate(
        (
            sts.poisson(b_rate).rvs(t_time),
            sts.poisson(t_rate).rvs(t_len),
            sts.poisson(b_rate).rvs(length - (t_time + t_len)),
        )
    )
    return indeces, counts


def snr(n, b):
    pvalue = sps.pdtrc(n, b)
    return -sps.ndtri(pvalue)


def make_count_matrix(cs):
    ids = np.arange(len(cs))
    out = np.array(
        [
            [sum(cs[col - row : col + 1]) if col >= row else np.nan for col in ids]
            for row in ids
        ]
    )
    return out


def make_snr_matrix(mc, b_rate):
    ids = np.arange(len(mc))
    out = np.array(
        [
            [
                snr(mc[row, col], b_rate * (row + 1)) if col >= row else np.nan
                for col in ids
            ]
            for row in ids
        ]
    )
    return out


def make_max_matrix(ms):
    ids = np.arange(len(ms))
    out = np.array(
        [
            [
                ms[row, col]
                if (ms[row, col] == max(ms[:, col]) and ms[row, col] > 0)
                else np.nan
                # if ms[row,col] == max(ms[:,col]) else np.nan
                for col in ids
            ]
            for row in ids
        ]
    )
    return out


def make_trigs_matrix(ms, thr):
    ids = np.arange(len(ms))
    out = np.array(
        [
            [ms[row, col] if ms[row, col] >= thr else np.nan for col in ids]
            for row in ids
        ]
    )
    return out


def make_gbm_matrix(ids, cs, b_rate, params, offsets=False):
    mc = make_count_matrix(cs)
    if offsets:
        out = np.array(
            [
                [
                    snr(mc[row, col], b_rate * (row + 1))
                    if (
                        col >= row
                        and (
                            ((col + 1) % (row + 1) == 0)
                            or (2 * (col + 1) % (row + 1) == 0)
                        )
                        and (row + 1) in params
                    )
                    else np.nan
                    for col in ids
                ]
                for row in ids
            ]
        )
    else:
        out = np.array(
            [
                [
                    snr(mc[row, col], b_rate * (row + 1))
                    if (col >= row and (col + 1) % ((row + 1)) == 0)
                    and (row + 1) in params
                    else np.nan
                    for col in ids
                ]
                for row in ids
            ]
        )
    return out


def make_focus_curve_matrix(f_mem, ms):
    ids = np.arange(len(ms))
    tiles = [item for sublist in f_mem for item in sublist]
    max_col = max(list(zip(*tiles))[1])
    out = np.array(
        [
            [
                ms[row, col]
                if ((row, col) in tiles or (row == 0 and col <= max_col))
                else np.nan
                for col in ids
            ]
            for row in ids
        ]
    )
    return out


def make_focus_max_matrix(f_mem, ms):
    ids = np.arange(len(ms))
    tiles = [item for sublist in f_mem for item in sublist]
    max_col = max(list(zip(*tiles))[1])
    out = np.array(
        [
            [ms[row, col] if ((row, col) in tiles) else np.nan for col in ids]
            for row in ids
        ]
    )
    return out


def intersect(m1, m2):
    assert m1.shape == m2.shape
    ids = np.arange(len(m1))
    out = np.array(
        [
            [m1[row, col] if not np.isnan(m2[row, col]) else np.nan for col in ids]
            for row in ids
        ]
    )
    return out


def plot(
    mp,
    ids,
    cs,
    b_rate,
    transient_time,
    transient_len,
    maxima_matrix=None,
    print_significance=True,
):
    """
    :param mp: a matrix containing the significance values estimated by the algorithm
    :param ids: an array of bin edges
    :param cs: an array of counts
    :param b_rate: true background rate
    :param transient_time: time-index of the transient start
    :param transient_len: transients duration in units of bins
    :param maxima_matrix: None or matrix. if given significances are plotted only over matrix's tiles.
    :param print_significance: whether if significance values should be printed or not.
    :return: matplotlib figure and axes
    """
    mc = make_count_matrix(cs)
    ms = make_snr_matrix(mc, b_rate)
    if maxima_matrix is None:
        maxima_matrix = mp

    fig, (ax1, ax0) = plt.subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        figsize=(13, 18.5),
        gridspec_kw={"height_ratios": [1, 4.2]},
        constrained_layout=True,
    )
    fig.patch.set_facecolor("white")
    extent = [ids[0], ids[-1] + 1, ids[-1] + 1, ids[0]]
    scores_all = ax0.matshow(
        ms,
        cmap=CMAP_BW,
        extent=extent,
        vmin=0.0,
    )
    scores = ax0.matshow(
        mp,
        cmap=CMAP,
        extent=extent,
        vmin=0.0,
    )
    if print_significance is True:
        font_size = 6
        vertical_offset = +0.05
        for (i, j), z in np.ndenumerate(maxima_matrix):
            if not np.isnan(z) and z >= 0:
                if z > 3:
                    text_color = "black"
                else:
                    text_color = "white"
                ax0.text(
                    j + 0.5,
                    i + 0.5 + vertical_offset,
                    "{:0.1f}".format(z),
                    size=font_size,
                    ha="center",
                    va="center",
                    c=text_color,
                    family="monospace",
                )
            elif z < 0:
                ax0.text(
                    j + 0.5,
                    i + 0.5 + vertical_offset,
                    " ".format(0),
                    size=font_size,
                    ha="center",
                    va="center",
                    c="white",
                    family="monospace",
                )
    ax0.hlines(
        y=ids, xmin=ids - 1.0, xmax=ids.max() + 1.0, color="black", linewidth=0.5
    )
    ax0.vlines(x=ids, ymin=0, ymax=ids + 1.0, color="black", linewidth=0.5)
    ax0.set_ylabel("Bin length")
    ax0.xaxis.set_ticks_position("bottom")
    ax0.set_xticks(ids, minor=True)
    ax0.set_xlim(ids[0], ids[-1])
    ax0.set_ylim(ids[-1] + 1, ids[0])

    _ids = list(ids) + [ids[-1] + 1]
    _cs = list(cs) + [cs[-1]]
    ax1.step(_ids, _cs, where="post", color="k")
    ax1.fill_between(_ids, _cs, step="post", alpha=0.4, color="grey")
    ax1.fill_between(
        ids[transient_time : transient_time + transient_len + 1],
        cs[transient_time : transient_time + transient_len + 1],
        step="post",
        alpha=0.4,
        color="red",
    )
    ax1.set_ylabel("Counts")
    ax1.set_ylim(0, 20)
    ax1.set_xlim(ids[0], ids[-1] + 1)
    ax1.xaxis.set_label_position("top")
    ax1.xaxis.set_ticks_position("top")
    ax1.set_xlabel("Time Index")
    fig.colorbar(
        scores_all,
        orientation="horizontal",
        aspect=100,
        pad=0.01,
        label="Significance [$\sigma$]",
    )
    fig.colorbar(scores, orientation="horizontal", aspect=100, pad=0.02)
    return fig, (ax0, ax1)
