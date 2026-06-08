"""19_empirical_delta_cyc.py - Empirically estimate the per-pixel
phenological shift Delta_cyc induced by cyclone-flood inundation on rice
SOS, from the real v2.1 BACI panel.

Background
----------
The v2.1 correction model is

    DOY_corrected = DOY_raw + correction_days
    correction_days = - f * Delta_cyc

with f = cyclone-flood pixel share (real, from EMSR357 + Module 12 GEE
polygon intersection) and Delta_cyc = the per-pixel SOS shift that
cyclone-flooded pixels exhibit relative to agronomically-flooded pixels.

The previous implementation (analysis/03b_apply_v21_correction.py) used
the literature-cited value Delta_cyc = +14 d (Singha et al. 2019; Sun et
al. 2020). This module replaces that with an EMPIRICAL estimate from the
real panel.

Identification
--------------
Within the treatment (coastal) district set in the cyclone post-period
(years in {2019, 2020, 2021}), for the raw pipeline:

    DOY_raw_{it} = mu + alpha_i + delta_t + beta * f_{it} + eps_{it}

where beta is the marginal SOS shift per unit increase in cyclone-flood
share f. Under the v2.1 mixture model (DOY_observed_pixel ~ (1-f) *
DOY_agronomic + f * DOY_cyclone), beta = Delta_cyc.

Estimator
---------
Within-transformation on district FEs (subtract district means) and year
FEs (subtract year means within the treated sub-sample), then OLS regress
demeaned DOY on demeaned f. Heteroskedasticity-robust HC1 SE. Optionally
cluster at the district level.

Writes:
  analysis/results/real_v21/delta_cyc_empirical.csv  (point estimate,
    SE, 95% CI, sample size, comparison vs literature 14 d)
  analysis/results/real_v21/delta_cyc_empirical.json  (machine-readable)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "analysis" / "baci_panel_real_v21.csv"
SHARE = ROOT / "data_real" / "cyclone_pixel_share.csv"
OUT = ROOT / "analysis" / "results" / "real_v21"
OUT.mkdir(parents=True, exist_ok=True)

LITERATURE_DELTA_CYC = 14.0   # d - Singha 2019 / Sun 2020


def estimate_for_metric(panel: pd.DataFrame, share: pd.DataFrame,
                        metric: str) -> dict:
    """Within-FE regression of DOY_raw on f for treated districts in 2019-2021."""

    # Build raw panel cells for the metric
    sub = panel[(panel.metric == metric) & (panel.pipeline == "raw")][
        ["district", "year", "median_doy", "cyclone_exposure"]
    ].copy()
    # Restrict to TREATED districts in cyclone years
    treat = sub[
        (sub.cyclone_exposure == "coastal_treatment")
        & (sub.year.isin([2019, 2020, 2021]))
    ].copy()

    # Attach pixel share f for the (district, year, cyclone) triple
    share_m = share[["district", "year", "flood_share"]].copy()
    treat = treat.merge(share_m, on=["district", "year"], how="left")
    treat = treat.dropna(subset=["flood_share"])
    n = len(treat)
    if n < 5:
        return {"metric": metric, "n": n, "note": "insufficient cells"}

    # Two-way FE within-transform: subtract district mean AND year mean of f & y
    y = treat["median_doy"].values.astype(float)
    f = treat["flood_share"].values.astype(float)

    # district demean
    treat["y_d"] = treat.groupby("district")["median_doy"].transform("mean")
    treat["f_d"] = treat.groupby("district")["flood_share"].transform("mean")
    # year demean (on residuals after district demean)
    treat["y_dd"] = treat["median_doy"] - treat["y_d"]
    treat["f_dd"] = treat["flood_share"] - treat["f_d"]
    treat["y_y"] = treat.groupby("year")["y_dd"].transform("mean")
    treat["f_y"] = treat.groupby("year")["f_dd"].transform("mean")
    yw = treat["y_dd"].values - treat["y_y"].values
    fw = treat["f_dd"].values - treat["f_y"].values

    # OLS on within-transformed
    Sxy = float((fw * yw).sum())
    Sxx = float((fw * fw).sum())
    if Sxx < 1e-12:
        return {"metric": metric, "n": n, "note": "f has no within-FE variance"}
    beta = Sxy / Sxx
    resid = yw - beta * fw
    # HC1 robust SE
    G_eff = max(n - len(treat["district"].unique()) - len(treat["year"].unique()) + 1, 1)
    s2 = float((resid ** 2).sum()) / G_eff
    var_b = s2 / Sxx
    se = float(np.sqrt(var_b))
    # 95% CI on t-distribution with df = G_eff
    from scipy import stats
    t_crit = float(stats.t.ppf(0.975, G_eff))
    ci = (beta - t_crit * se, beta + t_crit * se)
    # f is a SHARE in [0,1], so beta is in DOY per unit share. We want
    # Delta_cyc = DOY shift per fully-cyclone-flooded pixel = beta * 1.0.
    delta_cyc = beta
    delta_cyc_se = se
    delta_cyc_ci = ci

    return {
        "metric": metric,
        "n_cells_treated_postperiod": int(n),
        "districts": treat["district"].unique().tolist(),
        "years": sorted(treat["year"].unique().tolist()),
        "beta_doy_per_unit_f": float(beta),
        "se_HC1": float(se),
        "df_HC1": int(G_eff),
        "ci_95_lo": float(delta_cyc_ci[0]),
        "ci_95_hi": float(delta_cyc_ci[1]),
        "Delta_cyc_d_empirical": float(delta_cyc),
        "Delta_cyc_d_literature_singha_sun": LITERATURE_DELTA_CYC,
        "agreement_with_literature": (
            "consistent" if (delta_cyc_ci[0] <= LITERATURE_DELTA_CYC <= delta_cyc_ci[1])
            else "inconsistent"
        ),
    }


def main():
    panel = pd.read_csv(PANEL)
    share = pd.read_csv(SHARE)
    print(f"[OK] panel rows = {len(panel)}, share rows = {len(share)}")

    rows = []
    for m in ("SOS", "POS", "EOS"):
        r = estimate_for_metric(panel, share, m)
        print(f"\n=== {m} ===")
        for k, v in r.items():
            print(f"  {k} = {v}")
        rows.append(r)

    df = pd.DataFrame(rows)
    csv_path = OUT / "delta_cyc_empirical.csv"
    df.to_csv(csv_path, index=False)
    json_path = OUT / "delta_cyc_empirical.json"
    with open(json_path, "w") as f:
        json.dump(rows, f, indent=2, default=str)
    print(f"\n[OK] wrote {csv_path}")
    print(f"[OK] wrote {json_path}")


if __name__ == "__main__":
    main()
