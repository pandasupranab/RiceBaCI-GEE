"""Re-render fig6_placebo_distribution.png/pdf from existing CSVs.

Avoids re-running the full placebo permutation pipeline.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

# importlib import because module name starts with a digit
import importlib.util
spec = importlib.util.spec_from_file_location(
    "placebo_mod", str(ROOT / "analysis" / "05e_placebo_tests.py")
)
mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(mod)  # type: ignore[union-attr]

RESULTS = ROOT / "analysis" / "results" / "real_v21"
FIG_DIR = ROOT / "figures"

perm_df = pd.read_csv(RESULTS / "placebo_in_space.csv")
summary_df = pd.read_csv(RESULTS / "placebo_summary.csv")
static_df = pd.read_csv(RESULTS / "did_static.csv")

mod.make_figure(perm_df, summary_df, FIG_DIR, static_df=static_df)
print(f"re-rendered figures/fig6_placebo_distribution.{{png,pdf}}")
