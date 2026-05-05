#!/usr/bin/env bash
# =============================================================================
# RiceBaCI — full reproducibility harness
# -----------------------------------------------------------------------------
# Walks the entire offline analysis chain on the synthetic panel:
#
#   01-04  GEE (run separately on https://code.earthengine.google.com)
#   --- below this line, runs locally ---
#   05_did_regression               static DiD + event study + parallel trends
#   05a_wild_cluster_bootstrap      WCR p-values + CI by inversion
#   05b_bulbul_transferability      out-of-sample plug-in residuals
#   05d_jackknife_sensitivity       leave-one-district / leave-one-year LOO
#   05e_placebo_tests               in-space donor-swap + in-time placebo
#   06_figures                      Fig 2 / 3 / 4 publication PNG + PDF
#   07_supplement_tables            Tables S1-S7 in DOCX
#   09_power_analysis               MDE table + power curves (Fig 5 / Fig S1)
#   10_identification_dag           Fig 1B Pearl-style identification DAG
#
# Usage:
#   bash run_all.sh                  # synthetic panel, full WCR (B=9999)
#   bash run_all.sh --quick          # synthetic panel, B=999, no CI inversion
#   bash run_all.sh --panel <csv>    # use real GEE-exported panel (Module 04)
#
# Exit codes:
#   0  all stages OK
#   1  Python import failure / missing dep
#   2  a stage exited with non-zero status
#   3  a required output file was not written
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PANEL="analysis/synthetic_baci_panel.csv"
QUICK=0
WCR_B=9999
WCR_B_CI=499
WCR_FLAGS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)
      QUICK=1
      WCR_B=999
      WCR_B_CI=199
      WCR_FLAGS="--no-ci"
      shift ;;
    --panel)
      PANEL="$2"
      shift 2 ;;
    -h|--help)
      sed -n '2,30p' "$0"; exit 0 ;;
    *)
      echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# ----- helpers ----------------------------------------------------------------
say() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()  { printf "  \033[1;32mOK\033[0m  %s\n" "$*"; }
die() { printf "\n\033[1;31mFAIL\033[0m %s\n" "$*" >&2; exit "${2:-2}"; }

require_file() {
  [[ -f "$1" ]] || die "missing expected output: $1" 3
  ok "wrote $1"
}

# ----- stage 0: env check -----------------------------------------------------
say "Stage 0: environment"
python3 -c "import numpy, pandas, scipy, matplotlib, statsmodels, docx" \
  || die "Python deps missing. Run: pip install -r requirements.txt" 1
ok "Python $(python3 -c 'import sys; print(sys.version.split()[0])') with all deps"
ok "panel: $PANEL"
[[ $QUICK -eq 1 ]] && ok "QUICK mode (B=$WCR_B, B_ci=$WCR_B_CI, no CI inversion)"

# ----- stage 1: synthetic panel (skip if user provided real one) --------------
if [[ "$PANEL" == "analysis/synthetic_baci_panel.csv" ]]; then
  say "Stage 1: synthetic panel (offline test fixture)"
  python3 analysis/synthetic_panel.py
  require_file "$PANEL"
fi

# ----- stage 2: static DiD + event study + parallel trends --------------------
say "Stage 2: Module 05 — static DiD + event study + pre-trends"
python3 analysis/05_did_regression.py --panel "$PANEL"
require_file analysis/results/did_static.csv
require_file analysis/results/event_study.csv
require_file analysis/results/parallel_trends.csv

# ----- stage 3: wild-cluster bootstrap ----------------------------------------
say "Stage 3: Module 05a — wild-cluster bootstrap (G=8 small-cluster inference)"
# shellcheck disable=SC2086
python3 analysis/05a_wild_cluster_bootstrap.py \
  --panel "$PANEL" --B $WCR_B --B-ci $WCR_B_CI $WCR_FLAGS
require_file analysis/results/wild_bootstrap.csv

# ----- stage 4: Bulbul transferability ----------------------------------------
say "Stage 4: Module 05b — Bulbul transferability probe"
python3 analysis/05b_bulbul_transferability.py
require_file analysis/results/bulbul_transferability.csv

# ----- stage 5: LOO sensitivity -----------------------------------------------
say "Stage 5: Module 05d — leave-one-out (district + year)"
python3 analysis/05d_jackknife_sensitivity.py --panel "$PANEL"
require_file analysis/results/jackknife_district.csv
require_file analysis/results/jackknife_year.csv
require_file analysis/results/jackknife_verdicts.csv

# ----- stage 5e: placebo tests ------------------------------------------------
say "Stage 5e: Module 05e — placebo / falsification (in-space + in-time)"
python3 analysis/05e_placebo_tests.py --panel "$PANEL"
require_file analysis/results/placebo_in_space.csv
require_file analysis/results/placebo_summary.csv
require_file analysis/results/placebo_in_time.csv
require_file figures/fig6_placebo_distribution.pdf
require_file manuscript/supplement/Table_S7_placebo.docx

# ----- stage 6: figures -------------------------------------------------------
say "Stage 6: Module 06 — publication figures"
python3 analysis/06_figures.py --panel "$PANEL"
require_file figures/fig2_did_coefplot.pdf
require_file figures/fig3_event_study.pdf
require_file figures/fig4_district_sos_panel.pdf

# ----- stage 7: supplement tables ---------------------------------------------
say "Stage 7: Module 07 — supplement tables S1-S5"
python3 analysis/07_supplement_tables.py
require_file manuscript/supplement/Table_S1_did_static.docx
require_file manuscript/supplement/Table_S2_pretrends.docx
require_file manuscript/supplement/Table_S3_bulbul_transferability.docx
require_file manuscript/supplement/Table_S4_wild_bootstrap.docx
require_file manuscript/supplement/Table_S5_jackknife.docx

# ----- stage 8: post-hoc power analysis ---------------------------------------
say "Stage 8: Module 09 — MDE + power curves (§3.Y.4 / Fig 5)"
POWER_REPS=999
[[ $QUICK -eq 1 ]] && POWER_REPS=199
python3 analysis/09_power_analysis.py --reps $POWER_REPS
require_file analysis/results/power_mde.csv
require_file analysis/results/power_curves.csv
require_file analysis/results/power_summary.json
require_file figures/fig5_power_curves.pdf

# ----- stage 9: identification DAG --------------------------------------------
say "Stage 9: Module 10 — identification DAG (Fig 1B)"
python3 analysis/10_identification_dag.py
require_file figures/fig1b_identification_dag.pdf
require_file figures/fig1b_identification_dag.png

say "Stage 11: Module 11 — pre-Kharif cyclone climatology (Note S2 / Table S8 / Fig S1)"
python3 analysis/11_cyclone_climatology.py --quick
require_file analysis/results/cyclone_climatology.csv
require_file manuscript/supplement/Table_S8_cyclone_climatology.docx
require_file figures/figS1_cyclone_climatology.pdf
require_file figures/figS1_cyclone_climatology.png

# ----- summary ----------------------------------------------------------------
say "Summary"
python3 - <<'PY'
import pandas as pd
from pathlib import Path
res = Path("analysis/results")

print("\nStatic DiD (Module 05):")
df = pd.read_csv(res/"did_static.csv")
print(df[["pipeline","metric","tau_days","se_days","p_value",
         "ci_lo_95","ci_hi_95"]].to_string(index=False))

print("\nWCR bootstrap (Module 05a):")
df = pd.read_csv(res/"wild_bootstrap.csv")
print(df[["pipeline","metric","tau_hat","p_wcb_2sided",
         "ci_lo_95_wcb","ci_hi_95_wcb"]].to_string(index=False))

print("\nLOO verdicts (Module 05d):")
df = pd.read_csv(res/"jackknife_verdicts.csv")
print(df.to_string(index=False))

print("\nBulbul transferability (Module 05b):")
df = pd.read_csv(res/"bulbul_transferability.csv")
n_in = (df["inside_95pct_PI"]=="yes").sum()
mean_r = df["residual_d"].mean()
print(f"  {n_in}/{len(df)} districts inside 95% PI; "
      f"mean residual = {mean_r:+.2f} d")

print("\nMDE (Module 09):")
df = pd.read_csv(res/"power_mde.csv")
print(df[["pipeline","metric","tau_hat_d","MDE_2sided_d",
         "tau_over_MDE","detectable"]].to_string(index=False))
import json
ps = json.loads((res/"power_summary.json").read_text())
print(f"\n  G={ps['G']}, MDE range {ps['MDE_80_2sided_range_d'][0]:.2f}"
      f"-{ps['MDE_80_2sided_range_d'][1]:.2f} d")
print(f"  power 0.80 reached at tau ≈ {ps['tau_for_power_0_80_at_G8_d']} d")
print(f"  detectable: {ps['n_detectable_cells']}/{ps['n_total_cells']} cells")

print("\nPlacebo (Module 05e):")
df = pd.read_csv(res/"placebo_summary.csv")
print(df[["pipeline","metric","tau_real_d","median_placebo_d",
         "p_permutation","verdict"]].to_string(index=False))
PY

printf "\n\033[1;32mALL STAGES OK\033[0m\n"
