import logging
import time

import numpy as np
import pandas as pd

from algorithms.pfocus_des import FOCuSDES
from real_data.trigger_multiplexer import trigger_mux

if __name__ == "__main__":
    datafile = "./data/gbm_dataset_50to300keV_binned16ms_20171002_20171009.zip"
    trigger = FOCuSDES
    threshold = 5.0
    threshold_array = np.array([np.inf, threshold, np.inf] * 12)
    parameters = {
        "threshold": threshold,
        "alpha": 0.002,
        "beta": 0.,
        "m": 250,
        "t_max": 250,
        "sleep": 1062,
        "mu_min": 1.1,
    }

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        filename="real_data/logs/" + timestamp + "_run.log",
        level=logging.DEBUG,
    )
    print(
        "Hello!\nA log file with timestamp '{}' has been created.\n"
        "You can check it while I'm working.".format(timestamp)
    )
    logging.info("Running on datafile: {}.".format(datafile))
    logging.info("Trigger algorithm: {}.".format(trigger.__name__))
    logging.info("Trigger parameters: {}".format(parameters))

    obs_df = pd.read_csv(datafile)
    res = trigger_mux(obs_df, trigger, threshold_array, stride=18750, **parameters)
    print("I've found {} triggers. I'm done, ciao!.".format(len(res)))
