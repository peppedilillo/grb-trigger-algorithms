import pickle
import numpy as np
import pandas as pd
from lmfit.models import StepModel


def fit_erf(intensities, efficiency):
    x, y = intensities, efficiency
    mod = StepModel(form='erf')
    pars = mod.guess(y, x=x)
    pars['amplitude'].set(value=1, vary=False)
    out = mod.fit(y, pars, x=x)
    return out


def make_table(results_filepath):
    results = pickle.load(open(results_filepath, 'rb'))
    fluences = results["fluences"]
    labels = list(results["true"].keys())

    fits_dict = {}
    corr_det = []
    false_det = []
    undetected = []
    fit_50 = []
    xs = np.arange(fluences[0], fluences[-1], .01)

    for label in labels:
        correct_detections = np.where(results["true"][label]["significance"] > 0., 1, 0)
        correct_detections_num = np.sum(correct_detections)
        tests_num = np.prod(correct_detections.shape)
        correct_fraction = correct_detections_num / tests_num * 100
        false_detections = np.where(results["false"][label]["significance"] > 0., 1, 0)
        false_detections_num = np.sum(false_detections)
        detection_eff = np.mean(correct_detections, axis=0)

        fit = fit_erf(fluences, detection_eff)
        fits_dict[label] = fit
        q50 = xs[fit.eval(x=xs) > 0.5][0]
        corr_det.append(correct_detections_num)
        false_det.append(false_detections_num)
        undetected.append(tests_num - correct_detections_num - false_detections_num)
        fit_50.append(xs[fit.eval(x=xs) > 0.5][0])

    relative_eff = {}
    for label1, q50 in zip(labels, fit_50):
        for label2 in labels:
            relative_eff[(label1, label2)] = 100 * fits_dict[label2].eval(x=q50)
    dic = {
        "True": corr_det,
        "False": false_det,
        "N/A": undetected,
    }
    for i in range(len(labels)):
        dic.setdefault("F" + str(i), [relative_eff[(labels[i], l_)] for l_ in labels])

    dataframe = pd.DataFrame(data=dic, index=labels)
    latex_string = dataframe.style.format(precision=1).to_latex(hrules=True)
    return latex_string


if __name__ == "__main__":
    results_filepath = "table/results_dataset_grb180703949.pkl"
    print(make_table(results_filepath))
