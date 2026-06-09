"""Re-render fig5_power_curves.png/pdf from existing CSVs."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

spec = importlib.util.spec_from_file_location(
    "power_mod", str(ROOT / "analysis" / "09_power_analysis.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RESULTS = ROOT / "analysis" / "results" / "real_v21"
FIG_DIR = ROOT / "figures"

curves = pd.read_csv(RESULTS / "power_curves.csv")
mde = pd.read_csv(RESULTS / "power_mde.csv")
mod.make_figure(curves, mde, FIG_DIR)
print("re-rendered figures/fig5_power_curves.{png,pdf}")
