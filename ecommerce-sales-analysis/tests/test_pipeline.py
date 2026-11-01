"""Tests for loading, cleaning, analysis, charts and the end-to-end pipeline."""
import pandas as pd
import pytest

from main import main
from src.analyzer import run_analysis
from src.config import DEFAULT_INPUT
from src.data_loader import DataValidationError, clean_data, load_data
from src.report import describe_correlation
from src.visualizer import create_all_charts


@pytest.fixture
def raw_df():
    return pd.DataFrame({
        "date": ["2026-01-05", "2026-01-20", "2026-02-03", "2026-02-03", "2026-03-10", "2026-03-11"],
        "product": ["Laptop", "Pen Set", "Jeans", "Jeans", "Laptop", "Pen Set"],
        "category": ["Electronics", "Stationery", "Clothing", "Clothing", "Electronics", "Stationery"],
        "quantity": [1, 5, 2, 2, 2, 4],
        "unit_price": [800.0, 12.0, 45.0, 45.0, 810.0, 11.5],
    })


@pytest.fixture
def clean_df(raw_df):
    return clean_data(raw_df)[0]


# ---------- loading & validation ----------
def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path / "nope.csv")


def test_load_empty_file_raises(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("")
    with pytest.raises(DataValidationError):
        load_data(f)


def test_load_missing_columns_raises(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("date,product\n2026-01-01,Laptop\n")
    with pytest.raises(DataValidationError, match="Missing required column"):
        load_data(f)


def test_load_real_dataset_shape():
    df = load_data(DEFAULT_INPUT)
    assert df.shape == (100, 5)


# ---------- cleaning ----------
def test_clean_removes_duplicates(raw_df):
    clean, log = clean_data(raw_df)
    assert log["duplicates_removed"] == 1
    assert len(clean) == 5


def test_clean_removes_missing_and_invalid(raw_df):
    raw_df.loc[0, "quantity"] = None
    raw_df.loc[1, "date"] = "not a date"
    clean, log = clean_data(raw_df)
    assert log["missing_or_invalid_removed"] == 2
    assert clean["quantity"].notna().all()


def test_clean_removes_non_positive(raw_df):
    raw_df.loc[0, "quantity"] = 0
    raw_df.loc[4, "unit_price"] = -5
    _, log = clean_data(raw_df)
    assert log["non_positive_removed"] == 2


def test_clean_all_rows_invalid_raises(raw_df):
    raw_df["quantity"] = -1
    with pytest.raises(DataValidationError):
        clean_data(raw_df)


def test_revenue_is_quantity_times_price(clean_df):
    assert (clean_df["revenue"] == (clean_df["quantity"] * clean_df["unit_price"]).round(2)).all()


# ---------- analysis ----------
def test_totals_are_consistent(clean_df):
    r = run_analysis(clean_df)
    total = r["summary"]["total_revenue"]
    assert total == pytest.approx(clean_df["revenue"].sum())
    assert r["by_category"]["revenue"].sum() == pytest.approx(total)
    assert r["by_product"]["revenue"].sum() == pytest.approx(total)
    assert r["monthly"]["revenue"].sum() == pytest.approx(total)
    assert r["pivot"].to_numpy().sum() == pytest.approx(total)


def test_shares_sum_to_100(clean_df):
    r = run_analysis(clean_df)
    assert r["by_category"]["revenue_share_pct"].sum() == pytest.approx(100)
    assert r["by_category"]["order_share_pct"].sum() == pytest.approx(100)


def test_known_values(clean_df):
    r = run_analysis(clean_df)
    # Laptop: 1*800 + 2*810 = 2420 is the top category (Electronics)
    assert r["by_category"].index[0] == "Electronics"
    assert r["by_category"].loc["Electronics", "revenue"] == pytest.approx(2420.0)
    assert r["summary"]["total_orders"] == 5


def test_describe_correlation():
    assert describe_correlation(-0.7) == "strong negative"
    assert describe_correlation(0.1) == "negligible"
    assert describe_correlation(float("nan")) == "undefined"


# ---------- charts & end-to-end ----------
def test_charts_are_created(clean_df, tmp_path):
    charts = create_all_charts(run_analysis(clean_df), clean_df, tmp_path)
    assert len(charts) == 4
    for path in charts.values():
        assert path.exists() and path.stat().st_size > 1000


def test_full_pipeline_on_real_data(tmp_path):
    assert main(["--input", str(DEFAULT_INPUT), "--output-dir", str(tmp_path)]) == 0
    assert (tmp_path / "report" / "report.md").exists()
    assert (tmp_path / "data" / "sales_data_clean.csv").exists()
    assert len(list((tmp_path / "visualizations").glob("*.png"))) == 4


def test_pipeline_exit_code_missing_file(tmp_path):
    assert main(["--input", str(tmp_path / "missing.csv"), "--output-dir", str(tmp_path)]) == 1


def test_pipeline_exit_code_bad_schema(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b\n1,2\n")
    assert main(["--input", str(bad), "--output-dir", str(tmp_path)]) == 2
