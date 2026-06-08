"""
Bulbul transferability probe — real-data v2.1 residuals.

Inputs:
  bulbul_probe_deltas.csv          Per-district Δ_obs = SOS_2020 − mean(2017,2018)
  v2.1 corrected coefficient       τ_hat = +15.108 d, SE = 17.312 d (district-clustered)

Per-district residual r_d = Δ_obs_d − τ_hat
95% prediction interval = τ_hat ± 1.96 * sqrt(SE² + σ_idio²)

We use SE_idio = SD of pre-period SOS across the 6 probe-district baselines
as an empirical between-district idiosyncratic SD; this is a defensible
no-extra-data estimate of the variance the probe would face under H0.
"""
import numpy as np
import pandas as pd
from pathlib import Path

WORKDIR = Path(__file__).resolve().parent

# v2.1 corrected SOS coefficient (analysis/results/real_v21/did_static.csv)
TAU_HAT = 15.108
TAU_SE  = 17.312    # district-clustered SE
# These are the data quality flags
EXCLUDE_AOI_FOREST = {"Mayurbhanj", "Kandhamal"}  # forest-dominated AOIs
EXCLUDE_REASON = "AOI dominated by Eastern Ghats forest (April NDVI baseline > 0.40); not paddy-dominant at the 5 km centroid scale."

def main():
    df = pd.read_csv(WORKDIR / "bulbul_probe_deltas.csv")

    df["exclude_flag"] = df["district"].isin(EXCLUDE_AOI_FOREST)
    df["exclude_reason"] = df.apply(
        lambda r: EXCLUDE_REASON if r["exclude_flag"] else "", axis=1)

    # Per-district residual against v2.1 plug-in
    df["tau_hat_d"] = TAU_HAT
    df["residual_d"] = (df["delta_obs_d"] - TAU_HAT).round(2)

    # Empirical idiosyncratic SD from probe-baseline series
    pre_sd = float(np.nanstd(df.loc[~df["exclude_flag"], "sos_baseline"],
                              ddof=1))
    print(f"Empirical idiosyncratic SD (probe baselines, n={(~df['exclude_flag']).sum()}): {pre_sd:.2f} d")

    # 95% prediction interval half-width
    pi_half = 1.96 * np.sqrt(TAU_SE ** 2 + pre_sd ** 2)
    pi_low = TAU_HAT - pi_half
    pi_high = TAU_HAT + pi_half
    print(f"95% prediction interval: [{pi_low:.2f}, {pi_high:.2f}] d (half-width {pi_half:.2f})")

    df["in_95pi"] = ((df["delta_obs_d"] >= pi_low)
                     & (df["delta_obs_d"] <= pi_high))

    # Pre-registered pass criteria (residuals near zero AND >= 5/6 inside PI)
    paddy = df[~df["exclude_flag"]].copy()
    n_in = int(paddy["in_95pi"].sum())
    n_tot = len(paddy)
    mean_res = float(paddy["residual_d"].mean())

    print(f"\nPaddy-dominant districts (n={n_tot}):")
    cols_show = ["district", "exposure", "sos_baseline", "sos_2020",
                 "delta_obs_d", "tau_hat_d", "residual_d", "in_95pi"]
    print(paddy[cols_show].to_string(index=False))

    print(f"\nMean residual = {mean_res:+.2f} d  (range [{paddy['residual_d'].min():+.2f}, {paddy['residual_d'].max():+.2f}])")
    print(f"Districts inside 95% PI: {n_in}/{n_tot}")

    # Verdict
    if n_in >= int(np.ceil(0.83 * n_tot)) and abs(mean_res) < 1.96 * pre_sd:
        verdict = "PASS — residuals centred near zero and >=5/6 (proportionally) inside 95% PI"
    elif n_in < n_tot // 2:
        verdict = "INFORMATIVE-FAIL — majority of districts outside 95% PI; mechanism-specific transferability"
    else:
        verdict = "AMBIGUOUS — within small-G inferential floor of the design"
    print(f"\nVerdict: {verdict}")

    # Persist
    df.to_csv(WORKDIR / "bulbul_probe_residuals_real_v21.csv", index=False)
    summary = {
        "tau_hat_corrected_SOS_d": TAU_HAT,
        "tau_SE_d": TAU_SE,
        "empirical_idio_SD_d": round(pre_sd, 2),
        "pi95_low_d": round(pi_low, 2),
        "pi95_high_d": round(pi_high, 2),
        "n_paddy_districts": n_tot,
        "n_in_95pi": n_in,
        "mean_residual_d": round(mean_res, 2),
        "min_residual_d": round(float(paddy["residual_d"].min()), 2),
        "max_residual_d": round(float(paddy["residual_d"].max()), 2),
        "verdict": verdict,
        "districts_excluded": ", ".join(sorted(EXCLUDE_AOI_FOREST)),
        "exclusion_reason": EXCLUDE_REASON,
    }
    pd.DataFrame([summary]).to_csv(WORKDIR / "bulbul_probe_summary_real_v21.csv",
                                    index=False)
    print(f"\nWrote bulbul_probe_residuals_real_v21.csv and bulbul_probe_summary_real_v21.csv")
    return df, summary


if __name__ == "__main__":
    main()
