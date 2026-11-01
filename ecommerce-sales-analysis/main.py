"""E-commerce sales analysis pipeline: load -> clean -> analyze -> visualize -> report.

Usage:
    python main.py                              # uses data/sales_data.csv
    python main.py --input path/to/file.csv     # analyse another file
    python main.py --output-dir out/            # write outputs elsewhere

Exit codes: 0 success, 1 input file not found, 2 invalid data, 99 unexpected error.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.analyzer import run_analysis
from src.config import BASE_DIR, DEFAULT_INPUT
from src.data_loader import DataValidationError, clean_data, load_data
from src.report import write_report
from src.visualizer import create_all_charts

logger = logging.getLogger("pipeline")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="E-commerce sales analysis pipeline")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="path to the sales CSV")
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR,
                        help="folder that receives data/, visualizations/ and report/ outputs")
    return parser.parse_args(argv)


def run_pipeline(input_path: Path, output_dir: Path) -> dict:
    """Run every stage and return the key outputs."""
    raw = load_data(input_path)
    clean, cleaning_log = clean_data(raw)

    clean_path = output_dir / "data" / "sales_data_clean.csv"
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    clean.drop(columns=["month"]).to_csv(clean_path, index=False)

    results = run_analysis(clean)
    charts = create_all_charts(results, clean, output_dir / "visualizations")
    report_path = write_report(results, cleaning_log, charts, output_dir / "report" / "report.md")
    return {"results": results, "cleaning_log": cleaning_log, "charts": charts,
            "report": report_path, "clean_data": clean_path}


def main(argv=None) -> int:
    args = parse_args(argv)
    (args.output_dir / "report").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, force=True,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout),
                  logging.FileHandler(args.output_dir / "report" / "pipeline.log", mode="w")],
    )
    try:
        out = run_pipeline(args.input, args.output_dir)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1
    except DataValidationError as exc:
        logger.error("Invalid data: %s", exc)
        return 2
    except Exception:  # noqa: BLE001 - last-resort guard so the user gets a clear message
        logger.exception("Unexpected error")
        return 99

    s = out["results"]["summary"]
    logger.info("Done. Revenue $%.0f from %d orders. Report: %s",
                s["total_revenue"], s["total_orders"], out["report"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
