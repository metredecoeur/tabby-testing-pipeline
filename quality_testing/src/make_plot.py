""" Module for displaying results of testing the quality of Tabby's suggestions depending on various lengths of prefixes and similarity testing metrics """
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import argparse

import const


def cli_arguments():
    parser = argparse.ArgumentParser(
        prog="Plotter",
        description="Programme for drawing plots based on the testing results",
    )

    parser.add_argument(
        "test_results_path",
        help=f"Path to the directory where test results are stored in csv format, relative to {__file__}",
    )

    parser.add_argument(
        "-alg",
        "--similarity_algorithm",
        help=f"name of the similarity algorithm to choose as a plotting criteria. Must be one of {const.SIMILARITY_ALGORITHMS.keys()}",
        default=None,
        action="extend",
        nargs="+",
    )

    parser.add_argument(
        "-s",
        "--save_plot",
        help="path to save plot as png",
    )
    # @TODO add a desired number of samples to check


    args = parser.parse_args()
    # @TODO check if path exists

    if args.similarity_algorithm is None:
        args.similarity_algorithm = const.SIMILARITY_ALGORITHMS.keys()
    elif not all(
        [alg in const.SIMILARITY_ALGORITHMS.keys() for alg in args.similarity_algorithm]
    ):
        raise ValueError(
            f"Similarity algorithm names must be one of {const.SIMILARITY_ALGORITHMS.keys()}"
        )

    save_plot_fpath = args.save_plot
    if save_plot_fpath is not None:
        save_plot_fpath = Path(save_plot_fpath)
        save_plot_fpath.parent.mkdir(parents=True, exist_ok=True)

    return Path(args.test_results_path), args.similarity_algorithm, save_plot_fpath


def init_plot():
    fig, axis = plt.subplots()
    plt.ylabel("accuracy")
    plt.xlabel("prefix percentage")
    return fig, axis


def main():
    # create plot instance
    _, axis = init_plot()
    # for every algorithm update the plot with its results
    data_dir, similarity_algorithms, save_plot_fpath = cli_arguments()

    for fpath in [fpath for fpath in data_dir.rglob("*") if fpath.is_file()]:
        df = pd.read_csv(fpath, index_col=0)
        df.plot(
            y=similarity_algorithms,
            color=[const.ALGORITHMS_PLOT_COLORS[alg] for alg in similarity_algorithms],
            alpha=const.PLOT_COLORS_ALPHA,
            style="o",
            xlabel="prefix %",
            ylabel="accuracy",
            use_index=True,
            ax=axis,
            legend=False,
        )
    plt.legend(similarity_algorithms, loc="lower center")
    if save_plot_fpath is not None:
        plt.savefig(save_plot_fpath)
    plt.show()


if __name__ == "__main__":
    main()