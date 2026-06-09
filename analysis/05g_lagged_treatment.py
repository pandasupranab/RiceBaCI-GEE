"""
05g_lagged_treatment.py — Reviewer concern #23 (salinity carryover / temporal SUTVA).

Adds a 1-year-lagged treatment indicator to the canonical TWFE-DiD. Tests
whether the Fani 2019 treatment continues to affect Kharif 2020 phenology,
Amphan 2020 affects Kharif 2021, and Yaas 2021 affects Kharif 2022 — the
6-18 month salinity-recovery interval documented by Mondal et al. (2014).

Specification:
    Y_dt = a_d + g_t + tau_0 * (Treat_d * Post_t)
                     + tau_1 * (Treat_d * Post_t_lag1)
                     + e_dt

where Post_t_lag1 = 1 if year-1 was a treatment year for any coastal district.

Lagged-treatment years (years that *follow* a treatment year):
    2020 (lag of Fani 2019), 2021 (lag of Amphan 2020), 2022 (lag of Yaas 2021)

Note: 2020 and 2021 are BOTH original treatment years AND lagged-treatment
years simultaneously. We report two specifications:
    (i)  lag-only:  Post_t = 0 in 2020, 2021, 2022 (when restricted to lag1)
                    impossible to do without collapsing -- skip
    (ii) joint:     Both Post_t and Post_t_lag1 entered together
                    -- collinear at 2020, 2021, but identifies tau_1 off 2022
                    (carryover-only year following Yaas 2021)

Output:
    analysis/results/05g_lagged_treatment_did.csv
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf
from _did_core import load_panel, TREAT_YEARS, TREAT_EXPOSURE, PIPELINES, METRICS

HERE = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)


def estimate_lagged_did(df: pd.DataFrame, pipeline: str, metric: str) -> dict:
    sub = df.query("pipeline == @pipeline and metric == @metric").copy()
    # Build lagged-treatment indicator: any year that immediately follows a
    # treatment year (treatment years: 2019, 2020, 2021 -> lag years: 2020,
    # 2021, 2022).
    sub["post_lag1"] = sub["year"].isin([2020, 2021, 2022]).astype(int)
    sub["did_lag1"]  = sub["treat"] * sub["post_lag1"]

    sub["district"] = sub["district"].astype("category")
    sub["year_c"]   = sub["year"].astype("category")

    model = smf.ols(
        "median_doy ~ did + did_lag1 + C(district) + C(year_c)",
        data=sub,
    ).fit(cov_type="cluster", cov_kwds={"groups": sub["district"]})

    rec = {"pipeline": pipeline, "metric": metric, "n_obs": int(model.nobs)}
    for k in ["did", "did_lag1"]:
        rec[f"{k}_tau"]   = model.params.get(k, float("nan"))
        rec[f"{k}_se"]    = model.bse.get(k, float("nan"))
        rec[f"{k}_p"]     = model.pvalues.get(k, float("nan"))
        try:
            lo, hi = model.conf_int().loc[k].tolist()
            rec[f"{k}_ci_lo"] = lo
            rec[f"{k}_ci_hi"] = hi
        except KeyError:
            rec[f"{k}_ci_lo"] = float("nan")
            rec[f"{k}_ci_hi"] = float("nan")
    return rec


def main():
    df = load_panel(HERE / "baci_panel_real_v21.csv")
    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            rows.append(estimate_lagged_did(df, pipe, met))
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "05g_lagged_treatment_did.csv", index=False)
    print("=== 05g Lagged-treatment DiD (carryover, 1-year lag) ===")
    print(out.to_string(index=False))
    print(f"\nSaved -> {RESULTS / '05g_lagged_treatment_did.csv'}")


if __name__ == "__main__":
    main()
