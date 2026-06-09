"""
05g_validate_lag.py — Validate the +49.3 d lag-coefficient finding.

Four diagnostics:
  (1) Identification check: print exactly which cells identify did_lag1.
      did_lag1 = treat * 1[year in {2020, 2021, 2022}].
      Inland controls: did_lag1=0 always. Coastal-treated districts: did_lag1=1 in {2020,2021,2022}.
      Treatment indicator: did = treat * 1[year in {2019,2020,2021}].
      Collinearity: did and did_lag1 both = 1 for treated districts in {2020, 2021}.
      The only year where did=0 and did_lag1=1 for treated is 2022.
      So did_lag1 is essentially identified off the 2022 coastal-vs-inland gap.

  (2) Drop-2022 sensitivity: rerun the lag specification with 2022 dropped.
      If did_lag1 collapses, it was only identified off 2022.

  (3) Leave-one-out (district) jackknife on lag spec.

  (4) Compare 2022 raw cell values to 2019, 2020, 2021 for treated vs inland.

Output:
  analysis/results/05g_validate_lag.txt
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from _did_core import load_panel

HERE = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)


def fit_lag(df, pipeline, metric):
    sub = df.query("pipeline == @pipeline and metric == @metric").copy()
    sub["post_lag1"] = sub["year"].isin([2020, 2021, 2022]).astype(int)
    sub["did_lag1"]  = sub["treat"] * sub["post_lag1"]
    sub["district"]  = sub["district"].astype("category")
    sub["year_c"]    = sub["year"].astype("category")
    model = smf.ols(
        "median_doy ~ did + did_lag1 + C(district) + C(year_c)",
        data=sub,
    ).fit(cov_type="cluster", cov_kwds={"groups": sub["district"]})
    rec = {"n_obs": int(model.nobs)}
    for k in ["did", "did_lag1"]:
        try:
            rec[f"{k}_tau"] = model.params[k]
            rec[f"{k}_se"]  = model.bse[k]
            rec[f"{k}_p"]   = model.pvalues[k]
            lo, hi = model.conf_int().loc[k].tolist()
            rec[f"{k}_ci_lo"] = lo
            rec[f"{k}_ci_hi"] = hi
        except KeyError:
            rec[f"{k}_tau"]   = np.nan
            rec[f"{k}_se"]    = np.nan
            rec[f"{k}_p"]     = np.nan
            rec[f"{k}_ci_lo"] = np.nan
            rec[f"{k}_ci_hi"] = np.nan
    return rec


def main():
    df0 = load_panel(HERE / "baci_panel_real_v21.csv")
    out_lines = []

    def log(s=""):
        print(s)
        out_lines.append(s)

    # ---- (1) IDENTIFICATION CHECK ----
    log("="*70)
    log("(1) IDENTIFICATION CHECK")
    log("="*70)
    df = df0[(df0["pipeline"]=="corrected") & (df0["metric"]=="SOS")].copy()
    df["post_lag1"] = df["year"].isin([2020,2021,2022]).astype(int)
    df["did_lag1"]  = df["treat"] * df["post_lag1"]
    log("Cells contributing to did_lag1=1 (coastal-treatment in {2020,2021,2022}):")
    contrib = df[df["did_lag1"]==1][["district","year","did","did_lag1","median_doy"]]
    log(contrib.to_string(index=False))
    log(f"\nOf which: did=1 AND did_lag1=1 (collinear -> not identifying lag):  {((df['did']==1)&(df['did_lag1']==1)).sum()} cells")
    log(f"           did=0 AND did_lag1=1 (PURE LAG identification cells):     {((df['did']==0)&(df['did_lag1']==1)).sum()} cells")
    log("\n=> did_lag1 is identified primarily off the 2022 coastal-treatment-vs-inland-control gap (5 cells).")

    # ---- (2) DROP-2022 SENSITIVITY ----
    log()
    log("="*70)
    log("(2) DROP-2022 SENSITIVITY (rerun lag spec with 2022 dropped)")
    log("="*70)
    df_no22 = df0[df0["year"] != 2022].copy()
    rec = fit_lag(df_no22, "corrected", "SOS")
    log(f"corrected SOS, 2022 dropped:")
    log(f"  did_tau     = {rec['did_tau']:+.3f}  (SE {rec['did_se']:.3f}, p={rec['did_p']:.4f}, CI=[{rec['did_ci_lo']:+.2f}, {rec['did_ci_hi']:+.2f}])")
    log(f"  did_lag1_tau= {rec['did_lag1_tau']:+.3f}  (SE {rec['did_lag1_se']:.3f}, p={rec['did_lag1_p']:.4f}, CI=[{rec['did_lag1_ci_lo']:+.2f}, {rec['did_lag1_ci_hi']:+.2f}])")
    log("\nFor comparison, full-panel lag spec (corrected SOS):")
    rec_full = fit_lag(df0, "corrected", "SOS")
    log(f"  did_tau     = {rec_full['did_tau']:+.3f}  (CI=[{rec_full['did_ci_lo']:+.2f}, {rec_full['did_ci_hi']:+.2f}])")
    log(f"  did_lag1_tau= {rec_full['did_lag1_tau']:+.3f}  (CI=[{rec_full['did_lag1_ci_lo']:+.2f}, {rec_full['did_lag1_ci_hi']:+.2f}])")

    # ---- (3) PRE-2022-ONLY SUB-PANEL LAG SPEC ----
    log()
    log("="*70)
    log("(3) PRE-2022-ONLY SUB-PANEL (S1B-clean era)")
    log("="*70)
    df_pre22 = df0[df0["year"] <= 2021].copy()
    rec = fit_lag(df_pre22, "corrected", "SOS")
    log(f"corrected SOS, 2017-2021 only (S1B-clean):")
    log(f"  did_tau     = {rec['did_tau']:+.3f}  (CI=[{rec['did_ci_lo']:+.2f}, {rec['did_ci_hi']:+.2f}])")
    log(f"  did_lag1_tau= {rec['did_lag1_tau']:+.3f}  (CI=[{rec['did_lag1_ci_lo']:+.2f}, {rec['did_lag1_ci_hi']:+.2f}])")
    log("=> On the clean pre-S1B-failure era, lag1 is identified off 2020 and 2021 lag-overlap-with-treatment (collinear)")

    # ---- (4) RAW VALUES IN 2022 ----
    log()
    log("="*70)
    log("(4) RAW SOS VALUES BY DISTRICT-YEAR (corrected pipeline)")
    log("="*70)
    pivot = df0[(df0["pipeline"]=="corrected") & (df0["metric"]=="SOS")].pivot(
        index="district", columns="year", values="median_doy"
    )
    log(pivot.round(1).to_string())
    log()
    log("Coastal mean by year:")
    coast = df0[(df0["pipeline"]=="corrected") & (df0["metric"]=="SOS") & (df0["treat"]==1)]
    log(coast.groupby("year")["median_doy"].mean().round(2).to_string())
    log("\nInland mean by year:")
    inld = df0[(df0["pipeline"]=="corrected") & (df0["metric"]=="SOS") & (df0["treat"]==0)]
    log(inld.groupby("year")["median_doy"].mean().round(2).to_string())
    log("\nCoastal-minus-inland mean by year:")
    diff = (coast.groupby("year")["median_doy"].mean()
            - inld.groupby("year")["median_doy"].mean())
    log(diff.round(2).to_string())

    # ---- (5) LOO DISTRICT JACKKNIFE ON LAG SPEC ----
    log()
    log("="*70)
    log("(5) LEAVE-ONE-OUT DISTRICT JACKKNIFE ON LAG SPECIFICATION")
    log("="*70)
    districts = sorted(df0["district"].unique())
    log(f"{'Dropped district':>18}  {'did_tau':>10}  {'did_lag1_tau':>14}  {'lag1_p':>8}")
    log("-"*60)
    for d in districts:
        sub = df0[df0["district"] != d].copy()
        try:
            r = fit_lag(sub, "corrected", "SOS")
            log(f"{d:>18}  {r['did_tau']:>+10.3f}  {r['did_lag1_tau']:>+14.3f}  {r['did_lag1_p']:>8.4f}")
        except Exception as e:
            log(f"{d:>18}  ERROR: {e}")

    # Write
    with open(RESULTS / "05g_validate_lag.txt", "w") as f:
        f.write("\n".join(out_lines))
    print(f"\nSaved -> {RESULTS / '05g_validate_lag.txt'}")


if __name__ == "__main__":
    main()
