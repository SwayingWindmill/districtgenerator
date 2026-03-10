# -*- coding: utf-8 -*-

"""
This example computes 7-day demand curves for a single house
for occupant counts from 1 to 3 using the standard DistrictGenerator workflow.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from districtgenerator.classes import Datahandler


SCENARIO_NAME = "single_house_7d"
CONFIG_NAME = ".env.CONFIG.SINGLE_HOUSE_7D"
DEFAULT_OCCUPANT_COUNTS = (1, 2, 3)
DEFAULT_OUTPUT_DIRNAME = "e10_single_house_7day_people_sweep"


def _build_time_index(data: Datahandler) -> pd.DatetimeIndex:
    """Create a timestamp index matching the configured time horizon."""
    freq = pd.to_timedelta(data.time["timeResolution"], unit="s")
    start = "2015-01-01"
    return pd.date_range(start=start, periods=data.time["timeSteps"], freq=freq)


def _set_single_house_occupants(building: dict, data: Datahandler, occupants: int) -> None:
    """
    Override the stochastic occupant count with a fixed household size.

    This keeps the standard workflow intact while replacing the default
    random household size before the demand profiles are generated.
    """
    user = building["user"]
    if building["buildingFeatures"]["building"] not in {"SFH", "TH"}:
        raise ValueError("This example expects a single SFH or TH building.")

    user.nb_occ = [occupants]
    user.generate_annual_el_consumption_residential()
    building["envelope"].coolingload = building["envelope"].calcCoolingLoad(
        site=data.site,
        nb_occ=occupants
    )


def _run_single_case(occupants: int, output_dir: Path) -> pd.DataFrame:
    """Run the full workflow for one fixed occupant count and return the results."""
    case_result_dir = output_dir / f"{occupants}p"
    case_result_dir.mkdir(parents=True, exist_ok=True)

    data = Datahandler(
        scenario_name=SCENARIO_NAME,
        env_path=CONFIG_NAME,
        resultPath=str(case_result_dir)
    )

    data.generateEnvironment()
    data.initializeBuildings()
    data.generateBuildings()

    building = data.district[0]
    _set_single_house_occupants(building, data, occupants)

    data.generateDemands(
        calcUserProfiles=True,
        saveUserProfiles=False,
        gen_cars=False
    )

    time_index = _build_time_index(data)
    user = building["user"]

    result = pd.DataFrame({
        "timestamp": time_index,
        "occupants": occupants,
        "occupancy_persons": user.occ,
        "electricity_W": user.elec,
        "dhw_W": user.dhw,
        "internal_gains_W": user.gains,
        "heating_W": user.heat,
        "cooling_W": user.cooling,
    })
    result.to_csv(case_result_dir / f"single_house_7d_{occupants}p.csv", index=False)
    return result


def _plot_comparison(results: dict[int, pd.DataFrame], output_dir: Path, show: bool = False) -> None:
    """Plot demand curve comparisons for all requested occupant counts."""
    metrics = (
        ("occupancy_persons", "Occupancy [-]"),
        ("electricity_W", "Electricity [W]"),
        ("dhw_W", "DHW [W]"),
        ("heating_W", "Heating [W]"),
    )

    fig, axes = plt.subplots(len(metrics), 1, figsize=(14, 12), sharex=True)
    if len(metrics) == 1:
        axes = [axes]

    for axis, (column, ylabel) in zip(axes, metrics):
        for occupants, df in results.items():
            axis.plot(df["timestamp"], df[column], label=f"{occupants} person(s)", linewidth=1.2)
        axis.set_ylabel(ylabel)
        axis.grid(True, alpha=0.3)
        axis.legend()

    axes[-1].set_xlabel("Timestamp")
    fig.suptitle("Single House 7-Day Demand Comparison")
    fig.tight_layout()
    fig.savefig(output_dir / "single_house_7d_comparison.png", dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the example script."""
    parser = argparse.ArgumentParser(
        description="Generate 7-day demand curves for one house for one or more occupant counts."
    )
    parser.add_argument(
        "--occupants",
        nargs="+",
        type=int,
        default=list(DEFAULT_OCCUPANT_COUNTS),
        help="One or more household sizes to simulate, e.g. --occupants 1 2 3",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional directory for CSV and plot outputs.",
    )
    parser.add_argument(
        "--show-plot",
        action="store_true",
        help="Display the comparison plot after saving it.",
    )
    return parser.parse_args()


def example10_single_house_7day_people_sweep(
    output_dir: str | Path | None = None,
    occupant_counts: tuple[int, ...] = DEFAULT_OCCUPANT_COUNTS,
    show_plot: bool = False,
) -> dict[int, pd.DataFrame]:
    """
    Compute 7-day demand curves for one house with 1, 2 and 3 occupants.

    Parameters
    ----------
    output_dir : str | Path | None, optional
        Directory for the generated CSV files. If omitted, results are saved
        in "<repo>/results/e10_single_house_7day_people_sweep".

    Returns
    -------
    dict[int, pd.DataFrame]
        A mapping from occupant count to the computed demand time series.
    """
    occupant_counts = tuple(dict.fromkeys(occupant_counts))
    if not occupant_counts:
        raise ValueError("At least one occupant count must be provided.")
    if any(occupants <= 0 for occupants in occupant_counts):
        raise ValueError("Occupant counts must be positive integers.")

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "results" / DEFAULT_OUTPUT_DIRNAME
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    results: dict[int, pd.DataFrame] = {}
    for occupants in occupant_counts:
        print(f"Running 7-day demand generation for {occupants} occupant(s)...")
        results[occupants] = _run_single_case(occupants, output_dir)

    combined = pd.concat(results.values(), ignore_index=True)
    combined.to_csv(output_dir / "single_house_7d_combined.csv", index=False)

    summary = pd.DataFrame({
        "occupants": list(results.keys()),
        "electricity_kWh": [
            df["electricity_W"].sum() * 600 / 3600 / 1000 for df in results.values()
        ],
        "dhw_kWh": [
            df["dhw_W"].sum() * 600 / 3600 / 1000 for df in results.values()
        ],
        "heating_kWh": [
            df["heating_W"].sum() * 600 / 3600 / 1000 for df in results.values()
        ],
        "cooling_kWh": [
            df["cooling_W"].sum() * 600 / 3600 / 1000 for df in results.values()
        ],
    })
    summary.to_csv(output_dir / "single_house_7d_summary.csv", index=False)
    _plot_comparison(results, output_dir, show=show_plot)

    print(f"Finished. CSV files written to: {output_dir}")
    return results


if __name__ == "__main__":
    args = _parse_args()
    example10_single_house_7day_people_sweep(
        output_dir=args.output_dir,
        occupant_counts=tuple(args.occupants),
        show_plot=args.show_plot,
    )
