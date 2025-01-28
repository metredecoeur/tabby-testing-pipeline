""" Module for displaying results of testing the quality of Tabby's suggestions depending on various lengths of prefixes and similarity testing metrics """

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import const
import utils


def next_file(source_dir: Path) -> Path:
    for fpath in source_dir.rglob("*"):
        if fpath.is_file():
            yield fpath


def plot_algorithms(src_dir: Path, plot_suffix: str):
    for alg_name in list(const.SIMILARITY_ALGORITHMS.keys()):
        fig, axis = plt.subplots()
        for fpath in next_file(src_dir):
            df = pd.read_csv(fpath, index_col=0)
            df.plot(
                y=alg_name,
                color=const.ALGORITHMS_PLOT_COLORS[alg_name],
                alpha=const.PLOT_COLORS_ALPHA,
                style="o",
                xlabel="prefix %",
                ylabel="accuracy",
                use_index=True,
                ax=axis,
                legend=False,
            )

        plot_fpath = utils.get_plots_dir() / f"{alg_name}_{plot_suffix}.png"
        plot_fpath.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(plot_fpath)


def plot_len_ratios(src_dir: Path):
    fig, axis = plt.subplots()

    for fpath in next_file(src_dir):
        df = pd.read_csv(fpath, index_col=0)
        df.plot(
            y="original_duplicate_len_ratio",
            color=const.LEN_RATIO_COLOR,
            alpha=const.PLOT_COLORS_ALPHA,
            style="o",
            xlabel="prefix %",
            ylabel="length ratio",
            use_index=True,
            ax=axis,
            legend=False,
        )
    plot_fpath = utils.get_plots_dir() / "original_duplicate_len_ratio.png"
    plot_fpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(plot_fpath)


def plot_metrics(src_dir: Path):
    avg_df = None
    file_count = 0
    for fpath in next_file(src_dir):
        file_count += 1
        df = pd.read_csv(fpath, index_col=0)
        og_values = df.loc["original"]
        df.fillna(value=og_values, inplace=True)
        if avg_df is None:
            avg_df = df
        else:
            avg_df = avg_df.add(df, fill_value=0)

    avg_df = avg_df.divide(file_count)
    original_values = avg_df.loc["original"]

    for metric in const.METRICS:
        fig, axis = plt.subplots()
        axis.plot(
            avg_df.index[avg_df.index != "original"],
            [original_values[metric]] * (len(avg_df.index) - 1),
            label="original",
            color="green",
            linestyle="-",
        )

        x_vals = avg_df.index[avg_df.index != "original"]
        y_vals = avg_df.loc[avg_df.index != "original", metric]
        axis.plot(
            x_vals,
            y_vals,
            "o-",
            label=f"duplicates",
            color=const.METRICS_PLOT_COLORS[metric],
        )
        axis.set_xlabel("prefix %")
        axis.set_ylabel(f"{metric} score")
        axis.legend()
        plt.grid()
        plot_fpath = utils.get_plots_dir() / f"{metric}.png"
        plot_fpath.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(plot_fpath)
        plt.close()


def main():
    sorted_dir = utils.get_data_dir() / "sorted"
    fragment_logs_dir = utils.get_data_dir() / "similarity_logs_fragment"
    full_logs_dir = utils.get_data_dir() / "similarity_logs_full"
    static_metrics_dir = utils.get_data_dir() / "static_metrics"
    # plot_algorithms(fragment_logs_dir, "fragment")
    # plot_algorithms(full_logs_dir, "full")
    plot_metrics(static_metrics_dir)
    # plot_len_ratios(full_logs_dir)


if __name__ == "__main__":
    main()
