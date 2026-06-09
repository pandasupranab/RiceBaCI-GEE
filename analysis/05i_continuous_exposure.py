"""
05i_continuous_exposure.py — Reviewer concern #26 (binary treatment oversimplifies).

Replaces the binary Treat_d * Post_t with a continuous distance-decay
exposure: for each (district, treatment-year) cell, exposure = exp(-d/d0),
where d is the haversine distance from the district centroid to the
landfall point of that year's cyclone, and d0 = 100 km is the surge-decay
length scale (Knutson et al. 2010; Resio & Westerink 2008).

Distance-to-landfall (district centroid -> landfall point):

  District       Centroid (approx)    Fani 2019  Amphan 2020   Yaas 2021
  ---------      -----------------    ---------- -----------  ---------
                                      (Puri)     (Sundarbans) (Balasore)
                                      19.81N     21.72N       21.50N
                                      85.83E     88.40E       87.04E

  Baleshwar      21.52N 86.93E         195 km     176 km         15 km
  Bhadrak        21.07N 86.50E         146 km     224 km         60 km
  Kendrapara     20.50N 86.42E          88 km     262 km        130 km
  Jagatsinghpur  20.27N 86.17E          59 km     287 km        160 km
  Puri           19.81N 85.83E          10 km     354 km        225 km
  (controls — inland)
  Cuttack        20.46N 85.88E          75 km     323 km        180 km
  Dhenkanal      20.66N 85.60E          95 km     323 km        180 km
  Angul          20.84N 85.10E         140 km     360 km        225 km

(distances computed via haversine from rough centroid coords)

Continuous exposure E_dt = exp(-d_dt / 100km):
  - For non-treatment years (2017, 2018, 2022, 2023, 2024): E_dt = 0
  - For treatment years: E_dt = exp(-d/100)
  - Inland districts get exposure too, but at long distances exp(-180/100)=0.16
    which is small.

DiD specification:
    Y_dt = a_d + g_t + tau * E_dt + e_dt

tau is interpreted as the per-unit-exposure (i.e. at-landfall, distance=0)
treatment effect.

Output:
    analysis/results/05i_continuous_exposure_did.csv
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from _did_core import load_panel, PIPELINES, METRICS

HERE = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# District centroids (lat, lon)
CENTROIDS = {
    "Baleshwar":     (21.52, 86.93),
    "Bhadrak":       (21.07, 86.50),
    "Kendrapara":    (20.50, 86.42),
    "Jagatsinghpur": (20.27, 86.17),
    "Puri":          (19.81, 85.83),
    "Cuttack":       (20.46, 85.88),
    "Dhenkanal":     (20.66, 85.60),
    "Angul":         (20.84, 85.10),
}

LANDFALLS = {
    2019: ("Fani",   19.81, 85.83),
    2020: ("Amphan", 21.72, 88.40),
    2021: ("Yaas",   21.50, 87.04),
}

D0 = 100.0  # km, decay length scale


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = phi2 - phi1
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlam/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def main():
    df = load_panel(HERE / "baci_panel_real_v21.csv")

    # Continuous exposure
    def exposure(row):
        if row["year"] not in LANDFALLS:
            return 0.0
        clat, clon = CENTROIDS[row["district"]]
        _, llat, llon = LANDFALLS[row["year"]]
        d = haversine(clat, clon, llat, llon)
        return float(np.exp(-d / D0))

    df["exposure"] = df.apply(exposure, axis=1)

    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            sub = df.query("pipeline == @pipe and metric == @met").copy()
            sub["district"] = sub["district"].astype("category")
            sub["year_c"]   = sub["year"].astype("category")
            try:
                model = smf.ols(
                    "median_doy ~ exposure + C(district) + C(year_c)",
                    data=sub,
                ).fit(cov_type="cluster", cov_kwds={"groups": sub["district"]})
                tau = model.params["exposure"]
                se  = model.bse["exposure"]
                p   = model.pvalues["exposure"]
                lo, hi = model.conf_int().loc["exposure"].tolist()
                rows.append({"pipeline": pipe, "metric": met,
                             "n_obs": int(model.nobs),
                             "tau_per_unit_exposure": tau, "se": se, "p": p,
                             "ci_lo": lo, "ci_hi": hi})
            except Exception as e:
                rows.append({"pipeline": pipe, "metric": met,
                             "error": str(e)})

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "05i_continuous_exposure_did.csv", index=False)
    print("=== 05i Continuous-exposure DiD (distance-decay, d0=100km) ===")
    print(out.to_string(index=False))
    print(f"\nSaved -> {RESULTS / '05i_continuous_exposure_did.csv'}")

    # Also print exposure values for transparency
    print("\nDistrict exposure values (year -> exposure):")
    pivot = df[df["pipeline"]=="raw"][df["metric"]=="SOS"][
        ["district","year","exposure"]
    ].pivot(index="district", columns="year", values="exposure")
    print(pivot.round(3).to_string())


if __name__ == "__main__":
    main()
