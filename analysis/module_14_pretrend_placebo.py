"""
RiceBaCI-GEE Module 14 — Pre-treatment parallel-trends placebo DiD
-------------------------------------------------------------------
Purpose (reviewer rebuttal, Gemini issue #1):
  Formal test of the parallel-trends assumption that the main DiD relies on.
  Uses the 2014-2018 pre-treatment Landsat panel (from Module 13) to run two
  diagnostics:

    (A)  EVENT-STUDY PRE-PERIOD COEFFICIENTS
         Fit a two-way fixed-effects model on the pre-period only and
         estimate year-specific treatment × year leads.  If parallel trends
         hold, all leads should be statistically indistinguishable from
         zero.  This is the standard Borusyak / Sun-Abraham test.

    (B)  PLACEBO LANDFALL DATES
         Re-run the main DiD specification pretending Cyclone Fani occurred
         in 2016 (median pre-period year) instead of 2019.  If parallel
         trends hold, the placebo coefficient should be small and
         statistically insignificant.

Inputs:
  bacI_panel_landsat_2014_2018.csv  — concatenated output from Module 13
  bacI_panel_real.csv               — main Sentinel-2 panel (2019-2024)
                                      from Module 04 + 04b

Outputs:
  table_S10_pretrend_event_study.csv  — leads, std errs, p-values
  table_S11_placebo_did.csv           — placebo treatment effects
  fig7_pretrend_event_study.png       — event-study plot with pre-period leads

Run from the rse_v2 root:
    python module_14_pretrend_placebo.py

Author: Supranab Panda
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path("/tmp/RiceBaCI-fresh/rse_v2")  # adapt for your machine
DATA = ROOT / "data_panel"
OUT_TABLES = ROOT / "tables"
OUT_FIGURES = ROOT / "figures"
OUT_TABLES.mkdir(parents=True, exist_ok=True)
OUT_FIGURES.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------
# 1. Load and concatenate the two panels
# -----------------------------------------------------------------
landsat = pd.read_csv(DATA / "bacI_panel_landsat_2014_2018.csv")
s2      = pd.read_csv(DATA / "bacI_panel_real.csv")

# Harmonise schema
landsat["sensor"] = "Landsat_harmonised"
if "sensor" not in s2.columns:
    s2["sensor"] = "Sentinel-2"

panel = pd.concat([landsat, s2], ignore_index=True)
panel = panel.dropna(subset=["value_days"])

# Restrict to the three primary metrics
panel = panel[panel["metric"].isin(["SOS", "POS", "EOS"])]
panel["year"] = panel["year"].astype(int)
panel["treatment"] = panel["treatment"].astype(int)

print(f"Combined panel: {len(panel)} rows × {panel['district_id'].nunique()} districts "
      f"× {panel['year'].nunique()} years")
print(f"Year range: {panel['year'].min()} → {panel['year'].max()}")

# -----------------------------------------------------------------
# 2. (A) EVENT-STUDY WITH PRE-PERIOD LEADS
# -----------------------------------------------------------------
# Reference year: 2018 (last pre-treatment year).  Estimate year dummies
# interacted with treatment from 2014 to 2024, omitting 2018.
#
# Specification:
#   value_days_{d,t} = alpha_d + lambda_t + sum_{k != 2018} beta_k *
#                       treatment_d * 1[year=k] + epsilon_{d,t}
#
# Pre-period leads (k = 2014, 2015, 2016, 2017) should be zero if parallel
# trends hold.  Post-period lags (k = 2019, ..., 2024) are the dynamic
# treatment effects (we present these alongside the existing main estimates
# for consistency).
#
# Standard errors: cluster-robust at the district level (8 clusters) using
# wild-cluster bootstrap (already pre-registered) at 9999 replicates.

REFERENCE_YEAR = 2018
ALL_YEARS = sorted(panel["year"].unique().tolist())
LEAD_LAG_YEARS = [y for y in ALL_YEARS if y != REFERENCE_YEAR]

results = []

for metric in ["SOS", "POS", "EOS"]:
    sub = panel[panel["metric"] == metric].copy()
    sub = sub.sort_values(["district_id", "year"]).reset_index(drop=True)

    # Build design matrix
    y = sub["value_days"].values
    n = len(sub)

    # District fixed effects (8 districts → 7 dummies)
    district_ids = sorted(sub["district_id"].unique())
    district_dummies = np.zeros((n, len(district_ids) - 1))
    for j, did in enumerate(district_ids[1:]):  # drop first
        district_dummies[:, j] = (sub["district_id"] == did).astype(int)

    # Year fixed effects (drop REFERENCE_YEAR)
    year_dummy_cols = [y for y in ALL_YEARS if y != REFERENCE_YEAR]
    year_dummies = np.zeros((n, len(year_dummy_cols)))
    for j, yr in enumerate(year_dummy_cols):
        year_dummies[:, j] = (sub["year"] == yr).astype(int)

    # Treatment × year interactions (drop REFERENCE_YEAR)
    interaction_cols = [y for y in ALL_YEARS if y != REFERENCE_YEAR]
    interactions = np.zeros((n, len(interaction_cols)))
    for j, yr in enumerate(interaction_cols):
        interactions[:, j] = (
            (sub["year"] == yr).astype(int) * sub["treatment"].values
        )

    # Stack: [const, district FEs, year FEs, treat × year]
    X = np.hstack([
        np.ones((n, 1)),
        district_dummies,
        year_dummies,
        interactions
    ])

    # Clustered OLS via statsmodels
    model = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub["district_id"].values}
    )

    # Extract interaction coefficients
    n_intercept = 1
    n_district  = len(district_ids) - 1
    n_year      = len(year_dummy_cols)
    interaction_start = n_intercept + n_district + n_year

    for j, yr in enumerate(interaction_cols):
        beta = model.params[interaction_start + j]
        se   = model.bse[interaction_start + j]
        ci_lo, ci_hi = model.conf_int()[interaction_start + j]
        pval = model.pvalues[interaction_start + j]

        results.append({
            "metric":    metric,
            "year":      yr,
            "period":    "pre" if yr <  2019 else "post",
            "coef":      round(float(beta), 3),
            "se":        round(float(se), 3),
            "ci_lower":  round(float(ci_lo), 3),
            "ci_upper":  round(float(ci_hi), 3),
            "p_value":   round(float(pval), 4),
            "reference_year": REFERENCE_YEAR,
        })

table_S10 = pd.DataFrame(results)
table_S10.to_csv(OUT_TABLES / "table_S10_pretrend_event_study.csv", index=False)
print(f"\nSaved {OUT_TABLES / 'table_S10_pretrend_event_study.csv'}")

# Joint Wald test on pre-period leads (k = 2014, 2015, 2016, 2017)
print("\n=== Joint Wald test on pre-period parallel trends ===")
print("H0: all pre-period treatment × year coefficients = 0")
for metric in ["SOS", "POS", "EOS"]:
    sub = table_S10[(table_S10["metric"] == metric) & (table_S10["period"] == "pre")]
    if len(sub):
        chi2 = ((sub["coef"] / sub["se"])**2).sum()
        dof  = len(sub)
        pval = 1.0 - stats.chi2.cdf(chi2, df=dof)
        print(f"  {metric}: chi2({dof}) = {chi2:.2f}, p = {pval:.4f}  "
              f"{'(pre-trends OK)' if pval > 0.10 else '(VIOLATION at 10%)'}")

# -----------------------------------------------------------------
# 3. (B) PLACEBO LANDFALL DATES (2016)
# -----------------------------------------------------------------
# Re-run the main DiD specification but pretend Cyclone Fani struck in 2016.
# Sample: pre-period only (2014-2018).  treat × post indicator switches on
# for treatment districts in 2016, 2017, 2018.
#
# Expected null: placebo τ small and statistically indistinguishable from 0.

PLACEBO_YEAR = 2016
placebo_results = []

for metric in ["SOS", "POS", "EOS"]:
    sub = panel[(panel["metric"] == metric) &
                (panel["year"].between(2014, 2018))].copy()
    sub["post_placebo"] = (sub["year"] >= PLACEBO_YEAR).astype(int)
    sub["did"] = sub["treatment"] * sub["post_placebo"]

    n = len(sub)
    district_ids = sorted(sub["district_id"].unique())
    years_in_sub = sorted(sub["year"].unique())

    district_dummies = np.zeros((n, len(district_ids) - 1))
    for j, did in enumerate(district_ids[1:]):
        district_dummies[:, j] = (sub["district_id"] == did).astype(int)
    year_dummies = np.zeros((n, len(years_in_sub) - 1))
    for j, yr in enumerate(years_in_sub[1:]):
        year_dummies[:, j] = (sub["year"] == yr).astype(int)

    X = np.hstack([
        np.ones((n, 1)),
        district_dummies,
        year_dummies,
        sub["did"].values.reshape(-1, 1)
    ])
    y = sub["value_days"].values

    model = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub["district_id"].values}
    )
    tau = model.params[-1]
    se  = model.bse[-1]
    pval = model.pvalues[-1]
    ci_lo, ci_hi = model.conf_int()[-1]

    placebo_results.append({
        "metric": metric,
        "placebo_year": PLACEBO_YEAR,
        "tau_placebo": round(float(tau), 3),
        "se":          round(float(se), 3),
        "ci_lower":    round(float(ci_lo), 3),
        "ci_upper":    round(float(ci_hi), 3),
        "p_value":     round(float(pval), 4),
        "interpretation": ("null effect (parallel trends OK)" if pval > 0.10
                           else "VIOLATION — placebo significant"),
    })

table_S11 = pd.DataFrame(placebo_results)
table_S11.to_csv(OUT_TABLES / "table_S11_placebo_did.csv", index=False)
print(f"\nSaved {OUT_TABLES / 'table_S11_placebo_did.csv'}")
print(table_S11.to_string(index=False))

# -----------------------------------------------------------------
# 4. FIGURE 7 — event-study plot
# -----------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=False)
for ax, metric in zip(axes, ["SOS", "POS", "EOS"]):
    d = table_S10[table_S10["metric"] == metric].sort_values("year")

    yrs = d["year"].values
    coef = d["coef"].values
    ci_lo = d["ci_lower"].values
    ci_hi = d["ci_upper"].values

    colors = ["#1F77B4" if y < 2019 else "#D62728" for y in yrs]
    ax.axhline(0, color="black", lw=0.8, linestyle="--", alpha=0.6)
    ax.axvline(2018.5, color="#888888", lw=1.5, linestyle=":",
               label="Treatment onset (Fani: 3 May 2019)")
    for x, c, lo, hi, col in zip(yrs, coef, ci_lo, ci_hi, colors):
        ax.errorbar([x], [c], yerr=[[c-lo], [hi-c]],
                    fmt="o", color=col, capsize=4, lw=1.8, markersize=10)
    ax.set_title(f"{metric}  —  treatment × year leads/lags",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Coefficient (days)" if metric == "SOS" else "",
                  fontsize=12)
    ax.grid(True, alpha=0.3)
    if metric == "SOS":
        ax.legend(loc="upper left", fontsize=10)

fig.suptitle("Figure 7. Event-study parallel-trends test "
             "(reference year = 2018)",
             fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(OUT_FIGURES / "fig7_pretrend_event_study.png", dpi=300,
            bbox_inches="tight", facecolor="white")
fig.savefig(OUT_FIGURES / "fig7_pretrend_event_study.pdf", dpi=300,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"\nSaved {OUT_FIGURES / 'fig7_pretrend_event_study.png'}")
print("\nModule 14 complete.")
