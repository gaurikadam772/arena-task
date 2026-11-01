"""Compute the sales metrics and patterns used in the report."""
from __future__ import annotations

import logging

import pandas as pd

from .config import HIGH_TICKET_THRESHOLD

logger = logging.getLogger(__name__)


def summary_metrics(df: pd.DataFrame) -> dict:
    """Headline KPIs for the whole period."""
    revenue = df["revenue"]
    return {
        "total_revenue": float(revenue.sum()),
        "total_orders": int(len(df)),
        "total_units": int(df["quantity"].sum()),
        "avg_order_value": float(revenue.mean()),
        "median_order_value": float(revenue.median()),
        "max_order_value": float(revenue.max()),
        "date_start": df["date"].min(),
        "date_end": df["date"].max(),
        "n_products": int(df["product"].nunique()),
        "n_categories": int(df["category"].nunique()),
    }


def _group_summary(df: pd.DataFrame, key: str) -> pd.DataFrame:
    g = df.groupby(key).agg(
        revenue=("revenue", "sum"),
        orders=("revenue", "size"),
        units=("quantity", "sum"),
        avg_order_value=("revenue", "mean"),
    )
    g["revenue_share_pct"] = g["revenue"] / g["revenue"].sum() * 100
    g["order_share_pct"] = g["orders"] / g["orders"].sum() * 100
    return g.sort_values("revenue", ascending=False)


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return _group_summary(df, "category")


def revenue_by_product(df: pd.DataFrame) -> pd.DataFrame:
    out = _group_summary(df, "product")
    out["category"] = df.groupby("product")["category"].first()
    return out


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and order count per calendar month, plus month-over-month growth."""
    m = df.groupby("month").agg(revenue=("revenue", "sum"), orders=("revenue", "size"))
    m["mom_growth_pct"] = m["revenue"].pct_change() * 100
    return m


def category_month_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue matrix: categories (rows, biggest first) x months (columns)."""
    pivot = df.pivot_table(
        index="category", columns="month", values="revenue", aggfunc="sum", fill_value=0.0
    )
    return pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]


def order_value_distribution(df: pd.DataFrame) -> dict:
    """Shape of the order-value distribution and the weight of high-ticket orders."""
    rev = df["revenue"]
    high = rev >= HIGH_TICKET_THRESHOLD
    return {
        "mean": float(rev.mean()),
        "median": float(rev.median()),
        "mean_to_median": float(rev.mean() / rev.median()),
        "skew": float(rev.skew()),
        "high_ticket_threshold": HIGH_TICKET_THRESHOLD,
        "high_ticket_orders": int(high.sum()),
        "high_ticket_order_share_pct": float(high.mean() * 100),
        "high_ticket_revenue_share_pct": float(rev[high].sum() / rev.sum() * 100),
    }


def price_quantity_correlation(df: pd.DataFrame) -> float:
    """Spearman rank correlation between unit price and units per order."""
    if df["unit_price"].nunique() < 2 or df["quantity"].nunique() < 2:
        return float("nan")
    return float(df["unit_price"].corr(df["quantity"], method="spearman"))


def units_by_price_band(df: pd.DataFrame) -> dict:
    """Average units per order below vs at/above the median unit price."""
    median_price = float(df["unit_price"].median())
    low = df[df["unit_price"] < median_price]["quantity"]
    high = df[df["unit_price"] >= median_price]["quantity"]
    return {
        "median_price": median_price,
        "low_avg_units": float(low.mean()) if len(low) else float("nan"),
        "high_avg_units": float(high.mean()) if len(high) else float("nan"),
    }


def run_analysis(df: pd.DataFrame) -> dict:
    """Run every analysis step and return the results in one dictionary."""
    by_product = revenue_by_product(df)
    results = {
        "summary": summary_metrics(df),
        "by_category": revenue_by_category(df),
        "by_product": by_product,
        "monthly": monthly_revenue(df),
        "pivot": category_month_pivot(df),
        "distribution": order_value_distribution(df),
        "price_qty_corr": price_quantity_correlation(df),
        "price_bands": units_by_price_band(df),
        "top3_product_share_pct": float(by_product["revenue_share_pct"].head(3).sum()),
    }
    logger.info("Analysis complete: total revenue %.2f", results["summary"]["total_revenue"])
    return results
