"""Turn analysis results into written insights and a Markdown report."""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def describe_correlation(rho: float) -> str:
    """Plain-English label for a correlation coefficient."""
    if rho != rho:  # NaN
        return "undefined"
    size = abs(rho)
    strength = ("negligible" if size < 0.2 else "weak" if size < 0.4
                else "moderate" if size < 0.6 else "strong")
    direction = "negative" if rho < 0 else "positive"
    return strength if strength == "negligible" else f"{strength} {direction}"


def build_insights(results: dict) -> list[dict]:
    """Write the findings as ``{"key", "title", "text"}`` dicts, with numbers from the data."""
    s = results["summary"]
    cat = results["by_category"]
    prod = results["by_product"]
    monthly = results["monthly"]
    dist = results["distribution"]
    pivot = results["pivot"]
    rho = results["price_qty_corr"]

    top_cat, bottom_cat = cat.iloc[0], cat.iloc[-1]
    best_m, worst_m = monthly["revenue"].idxmax(), monthly["revenue"].idxmin()
    cv = monthly["revenue"].std() / monthly["revenue"].mean() * 100
    avg_orders = monthly["orders"].mean()
    first, last = monthly["revenue"].iloc[0], monthly["revenue"].iloc[-1]
    bands = results["price_bands"]
    top3 = prod.head(3)

    # Heatmap facts: biggest category-month cell and how stable the rankings are
    values = pivot.to_numpy()
    peak_row, peak_col = np.unravel_index(np.argmax(values), values.shape)
    peak_cat, peak_month, peak_val = pivot.index[peak_row], pivot.columns[peak_col], values[peak_row, peak_col]
    others = np.delete(values[peak_row], peak_col)
    peak_ratio = peak_val / others.mean() if len(others) and others.mean() > 0 else float("nan")
    n_months = pivot.shape[1]
    lead_months = int((pivot.idxmax(axis=0) == top_cat.name).sum())
    trail_months = int((pivot.idxmin(axis=0) == bottom_cat.name).sum())
    spike_note = (
        " Much of the early-year strength in the line chart therefore comes from one category "
        "in one month rather than from broad growth." if peak_month == best_m else "")

    return [
        {"key": "category", "title": "Revenue is driven by a few categories", "text": (
            f"{top_cat.name} brings in {top_cat['revenue_share_pct']:.1f}% of revenue "
            f"(${top_cat['revenue']:,.0f}) from only {top_cat['order_share_pct']:.1f}% of orders, "
            f"with an average order of ${top_cat['avg_order_value']:,.0f}. "
            f"{bottom_cat.name} is the smallest category at {bottom_cat['revenue_share_pct']:.1f}% "
            f"of revenue even though it makes up {bottom_cat['order_share_pct']:.1f}% of orders. "
            "Order count alone is therefore a poor guide to where the money comes from.")},
        {"key": "products", "title": "Three products account for most of the revenue", "text": (
            f"The top three products ({', '.join(top3.index)}) generate "
            f"{results['top3_product_share_pct']:.1f}% of total revenue across "
            f"{s['n_products']} products. {top3.index[0]} alone contributes "
            f"{top3['revenue_share_pct'].iloc[0]:.1f}%. Stock, pricing and marketing "
            "decisions for these items have an outsized effect on results.")},
        {"key": "monthly", "title": "Monthly revenue is uneven", "text": (
            f"{best_m:%B} was the strongest month (${monthly.loc[best_m, 'revenue']:,.0f}) and "
            f"{worst_m:%B} the weakest (${monthly.loc[worst_m, 'revenue']:,.0f}). "
            f"Revenue moved from ${first:,.0f} in {monthly.index[0]:%B} to ${last:,.0f} in "
            f"{monthly.index[-1]:%B}, and month-to-month variation is large "
            f"(coefficient of variation {cv:.0f}%). With only about {avg_orders:.0f} orders per "
            "month, a handful of high-value sales can swing a month, so single-month changes "
            "should be read cautiously rather than as a firm trend.")},
        {"key": "distribution", "title": "A small share of orders produces a large share of revenue", "text": (
            f"The average order is ${dist['mean']:,.0f} but the median is only "
            f"${dist['median']:,.0f} ({dist['mean_to_median']:.1f}x lower), so the distribution is "
            f"right-skewed (skew {dist['skew']:.1f}). Orders of ${dist['high_ticket_threshold']:,} or more "
            f"are {dist['high_ticket_order_share_pct']:.1f}% of orders "
            f"({dist['high_ticket_orders']} orders) but {dist['high_ticket_revenue_share_pct']:.1f}% "
            "of revenue. The median is the better description of a typical order.")},
        {"key": "price_qty", "title": "Cheaper items are bought in larger quantities", "text": (
            f"Unit price and units per order show a {describe_correlation(rho)} relationship "
            f"(Spearman rho = {rho:.2f}). Orders for items priced below the median unit price "
            f"(${bands['median_price']:,.0f}) average {bands['low_avg_units']:.1f} units, versus "
            f"{bands['high_avg_units']:.1f} units for items priced at or above it. "
            "This is a correlation in this sample, not proof of cause.")},
        {"key": "heatmap", "title": f"Biggest category-month result: {peak_cat} in {peak_month:%B}", "text": (
            f"The single biggest category-month cell is {peak_cat} in {peak_month:%B} "
            f"(${peak_val:,.0f}), about {peak_ratio:.1f}x that category's average in its other months. "
            f"{top_cat.name} is the top category in {lead_months} of {n_months} months and "
            f"{bottom_cat.name} is last in {trail_months} of {n_months}.{spike_note}")},
    ]


def build_recommendations(results: dict) -> list[str]:
    cat = results["by_category"]
    prod = results["by_product"]
    return [
        f"Protect the core: keep {', '.join(prod.index[:3])} well stocked and competitively priced, "
        f"because they carry {results['top3_product_share_pct']:.0f}% of revenue.",
        f"Grow {cat.index[-1]} through bundling or cross-selling with larger orders; it has many orders "
        "but contributes little revenue.",
        "Track revenue with a rolling 3-month average and report order counts beside revenue, "
        "so one large order does not look like a trend.",
        "Collect more history (a full year or more) before judging seasonality.",
    ]


def write_report(results: dict, cleaning_log: dict, chart_paths: dict, out_path: str | Path) -> Path:
    """Write ``report.md`` combining metrics, charts and insights."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    s = results["summary"]
    insights = build_insights(results)
    by_key = {i["key"]: i for i in insights}
    rel = lambda name: f"../visualizations/{Path(chart_paths[name]).name}"  # noqa: E731

    cat_rows = "\n".join(
        f"| {n} | ${r.revenue:,.0f} | {r.revenue_share_pct:.1f}% | {int(r.orders)} | ${r.avg_order_value:,.0f} |"
        for n, r in results["by_category"].iterrows())
    prod_rows = "\n".join(
        f"| {n} | {r.category} | ${r.revenue:,.0f} | {r.revenue_share_pct:.1f}% | {int(r.units)} |"
        for n, r in results["by_product"].head(5).iterrows())

    def section(key: str, chart: str, alt: str) -> str:
        i = by_key[key]
        return f"### {i['title']}\n\n![{alt}]({rel(chart)})\n\n{i['text']}\n"

    lines = [
        "# E-commerce Sales Analysis - Report\n",
        f"Period analysed: **{s['date_start']:%d %b %Y} to {s['date_end']:%d %b %Y}** "
        f"({s['total_orders']} orders, {s['n_products']} products, {s['n_categories']} categories).\n",
        "## 1. Headline numbers\n",
        "| Metric | Value |\n|---|---|",
        f"| Total revenue | ${s['total_revenue']:,.0f} |",
        f"| Orders | {s['total_orders']} |",
        f"| Units sold | {s['total_units']} |",
        f"| Average order value | ${s['avg_order_value']:,.0f} |",
        f"| Median order value | ${s['median_order_value']:,.0f} |",
        f"| Largest order | ${s['max_order_value']:,.0f} |\n",
        "## 2. Data preparation\n",
        f"The raw file had {cleaning_log['rows_raw']} rows. After cleaning, "
        f"{cleaning_log['rows_clean']} rows remain "
        f"({cleaning_log['duplicates_removed']} duplicate, "
        f"{cleaning_log['missing_or_invalid_removed']} missing/invalid and "
        f"{cleaning_log['non_positive_removed']} non-positive rows removed). "
        "Revenue was calculated as quantity x unit price.\n",
        "## 3. Findings\n",
        section("category", "category_bar", "Bar chart of revenue by category"),
        "| Category | Revenue | Share | Orders | Avg order |\n|---|---|---|---|---|",
        cat_rows + "\n",
        f"**{by_key['products']['title']}.** {by_key['products']['text']}\n",
        "| Product | Category | Revenue | Share | Units |\n|---|---|---|---|---|",
        prod_rows + "\n",
        section("monthly", "monthly_line", "Line chart of monthly revenue"),
        section("distribution", "order_histogram", "Histogram of order values"),
        f"**{by_key['price_qty']['title']}.** {by_key['price_qty']['text']}\n",
        section("heatmap", "heatmap", "Heatmap of revenue by category and month"),
        "## 4. Recommendations\n",
        "\n".join(f"{n}. {t}" for n, t in enumerate(build_recommendations(results), 1)) + "\n",
        "## 5. Limitations\n",
        "- The sample is small (under 100 orders over six months), so percentages can shift noticeably "
        "with a few extra orders.\n"
        "- There is no order or customer id, so identical rows were treated as duplicates and "
        "customer-level analysis (repeat buyers, lifetime value) is not possible.\n"
        "- The dataset in `data/` is a synthetic practice file with deliberate quality issues; "
        "conclusions describe this data, not a real business.\n",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Report written to %s", out_path)
    return out_path
