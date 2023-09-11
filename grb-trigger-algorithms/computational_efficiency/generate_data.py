import numpy as np
from pathlib import Path

seed = 666
rng = np.random.default_rng(seed)


def stringified(value, decimals):
    return "{:.{decimals}f}\n".format(value, decimals=decimals)


def write_to_file(sample, lambda_, filepath):
    with open(filepath, mode='w') as f:
        f.write("#" + stringified(lambda_, decimals=2))
        for value in sample:
            f.write(str(value) + '\n')


def generate_data(n, lambda_, anomaly_dur, anomaly_intensity):
    background = rng.poisson(lam=lambda_, size=n)
    if anomaly_dur:
        anomaly = rng.poisson(lam=anomaly_intensity * lambda_, size=anomaly_dur)
        sample = np.concatenate((background, anomaly))
    else:
        sample = background
    return sample


def run(
        n,
        lambda_,
        folderpath,
        anomaly=None,
        iteration_id=None,
):
    if anomaly is not None:
        anomaly_dur, anomaly_intensity = anomaly
        filepath = folderpath + "pois_l{}_n{}_ad{}_ai{}".format(
            str(lambda_),
            n,
            anomaly_dur,
            str(anomaly_intensity),
        )
    else:
        anomaly_dur = 0
        anomaly_intensity = 1
        filepath = folderpath + "pois_l{}_n{}".format(
            str(lambda_),
            n,
        )
    if iteration_id is not None:
        filepath = filepath + "_{:04x}".format(iteration_id)
    filepath = filepath + ".txt"

    sample = generate_data(n, lambda_, anomaly_dur, anomaly_intensity)
    write_to_file(sample, lambda_, filepath)
    return sample


if __name__ == '__main__':
    folderpath = "inputs/"
    Path("inputs/").mkdir(parents=True, exist_ok=True)

    counter = 0
    lambdas = [2 ** i for i in range(2, 7)]
    nums = [2 ** i for i in range(11, 21) for j in range(20)]
    print("generating data for performance test..")
    for lmb in lambdas:
        for num in nums:
            sample = run(
                num,
                lambda_=lmb,
                folderpath=folderpath,
                iteration_id=counter
            )
            counter += 1
    print("done!")
