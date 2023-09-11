import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lmfit.models import StepModel


def fit_erf(intensities, efficiency):
    x, y = intensities, efficiency
    mod = StepModel(form="erf")
    pars = mod.guess(y, x=x)
    pars["amplitude"].set(value=1, vary=False)
    out = mod.fit(y, pars, x=x)
    return out


def make_plot(results_filepath):
    results = pickle.load(open(results_filepath, "rb"))

    fluences = results["fluences"]
    labels = results["true"].keys()
    colors = [
        ("black", "grey"),
        ("black", "grey"),
        ("tomato", "red"),
        ("peachpuff", "orange"),
        ("skyblue", "lightblue"),
    ]
    linestyles = [
        "dashed",
        "dotted",
        "solid",
        "solid",
        "solid",
    ]
    fits_dict = {}
    xs = np.arange(fluences[0], fluences[-1], 1)
    fig, ax = plt.subplots(figsize=(12, 6))
    for c, label, ll in list(zip(colors, labels, linestyles)):
        if label == "FOCuS":
            continue
        corr = np.where(results["true"][label]["significance"] > 0.0, 1, 0)
        detection_eff = np.mean(corr, axis=0)
        fit = fit_erf(fluences, detection_eff)
        fits_dict[label] = fit
        table_df = pd.DataFrame(
            {"Fluence": fluences, "Efficiency": detection_eff, "Fit": fit.best_fit}
        )

        ax.plot(
            xs,
            100 * fit.eval(x=xs),
            color=c[1],
            label="FOCuS/Exhaustive" if label == "Exhaustive" else label,
            linewidth=2,
            linestyle=ll,
        )
        ax.scatter(fluences, 100 * table_df["Efficiency"], color=c[0])
    ax.set_ylabel("True positive rate [%]")
    ax.set_xlabel("Number of simulated source photons")
    plt.legend()
    return fig, ax


if __name__ == "__main__":
    results_filepath = "outputs/results_dataset_grb180703949.pkl"
    fig, ax = make_plot(results_filepath)
    plt.show()
