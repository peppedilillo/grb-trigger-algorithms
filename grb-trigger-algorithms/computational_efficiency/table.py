import pandas as pd

if __name__ == "__main__":
    outputs = ["./outputs/results_focus.txt", "./outputs/results_gbm.txt"]
    results = {
        "focus": {},
        "benchmark": {},
    }
    for file, key in zip(outputs, results):
        with open(file) as f:
            lines = f.readlines()
            assert len(lines) % 2 == 0
            for input_file, result in zip(lines[::2], lines[1::2]):
                data_num = int(input_file.split("n")[-1].split("_")[0])
                data_bkgrate = float(input_file.split("l")[-1].split("_")[0])
                results[key].setdefault((data_num, data_bkgrate), []).append(
                    float(result.split(" s.")[0])
                )

    df_focus = (
        pd.DataFrame(results["focus"])
        .stack()
        .reset_index(level=0, drop=True)
        .transpose()
        .groupby(level=0, axis=1)
        .mean()
    )
    df_benchmark = (
        pd.DataFrame(results["benchmark"])
        .stack()
        .reset_index(level=0, drop=True)
        .transpose()
        .groupby(level=0, axis=1)
        .mean()
    )
    df_focus = df_focus * 1000
    df_benchmark = df_benchmark * 1000

    print("focus: ")
    print(df_focus.style.format(precision=2).to_latex(hrules=True))
    print("benchmark: ")
    print(df_benchmark.style.format(precision=2).to_latex(hrules=True))
    merged_df = pd.concat((df_focus, df_benchmark), axis=1).drop(columns=[8.0, 32.0])
    latex_string = merged_df.style.format(precision=2).to_latex(hrules=True)
    print("concatenated: ")
    print(latex_string)
    with open("./outputs/table.tex", "w") as text_file:
        text_file.write(latex_string)
