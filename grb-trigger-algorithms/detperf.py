"""
This scipts runs the computational efficiency tests.
The use of the exhaustive search algorithm is disabled by default.
You can enable it uncommenting line 179.
The script is parallelized with joblib. By default it uses 4 threads.
"""

import pickle
from math import ceil

import numpy as np
from algorithms import exhaustive_true, param_sma, pfocus_des, pfocus_true
from astropy.io import fits
from detection_performances.plot import make_plot
from detection_performances.table import make_table
from joblib import Parallel, delayed


def run_triggers(control, test, triglist, labels, fluences, binning):
    container = np.zeros(
        len(fluences),
        dtype=[("significance", "f"), ("changepoint", "f"), ("triggertime", "f")],
    )
    false_positives = {label: container.copy() for label in labels}
    true_positives = {label: container.copy() for label in labels}

    for i, f in enumerate(fluences):
        counts = control[i]
        for label, trigger in list(zip(labels, triglist)):
            significance, changepoint, triggertime = trigger(counts)
            if significance > 0:
                result = (significance, changepoint * binning, triggertime * binning)
                false_positives[label][i] = result

        counts = test[i]
        for label, trigger in list(zip(labels, triglist)):
            if false_positives[label][i]["significance"] > 0.0:
                continue
            significance, changepoint, triggertime = trigger(counts)
            if significance > 0:
                result = (significance, changepoint * binning, triggertime * binning)
                true_positives[label][i] = result
    output = {
        "true det": true_positives,
        "false det": false_positives,
    }
    return output


def parallelize(
    controls,
    tests,
    triglist,
    labels,
    fluences,
    binning,
    nthreads,
    repeats=None,
    verbose=13,
):
    def step(control, test):
        return run_triggers(control, test, triglist, labels, fluences, binning)

    assert len(tests) % len(fluences) == 0
    assert len(tests) == len(controls)
    stride = int(len(tests) / len(fluences))
    intensity_steps = len(fluences)
    _repeats = stride if repeats is None else repeats
    out = Parallel(n_jobs=nthreads, verbose=verbose)(
        delayed(step)(
            controls[j * intensity_steps : (j + 1) * intensity_steps, :],
            tests[j * intensity_steps : (j + 1) * intensity_steps, :],
        )
        for j in range(_repeats)
    )
    true_positives = {}
    false_positives = {}
    for label in labels:
        true_positives[label] = np.vstack([o["true det"][label] for o in out])
        false_positives[label] = np.vstack([o["false det"][label] for o in out])
    return true_positives, false_positives


def _test(filepath):
    focus = pfocus_des.init(
        threshold=5.0,
        alpha=0.002,
        beta=0.0,
        m=250,
        t_max=250,
        sleep=1062,
        mu_min=1.1,
    )
    triglist = [focus]
    labels = ["focus"]

    hdul = fits.open(filepath)
    fsteps = hdul[0].header["FSTEPS"]
    nmin, nmax = hdul[0].header["NMIN"], hdul[0].header["NMAX"]
    binning = hdul[0].header["BINNING"]
    fluences = [round(f) for f in np.linspace(nmin, nmax, fsteps, endpoint=True)]
    controls = hdul[2].data
    tests = hdul[1].data
    run_triggers(
        controls[: len(fluences), :],
        tests[: len(fluences), :],
        triglist,
        labels,
        fluences,
        binning,
    )
    print("completed single thread test")

    parallelize(
        controls,
        tests,
        triglist,
        labels,
        fluences,
        binning,
        nthreads=20,
        verbose=13,
    )
    print("completed parallel test")


def main(nthreads=8):
    from pathlib import Path

    threshold = 5.0
    filenames = [
        "dataset_grb180703949",
        "dataset_grb120707800",
    ]
    for filename in filenames:
        hdul = fits.open(f"data/simulated_{filename}.fits")
        fsteps = hdul[0].header["FSTEPS"]
        nmin, nmax = hdul[0].header["NMIN"], hdul[0].header["NMAX"]
        binning = hdul[0].header["BINNING"]
        bkg_rate = hdul[0].header["BKGRATE"]
        lc_duration = hdul[0].header["DURATION"]
        burst_start_time = hdul[0].header["BSTART"]
        fluences = [round(f) for f in np.linspace(nmin, nmax, fsteps, endpoint=True)]
        controls = hdul[2].data
        tests = hdul[1].data

        ftrue = pfocus_true.init(
            threshold=threshold,
            b=bkg_rate * binning,
            skip=1062,
        )

        exh = exhaustive_true.init(
            threshold=threshold,
            b=bkg_rate * binning,
            hmax=ceil((lc_duration - burst_start_time) / binning),
            skip=1062,
        )

        focus = pfocus_des.init(
            threshold=threshold,
            alpha=0.002,
            beta=0.0,
            m=250,
            t_max=250,
            sleep=1062,
            mu_min=1.1,
        )

        gbm = param_sma.init_gbm(
            threshold=threshold,
        )

        batse = param_sma.init_batse(
            threshold=threshold,
        )

        trig_dict = {
            # "Exhaustive": exh,
            "FOCuS": ftrue,
            "FOCuS-AES": focus,
            "GBM": gbm,
            "BATSE": batse,
        }
        triglist = list(trig_dict.values())
        labels = list(trig_dict.keys())

        true_detections, false_detections = parallelize(
            controls,
            tests,
            triglist,
            labels,
            fluences,
            binning,
            nthreads,
            verbose=13,
        )

        results = {
            "fluences": fluences,
            "true": true_detections,
            "false": false_detections,
        }

        Path("detection_performances/outputs/").mkdir(parents=True, exist_ok=True)
        results_filepath = f"detection_performances/outputs/results_{filename}.pkl"
        with open(results_filepath, "wb") as to_file:
            pickle.dump(results, to_file)

        latex_string = make_table(results_filepath)
        Path("detection_performances/tables/").mkdir(parents=True, exist_ok=True)
        table_filepath = f"detection_performances/tables/table_{filename}.tex"
        with open(table_filepath, "w") as f:
            f.write(latex_string)
        make_plot(results_filepath)

        fig, ax = make_plot(results_filepath)
        Path("detection_performances/plots/").mkdir(parents=True, exist_ok=True)
        plot_filepath = f"detection_performances/plots/plot_{filename}.png"
        fig.savefig(plot_filepath, dpi=300)


if __name__ == "__main__":
    main(nthreads=4)
