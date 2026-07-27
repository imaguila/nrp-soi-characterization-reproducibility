# -*- coding: utf-8 -*-
"""
Reproducibility script for the WordProc SOI characterization.

This script reads exported SOI CSV files from the WordProc walkthrough and
generates the descriptive metrics, pairwise similarities, consensus support
tables, and figures reported in the paper:

"From Pareto Fronts to Decision Spaces: A Method-Agnostic Workflow for
Post-Optimization Decision Support in the Next Release Problem"

The script does not require the source code of the interactive prototype.
It works from exported CSV files only.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


EXPECTED_FILES = {
    "framed": "framed.csv",
    "domain": "domain.csv",
    "efficiency": "efficiency.csv",
    "hdbscan": "hdbscan.csv",
    "kmediods": "kmediods.csv",
    "topsis": "topsis.csv",
    "weight": "weight.csv",
    "con50": "con50.csv",
    "con75": "con75.csv",
    "con90": "con90.csv",
}

BASE_SOIS_FOR_CONSENSUS = [
    "domain",
    "efficiency",
    "hdbscan",
    "kmediods",
    "topsis",
    "weight",
]

COMPARISON_ORDER = [
    "framed",
    "domain",
    "efficiency",
    "hdbscan",
    "kmediods",
    "topsis",
    "weight",
    "con50",
    "con75",
    "con90",
]

PROFILE_COLS_CANDIDATES = [
    "satisfaction",
    "effort",
    "time",
    "productivity",
    "response",
    "opportunity",
    "scope",
    "squandering",
    "stcov_cv1",
    "stcov_cv2",
    "stcov_cv3",
    "stcov_cv4",
]

CONSENSUS_THRESHOLDS = [0.50, 0.75, 0.90]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate descriptive SOI metrics, consensus tables, and figures."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/sois"),
        help="Directory containing exported SOI CSV files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory where generated tables and figures will be written.",
    )
    parser.add_argument(
        "--no-figures",
        action="store_true",
        help="Generate only CSV/LaTeX tables and skip PNG figures.",
    )
    return parser.parse_args()


def read_sois(data_dir: Path) -> dict[str, pd.DataFrame]:
    sois: dict[str, pd.DataFrame] = {}

    for name, filename in EXPECTED_FILES.items():
        path = data_dir / filename

        if not path.exists():
            print(f"[MISS] {filename}")
            continue

        df = pd.read_csv(path)

        if "id" not in df.columns:
            print(f"[WARN] {filename} skipped: no 'id' column.")
            continue

        if df["id"].duplicated().any():
            duplicated = df.loc[df["id"].duplicated(), "id"].tolist()
            print(f"[WARN] {filename} contains duplicated IDs: {duplicated}")

        df["id"] = df["id"].astype(int)
        sois[name] = df
        print(f"[OK] loaded {name}: {df.shape[0]} rows")

    return sois


def get_req_cols(df: pd.DataFrame) -> listreturn [c for c in df.columns if re.match(r"^req_\d+$", c)]


def safe_id_set(df: pd.DataFrame) -> setreturn set(df["id"].dropna().astype(int).tolist())


def jaccard(a: set[int], b: set[int]) -> float:
    if not a and not b:
        return np.nan
    union = a | b
    return len(a & b) / len(union) if union else np.nan


def overlap_coeff(a: set[int], b: set[int]) -> float:
    if not a or not b:
        return np.nan
    return len(a & b) / min(len(a), len(b))


def containment(a: set[int], b: set[int]) -> float:
    """Proportion of A contained in B."""
    if not a:
        return np.nan
    return len(a & b) / len(a)


def requirement_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    req_cols = get_req_cols(df)
    n = len(df)

    if n == 0 or len(req_cols) == 0:
        return {
            "req_density": np.nan,
            "active_req_count": 0,
            "core_req_count": 0,
            "core_req_ratio": np.nan,
            "variable_req_count": 0,
            "req_variability": np.nan,
        }

    x = df[req_cols].astype(float)
    freq = x.mean(axis=0)

    active = freq > 0
    core = freq == 1
    variable = (freq > 0) & (freq < 1)

    active_count = int(active.sum())
    core_count = int(core.sum())

    variability = float((freq * (1 - freq)).mean())

    return {
        "req_density": float(x.values.mean()),
        "active_req_count": active_count,
        "core_req_count": core_count,
        "core_req_ratio": float(core_count / active_count) if active_count > 0 else np.nan,
        "variable_req_count": int(variable.sum()),
        "req_variability": variability,
    }


def objective_profile_metrics(
    df: pd.DataFrame,
    columns: list[str],
) -> dict[str, float]:
    out: dict[str, float] = {}

    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            out[f"{col}_mean"] = float(df[col].mean())
            out[f"{col}_std"] = float(df[col].std(ddof=0))
            out[f"{col}_min"] = float(df[col].min())
            out[f"{col}_max"] = float(df[col].max())
            out[f"{col}_spread"] = float(df[col].max() - df[col].min())

    return out


def compute_summary(sois: dict[str, pd.DataFrame]) -> pd.DataFrame:
    framed_size = len(sois["framed"]) if "framed" in sois else None

    id_to_sois: dict[int, list[str]] = {}
    for name, df in sois.items():
        for sid in safe_id_set(df):
            id_to_sois.setdefault(sid, []).append(name)

    rows = []

    for name in COMPARISON_ORDER:
        if name not in sois:
            continue

        df = sois[name]
        ids = safe_id_set(df)

        row = {
            "soi": name,
            "size": len(ids),
            "selectivity_vs_framed": len(ids) / framed_size if framed_size else np.nan,
        }

        unique_ids = [
            sid
            for sid in ids
            if len([x for x in id_to_sois.get(sid, []) if x != "framed"]) == 1
        ]

        row["unique_solution_count_excluding_framed"] = len(unique_ids)
        row.update(requirement_metrics(df))
        row.update(objective_profile_metrics(df, PROFILE_COLS_CANDIDATES))

        rows.append(row)

    return pd.DataFrame(rows)


def compute_pairwise(
    sois: dict[str, pd.DataFrame],
    metric: str = "jaccard",
) -> pd.DataFrame:
    names = [n for n in COMPARISON_ORDER if n in sois]
    sets = {n: safe_id_set(sois[n]) for n in names}

    matrix = pd.DataFrame(index=names, columns=names, dtype=float)

    for a in names:
        for b in names:
            if metric == "jaccard":
                matrix.loc[a, b] = jaccard(sets[a], sets[b])
            elif metric == "overlap":
                matrix.loc[a, b] = overlap_coeff(sets[a], sets[b])
            elif metric == "containment":
                matrix.loc[a, b] = containment(sets[a], sets[b])
            else:
                raise ValueError(f"Unknown metric: {metric}")

    return matrix


def compute_solution_consensus(
    sois: dict[str, pd.DataFrame],
    base_names: list[str],
) -> pd.DataFrame:
    present_base = [n for n in base_names if n in sois]

    if not present_base:
        raise ValueError("No base SOIs available for consensus.")

    all_ids = sorted(set().union(*[safe_id_set(sois[n]) for n in present_base]))

    rows = []
    for sid in all_ids:
        support_names = [n for n in present_base if sid in safe_id_set(sois[n])]
        consensus_score = len(support_names) / len(present_base)

        rows.append(
            {
                "id": sid,
                "consensus_score": consensus_score,
                "support_count": len(support_names),
                "support_names": ";".join(support_names),
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["consensus_score", "support_count", "id"],
        ascending=[False, False, True],
    )


def compute_requirement_frequency_by_soi(
    sois: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []

    for name in COMPARISON_ORDER:
        if name not in sois:
            continue

        df = sois[name]
        req_cols = get_req_cols(df)

        if not req_cols:
            continue

        freq = df[req_cols].mean(axis=0)

        for req, val in freq.items():
            rows.append(
                {
                    "soi": name,
                    "requirement": req,
                    "frequency": float(val),
                }
            )

    return pd.DataFrame(rows)


def save_heatmap(
    matrix: pd.DataFrame,
    output_path: Path,
    title: str,
    vmin: float = 0,
    vmax: float = 1,
) -> None:
    if matrix.empty:
        return

    fig_w = max(7, 0.55 * len(matrix.columns))
    fig_h = max(5, 0.45 * len(matrix.index))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    image = ax.imshow(matrix.values.astype(float), vmin=vmin, vmax=vmax, aspect="auto")

    ax.set_xticks(np.arange(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(matrix.index)))
    ax.set_yticklabels(matrix.index)

    ax.set_title(title, fontsize=12, fontweight="bold")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix.iloc[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_summary_bars(summary: pd.DataFrame, output_path: Path) -> None:
    if summary.empty:
        return

    plot_df = summary.copy().set_index("soi")
    cols = [
        "size",
        "selectivity_vs_framed",
        "core_req_ratio",
        "req_density",
        "req_variability",
    ]
    cols = [c for c in cols if c in plot_df.columns]

    fig, axes = plt.subplots(len(cols), 1, figsize=(9, 2.4 * len(cols)), sharex=True)

    if len(cols) == 1:
        axes = [axes]

    for ax, col in zip(axes, cols):
        ax.bar(plot_df.index, plot_df[col])
        ax.set_ylabel(col)
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("SOI descriptive characterization", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_requirement_frequency_heatmap(
    req_freq: pd.DataFrame,
    output_path: Path,
) -> None:
    if req_freq.empty:
        return

    mat = req_freq.pivot(index="soi", columns="requirement", values="frequency")
    req_cols = sorted(mat.columns, key=lambda x: int(x.split("_")[1]))
    mat = mat[req_cols]

    fig_w = max(12, 0.28 * len(req_cols))
    fig_h = max(4, 0.45 * len(mat.index))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    image = ax.imshow(mat.values, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(np.arange(len(req_cols)))
    ax.set_xticklabels(req_cols, rotation=65, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(mat.index)))
    ax.set_yticklabels(mat.index)

    ax.set_title("Requirement inclusion frequency by SOI", fontsize=12, fontweight="bold")
    fig.colorbar(image, ax=ax, fraction=0.02, pad=0.02)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_solution_consensus_membership(
    sois: dict[str, pd.DataFrame],
    consensus_df: pd.DataFrame,
    base_names: list[str],
    output_path: Path,
    max_solutions: int = 60,
) -> None:
    present_base = [n for n in base_names if n in sois]

    if not present_base or consensus_df.empty:
        return

    top_ids = consensus_df.head(max_solutions)["id"].tolist()

    data = []
    for sid in top_ids:
        row = []
        for name in present_base:
            row.append(1 if sid in safe_id_set(sois[name]) else 0)
        data.append(row)

    mat = pd.DataFrame(data, index=[str(x) for x in top_ids], columns=present_base)

    fig_w = max(7, 0.6 * len(present_base))
    fig_h = max(6, 0.18 * len(top_ids))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.imshow(mat.values, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(np.arange(len(mat.columns)))
    ax.set_xticklabels(mat.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(mat.index)))
    ax.set_yticklabels(mat.index, fontsize=7)

    ax.set_ylabel("Solution ID")
    ax.set_title("Solution membership across base SOIs", fontsize=12, fontweight="bold")

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()

    data_dir = args.data_dir
    out_dir = args.out_dir
    table_dir = out_dir / "tables"
    figure_dir = out_dir / "figures"

    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    sois = read_sois(data_dir)

    if not sois:
        raise SystemExit("No SOI CSV files found.")

    if "framed" not in sois:
        print("[WARN] framed.csv not found. Selectivity vs framed will be NaN.")

    summary = compute_summary(sois)
    summary.to_csv(table_dir / "out_soi_summary.csv", index=False)

    latex_cols = [
        "soi",
        "size",
        "selectivity_vs_framed",
        "active_req_count",
        "core_req_count",
        "core_req_ratio",
        "req_density",
        "req_variability",
    ]
    latex_cols = [c for c in latex_cols if c in summary.columns]

    summary[latex_cols].to_latex(
        table_dir / "out_soi_metrics_latex.tex",
        index=False,
        float_format="%.3f",
    )

    pairwise_jaccard = compute_pairwise(sois, "jaccard")
    pairwise_overlap = compute_pairwise(sois, "overlap")
    pairwise_containment = compute_pairwise(sois, "containment")

    pairwise_jaccard.to_csv(table_dir / "out_pairwise_jaccard.csv")
    pairwise_overlap.to_csv(table_dir / "out_pairwise_overlap.csv")
    pairwise_containment.to_csv(table_dir / "out_pairwise_containment.csv")

    present_base = [n for n in BASE_SOIS_FOR_CONSENSUS if n in sois]

    if present_base:
        consensus_df = compute_solution_consensus(sois, BASE_SOIS_FOR_CONSENSUS)

        for tau in CONSENSUS_THRESHOLDS:
            consensus_df[f"in_consensus_{tau:.2f}"] = (
                consensus_df["consensus_score"] >= tau
            )

        consensus_df.to_csv(table_dir / "out_consensus_by_solution.csv", index=False)

        consensus_rows = []
        for tau in CONSENSUS_THRESHOLDS:
            n_tau = int((consensus_df["consensus_score"] >= tau).sum())
            consensus_rows.append(
                {
                    "tau": tau,
                    "consensus_size": n_tau,
                    "interpretation": (
                        "broad consensus pool" if tau < 0.75 else "compact consensus core"
                    ),
                }
            )

        consensus_sizes = pd.DataFrame(consensus_rows)
        consensus_sizes.to_csv(table_dir / "out_consensus_sizes.csv", index=False)
        consensus_sizes.to_latex(
            table_dir / "out_consensus_sizes_latex.tex",
            index=False,
            float_format="%.2f",
        )

    else:
        consensus_df = pd.DataFrame()
        print("[WARN] No base SOIs found for consensus calculation.")

    req_freq = compute_requirement_frequency_by_soi(sois)
    req_freq.to_csv(table_dir / "out_requirement_frequency_by_soi.csv", index=False)

    if not args.no_figures:
        save_heatmap(
            pairwise_jaccard,
            figure_dir / "fig_pairwise_jaccard.png",
            "Pairwise Jaccard similarity",
        )
        save_heatmap(
            pairwise_overlap,
            figure_dir / "fig_pairwise_overlap.png",
            "Pairwise overlap coefficient",
        )
        plot_summary_bars(
            summary,
            figure_dir / "fig_soi_summary_bars.png",
        )
        plot_requirement_frequency_heatmap(
            req_freq,
            figure_dir / "fig_requirement_frequency_heatmap.png",
        )

        if not consensus_df.empty:
            plot_solution_consensus_membership(
                sois,
                consensus_df,
                BASE_SOIS_FOR_CONSENSUS,
                figure_dir / "fig_solution_consensus_membership.png",
            )

    print("\nGenerated outputs:")
    for path in sorted(table_dir.glob("*")) + sorted(figure_dir.glob("*")):
        print(f" - {path}")


if __name__ == "__main__":
    main()
    