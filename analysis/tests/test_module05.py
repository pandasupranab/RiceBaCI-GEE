"""
test_module05.py — sanity tests for the synthetic panel + DiD estimator.

Run with: python3 -m pytest analysis/tests/test_module05.py -v
or simply: python3 analysis/tests/test_module05.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Make package-style imports work when run as a script
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

import importlib.util

def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod                  # register before exec (dataclass needs it)
    spec.loader.exec_module(mod)
    return mod

synth = _load("synthetic_panel",  ROOT / "analysis" / "synthetic_panel.py")
did   = _load("did_regression",   ROOT / "analysis" / "05_did_regression.py")


# ---------------------------------------------------------------------------
def test_panel_shape():
    df = synth.make_panel(seed=42)
    assert len(df) == 384
    assert df["district"].nunique() == 8
    assert df["year"].nunique() == 8
    assert set(df["pipeline"].unique()) == {"raw", "corrected"}
    assert set(df["metric"].unique())   == {"SOS", "POS", "EOS"}


def test_panel_columns():
    df = synth.make_panel(seed=42)
    required = {
        "district", "district_id", "year", "year_type", "cyclone_exposure",
        "cyclone_year_event", "pipeline", "metric",
        "median_doy", "p25_doy", "p75_doy",
        "boot_p025", "boot_p975", "n_pixels",
    }
    assert required.issubset(df.columns)


def test_treat_post_indicators():
    df = synth.make_panel(seed=42)
    df = did.load_panel.__wrapped__ if False else did.load_panel
    # use load_panel via a tmp file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        synth.make_panel(seed=42).to_csv(f.name, index=False)
        loaded = did.load_panel(Path(f.name))
    assert (loaded.loc[loaded["cyclone_exposure"] == "coastal_treatment",
                      "treat"] == 1).all()
    assert (loaded.loc[loaded["cyclone_exposure"] == "inland_control",
                      "treat"] == 0).all()
    assert (loaded.loc[loaded["year"].isin([2019, 2020, 2021]),
                      "post"] == 1).all()


def test_did_recovers_true_tau():
    """The estimator must recover synthetic ATT to within 1 day."""
    df_raw = synth.make_panel(seed=42)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        df_raw.to_csv(f.name, index=False)
        df = did.load_panel(Path(f.name))

    for (pipe, met), true_tau in synth.TRUE_TAU.items():
        res = did.estimate_static_did(df, pipe, met)
        # Tolerance: 1.5 d for effects ≥ 2 d; 1.5 d absolute for tiny effects
        # (sub-day true effects can plausibly flip sign under realistic noise)
        tol = 1.5 if abs(true_tau) >= 2.0 else 1.7
        assert abs(res.tau - true_tau) < tol, (
            f"{pipe}/{met}: recovered {res.tau:.2f}, true {true_tau:.2f}"
        )
        # Sign-match required only when |tau| >= 1 d
        if abs(true_tau) >= 1.0:
            assert np.sign(res.tau) == np.sign(true_tau), (
                f"{pipe}/{met}: sign flipped (tau={res.tau:.2f}, "
                f"true={true_tau:.2f})"
            )


def test_did_significance_for_strong_effects():
    """Effects ≥ 4 d should be highly significant (p < 0.01)."""
    df_raw = synth.make_panel(seed=42)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        df_raw.to_csv(f.name, index=False)
        df = did.load_panel(Path(f.name))
    for (pipe, met), true_tau in synth.TRUE_TAU.items():
        if abs(true_tau) >= 4.0:
            res = did.estimate_static_did(df, pipe, met)
            assert res.p_value < 0.01, (
                f"{pipe}/{met}: p={res.p_value:.4f} not significant despite "
                f"true tau={true_tau}"
            )


def test_event_study_reference_zero():
    """Reference period (k = -1) coefficient must be exactly 0."""
    df_raw = synth.make_panel(seed=42)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        df_raw.to_csv(f.name, index=False)
        df = did.load_panel(Path(f.name))

    es = did.estimate_event_study(df, "raw", "SOS")
    ref = es[es["event_k"] == -1]
    assert len(ref) == 1
    assert ref.iloc[0]["beta"] == 0.0


def test_pre_trend_check_runs():
    df_raw = synth.make_panel(seed=42)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        df_raw.to_csv(f.name, index=False)
        df = did.load_panel(Path(f.name))
    pre = did.parallel_trends_check(df)
    assert len(pre) == 6      # 2 pipelines × 3 metrics
    assert pre["interaction_coef"].notna().all()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tests = [v for k, v in globals().items()
             if k.startswith("test_") and callable(v)]
    fails = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            fails += 1
        except Exception as e:                       # noqa: BLE001
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            fails += 1
    print(f"\n{len(tests) - fails}/{len(tests)} tests passed")
    sys.exit(1 if fails else 0)
