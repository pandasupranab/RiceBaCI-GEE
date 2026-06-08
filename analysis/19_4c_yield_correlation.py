"""
Batch 19.4c: District-level yield anomaly correlation.

Strategy: Without a fresh fetch of DES-Agri / IndiaStat yields, we use the
cyclone_year_event flag in the v2.1 panel as a proxy for known yield-loss
years (Phailin 2013, Hudhud 2014, Titli 2018, Fani 2019, Bulbul 2019, Yaas 2021).

For each district we compute the correlation between SOS anomaly
(district-year SOS minus district mean across all years) and a binary yield-
loss indicator (cyclone_year_event != ''). A robust negative correlation in
both raw (v1) and corrected (v2.1) panels — with consistent sign and similar
magnitude — confirms the correction does not flip the agronomic signal.

Reference benchmarks (literature):
  - Phailin (2013) Odisha rice yield loss ~12%  (IFPRI 2014; ICRISAT 2014)
  - Fani  (2019) coastal yield loss 8-15%        (FAO GIEWS; DES-Agri Odisha 2020)
  - Bulbul (2019) localized ~5-8%                (ICRISAT Odisha BC AR 2019-20)
  - Yaas  (2021) Bhadrak/Baleshwar 10-18%        (DES-Agri; OUAT post-cyclone survey)

Output: analysis/results/v21/table_S12_yield_anomaly_corr.csv
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr, spearmanr

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
PANEL = ROOT / "analysis" / "baci_panel_real_v21.csv"
OUT = ROOT / "analysis" / "results" / "v21"

df = pd.read_csv(PANEL)
sos = df[df["metric"] == "SOS"].copy()
sos["yield_loss_event"] = sos["cyclone_year_event"].fillna("").astype(str).str.strip().ne("").astype(int)

def per_pipeline(pipe_label):
    sub = sos[sos["pipeline"] == pipe_label].copy()
    # district anomaly
    sub["sos_anomaly_d"] = sub.groupby("district")["median_doy"].transform(lambda x: x - x.mean())
    r_p, p_p = pearsonr(sub["sos_anomaly_d"], sub["yield_loss_event"])
    r_s, p_s = spearmanr(sub["sos_anomaly_d"], sub["yield_loss_event"])
    # split by exposure
    coastal = sub[sub["cyclone_exposure"] == "coastal_treatment"]
    if len(coastal) > 5:
        r_c, p_c = pearsonr(coastal["sos_anomaly_d"], coastal["yield_loss_event"])
    else:
        r_c, p_c = np.nan, np.nan
    return {
        "pipeline": pipe_label,
        "n_obs": len(sub),
        "pearson_r_all": float(r_p),
        "pearson_p_all": float(p_p),
        "spearman_r_all": float(r_s),
        "spearman_p_all": float(p_s),
        "pearson_r_coastal": float(r_c) if not np.isnan(r_c) else None,
        "pearson_p_coastal": float(p_c) if not np.isnan(p_c) else None,
    }

rows = [per_pipeline("raw"), per_pipeline("corrected")]
# Delta row
dr = {
    "pipeline": "Δ (v21 − v1)",
    "n_obs": rows[1]["n_obs"] - rows[0]["n_obs"],
    "pearson_r_all": rows[1]["pearson_r_all"] - rows[0]["pearson_r_all"],
    "pearson_p_all": rows[1]["pearson_p_all"] - rows[0]["pearson_p_all"],
    "spearman_r_all": rows[1]["spearman_r_all"] - rows[0]["spearman_r_all"],
    "spearman_p_all": rows[1]["spearman_p_all"] - rows[0]["spearman_p_all"],
    "pearson_r_coastal": (rows[1]["pearson_r_coastal"] or 0) - (rows[0]["pearson_r_coastal"] or 0),
    "pearson_p_coastal": (rows[1]["pearson_p_coastal"] or 0) - (rows[0]["pearson_p_coastal"] or 0),
}
rows.append(dr)

table = pd.DataFrame(rows)
out_path = OUT / "table_S12_yield_anomaly_corr.csv"
table.to_csv(out_path, index=False)
print(f"Wrote {out_path}")
print(table.to_string(index=False))
