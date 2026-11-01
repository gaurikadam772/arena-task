"""Create the four charts: line, horizontal bar, histogram and heatmap."""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend: no display needed
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize  # noqa: E402
from matplotlib.ticker import FuncFormatter, MaxNLocator  # noqa: E402

from .config import (  # noqa: E402
    BASELINE, BLUE, BLUE_RAMP, GRID, MUTED, SURFACE, TEXT_PRIMARY, TEXT_SECONDARY,
)

logger = logging.getLogger(__name__)

plt.rcParams.update({
    "font.family": "sans-serif",
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def _money_compact(x: float, _pos=None) -> str:
    if abs(x) >= 1_000_000:
        return f"${x / 1_000_000:.1f}M"
    if abs(x) >= 1_000:
        k = x / 1_000
        return f"${k:.0f}K" if abs(k - round(k)) < 1e-9 else f"${k:.1f}K"
    return f"${x:.0f}"


def _style_axes(ax, grid_axis: str = "y") -> None:
    """Quiet chrome: hairline grid, one baseline, no box."""
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=MUTED, length=0, labelsize=10)
    ax.grid(axis=grid_axis, color=GRID, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)


def _title(ax, title: str, subtitle: str) -> None:
    ax.text(0, 1.15, title, transform=ax.transAxes, fontsize=15, fontweight="bold",
            color=TEXT_PRIMARY, ha="left", va="bottom")
    ax.text(0, 1.07, subtitle, transform=ax.transAxes, fontsize=10.5,
            color=TEXT_SECONDARY, ha="left", va="bottom")


def _save(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    logger.info("Saved %s", path.name)
    return path


def plot_monthly_revenue(monthly: pd.DataFrame, out_dir: Path) -> Path:
    """Line chart: revenue per month (peak and latest month labelled)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(monthly))
    y = monthly["revenue"].to_numpy()
    ax.fill_between(x, y, color=BLUE, alpha=0.10, linewidth=0)
    ax.plot(x, y, color=BLUE, linewidth=2, solid_capstyle="round", solid_joinstyle="round")
    ax.plot(x, y, "o", markersize=8, color=BLUE, markeredgecolor=SURFACE, markeredgewidth=2)

    for idx in sorted({int(np.argmax(y)), len(y) - 1}):
        ax.annotate(f"${y[idx]:,.0f}", (x[idx], y[idx]), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=10, fontweight="bold",
                    color=TEXT_PRIMARY)

    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%b") for d in monthly.index])
    ax.set_ylim(0, y.max() * 1.22)
    ax.yaxis.set_major_formatter(FuncFormatter(_money_compact))
    _style_axes(ax, "y")
    _title(ax, "Monthly revenue", "Total revenue per calendar month (USD)")
    return _save(fig, out_dir / "monthly_revenue_line.png")


def plot_category_revenue(by_category: pd.DataFrame, out_dir: Path) -> Path:
    """Horizontal bar chart: revenue per category with share labels at the tip."""
    data = by_category.sort_values("revenue")  # largest ends up on top
    fig, ax = plt.subplots(figsize=(9, 4.5))
    y = np.arange(len(data))
    values = data["revenue"].to_numpy()
    ax.barh(y, values, height=0.5, color=BLUE)
    for yi, v, share in zip(y, values, data["revenue_share_pct"]):
        ax.text(v + values.max() * 0.015, yi, f"${v:,.0f}  ({share:.1f}%)", va="center",
                fontsize=10, color=TEXT_PRIMARY)
    ax.set_yticks(y)
    ax.set_yticklabels(data.index, fontsize=11, color=TEXT_SECONDARY)
    ax.set_xlim(0, values.max() * 1.3)
    ax.xaxis.set_major_formatter(FuncFormatter(_money_compact))
    _style_axes(ax, "x")
    _title(ax, "Revenue by category", "Total revenue and share of overall revenue")
    return _save(fig, out_dir / "category_revenue_bar.png")


def plot_order_value_histogram(df: pd.DataFrame, out_dir: Path, bin_width: int = 250) -> Path:
    """Histogram: distribution of order values with the median marked."""
    values = df["revenue"].to_numpy()
    edges = np.arange(0, np.ceil(values.max() / bin_width) * bin_width + bin_width, bin_width)
    fig, ax = plt.subplots(figsize=(9, 5))
    counts, _, _ = ax.hist(values, bins=edges, color=BLUE, edgecolor=SURFACE, linewidth=2)
    median = float(np.median(values))
    ax.axvline(median, color=TEXT_SECONDARY, linewidth=1.5)
    ax.set_ylim(0, counts.max() * 1.25)
    ax.text(median + bin_width * 0.1, counts.max() * 1.14, f"Median ${median:,.0f}",
            fontsize=10, fontweight="bold", color=TEXT_SECONDARY, va="center")
    ax.xaxis.set_major_formatter(FuncFormatter(_money_compact))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Order value (USD)", color=MUTED, fontsize=10)
    ax.set_ylabel("Number of orders", color=MUTED, fontsize=10)
    _style_axes(ax, "y")
    _title(ax, "Distribution of order values",
           f"Orders grouped into ${bin_width} bands; most orders are small, a few are very large")
    return _save(fig, out_dir / "order_value_histogram.png")


def plot_category_month_heatmap(pivot: pd.DataFrame, out_dir: Path) -> Path:
    """Heatmap: revenue for every category x month (single-hue sequential scale)."""
    data = pivot.to_numpy()
    cmap = LinearSegmentedColormap.from_list("blue_seq", BLUE_RAMP)
    norm = Normalize(vmin=0, vmax=data.max())
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    mesh = ax.pcolormesh(data, cmap=cmap, norm=norm, edgecolors=SURFACE, linewidth=2)
    ax.invert_yaxis()

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            r, g, b, _ = cmap(norm(data[i, j]))
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            val = data[i, j]
            label = "-" if not val else (f"${val / 1000:.1f}K" if val >= 1000 else f"${val:,.0f}")
            ax.text(j + 0.5, i + 0.5, label,
                    ha="center", va="center", fontsize=9.5, fontweight="bold",
                    color="#ffffff" if lum < 0.5 else TEXT_PRIMARY)

    ax.set_xticks(np.arange(data.shape[1]) + 0.5)
    ax.set_xticklabels([pd.Timestamp(c).strftime("%b") for c in pivot.columns])
    ax.set_yticks(np.arange(data.shape[0]) + 0.5)
    ax.set_yticklabels(pivot.index, fontsize=11, color=TEXT_SECONDARY)
    ax.tick_params(colors=MUTED, length=0, labelsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(mesh, ax=ax, fraction=0.035, pad=0.02)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(colors=MUTED, length=0, labelsize=9)
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(_money_compact))
    _title(ax, "Revenue by category and month", "Darker = more revenue (USD)")
    return _save(fig, out_dir / "category_month_heatmap.png")


def create_all_charts(results: dict, df: pd.DataFrame, out_dir: str | Path) -> dict[str, Path]:
    """Create every chart and return ``{name: path}``."""
    out_dir = Path(out_dir)
    return {
        "monthly_line": plot_monthly_revenue(results["monthly"], out_dir),
        "category_bar": plot_category_revenue(results["by_category"], out_dir),
        "order_histogram": plot_order_value_histogram(df, out_dir),
        "heatmap": plot_category_month_heatmap(results["pivot"], out_dir),
    }
