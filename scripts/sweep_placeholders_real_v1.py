"""sweep_placeholders_real_v1.py

Sweep every [PLACEHOLDER: ...] in manuscript/manuscript_text.md with real-data values
from analysis/results/real_v1/. Adds an upfront v1 Provenance & Scope note so the
manuscript honestly reports what is empirically estimated in v1 vs what is queued
for v2 (classifier, 8-day GEE refit, MODIS/VDSA validation).

v1 reality:
  - 192 real DOY values (8 districts x 8 years x 3 metrics) from Sentinel-2 monthly
    composites (DOY snapped to month-15ths).
  - raw == corrected because Module 02 saline classifier hasn't run on real S1
    pixel labels yet (480 visual labels still to be drawn from S2 imagery).
  - EOS is degenerate for many cyclone-damaged pixels where NDVI never crosses 0.4.
  - DiD on real panel returns SOS tau = +15.29 d (SE 17.33, p=0.378, WCR p=0.371);
    POS tau = -3.59 d (p=0.213); EOS tau ~ 0 (degenerate).
  - Event-study Yaas k=+3: beta = +133.2 d, CI [+43.6, +222.8] — the one significant
    dynamic coefficient.
  - Jackknife: Bhadrak removal shifts SOS tau by 76.1% (leverage flag).
  - Placebo in-time (2018 pseudo-post): tau_pseudo SOS = -76.5 d.

Author: Supranab Panda (via Computer agent)
Date: 2026-06-02
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
SRC = ROOT / "manuscript" / "manuscript_text.md"
DST = ROOT / "manuscript" / "manuscript_text.md"
BAK = ROOT / "manuscript" / "manuscript_text.pre_b16.md"

text = SRC.read_text(encoding="utf-8")
BAK.write_text(text, encoding="utf-8")

# ------------------------------------------------------------------
# v1 Provenance note — inserted just below the Abstract block.
# ------------------------------------------------------------------
PROVENANCE_NOTE = """
> **v1 Provenance & Scope (release v1.0.0-rc1-real-data, 2026-06-02).** All
> empirical numbers reported in this manuscript are estimated from the real
> Sentinel-2 NDVI phenology panel (n = 192 district-year-metric observations,
> 8 coastal/inland Odisha districts × 8 Kharif seasons 2017–2024 × 3 phenometrics
> SOS/POS/EOS). Phenometric dates are extracted from monthly NDVI composites in
> Google Earth Engine using the double-logistic + half-max method (Module 04).
> Three honest v1 limitations are flagged here and recur as italicised
> *v1 limitation* notes in the relevant Results subsections:
>
> 1. **Monthly composite quantisation.** v1 NDVI inputs are monthly Sentinel-2
>    composites, so all extracted DOY values are snapped to month-15ths.
>    Sub-monthly precision and a Whittaker-smoothed 8-day refit (Module 04 v2)
>    are queued as the v2 priority.
> 2. **Raw == corrected in v1.** The Module 02 random-forest saline-flood
>    classifier is operational on synthetic labels but has not yet been retrained
>    on the 480 Sentinel-2 visual reference labels that will form the v2 ground
>    truth. Until then, the "corrected" pipeline in v1 emits the same DOY values
>    as the "raw" pipeline; classifier-dependent quantities are reported as
>    *v2 — pending classifier* rather than estimated from synthetic labels.
> 3. **EOS sparsity.** In cyclone-damaged years many coastal pixels never
>    achieve post-peak NDVI > 0.4, so EOS is undefined for those observations
>    (20 of 192 real DOY cells are legitimate NaN). EOS-cell estimates have only
>    nominal degrees of freedom and are reported with that caveat.
>
> The pre-registered design (OSF c4mp8) and the five-instrument robustness
> suite are unchanged. The v1 release demonstrates the full DiD + WCB +
> jackknife + placebo + event-study pipeline end-to-end on real data;
> classifier-dependent attenuation analyses migrate to v2 once the visual
> labels are drawn. All inputs, scripts, and outputs are public at the
> GitHub repository and Zenodo concept DOI listed in §6.

"""

# Anchor: insert right after the abstract word-count line
ABSTRACT_ANCHOR = "**Word count (abstract): 245**"
if ABSTRACT_ANCHOR in text and "v1 Provenance & Scope" not in text:
    text = text.replace(
        ABSTRACT_ANCHOR,
        ABSTRACT_ANCHOR + "\n" + PROVENANCE_NOTE,
        1,
    )

# ------------------------------------------------------------------
# Helper: replace a placeholder span in-place.
# ------------------------------------------------------------------
PENDING = "*[v2 — pending classifier; not estimated from synthetic labels]*"


def sweep(text: str, needle: str, replacement: str) -> str:
    if needle not in text:
        print(f"WARN: did not find: {needle[:90]!r}")
        return text
    return text.replace(needle, replacement, 1)


# ------------------------------------------------------------------
# 1. Abstract numerical claims
# ------------------------------------------------------------------

# Classifier OA/F1 — v2-pending
text = sweep(
    text,
    "[PLACEHOLDER: OA = X.XX, F1 = X.XX]",
    PENDING,
)

# Corrected vs uncorrected SOS difference, treatment seasons — v2-pending (because
# raw==corrected in v1 by construction). We state the v1 reality plainly.
text = sweep(
    text,
    "[PLACEHOLDER: XX days]",
    "0 days (raw == corrected in v1; *v1 limitation #2*)",
)

# Control-season difference — same caveat
text = sweep(
    text,
    "[PLACEHOLDER: X days]",
    "0 days (raw == corrected in v1)",
)

# Headline raw SOS DiD coefficient
text = sweep(
    text,
    "[PLACEHOLDER: X.X days (WCR-restricted *p* = X.XX)]",
    "+15.29 days (cluster-robust SE 17.33, WCR-restricted *p* = 0.371, "
    "WCR 95% CI [−54.0, +84.6])",
)

# Corrected SOS attenuation — in v1 identical to raw, flagged
text = sweep(
    text,
    "[PLACEHOLDER: X.X days (WCR *p* = X.XX)]",
    "+15.29 days (identical to raw in v1; attenuation analysis migrates to v2 "
    "once the saline classifier is retrained on the Sentinel-2 visual labels)",
)

# ------------------------------------------------------------------
# 2. §4.1 — Classifier accuracy block (all v2-pending)
# ------------------------------------------------------------------
for needle in [
    "[PLACEHOLDER: overall accuracy (OA) = X.XX (95% CI: X.XX–X.XX) and F1 = X.XX (95% CI: X.XX–X.XX)]",
    "[PLACEHOLDER: UA = X.XX]",
    "[PLACEHOLDER: PA = X.XX]",
    "[PLACEHOLDER: describe level of commission/omission balance]",
    "[PLACEHOLDER: X.XX]",
    "[PLACEHOLDER: meet / exceed]",
    "[PLACEHOLDER: confirming / refining the pre-registered H1 hypothesis]",
    "[PLACEHOLDER: X.XX ± X.XX (SD)]",
    "[PLACEHOLDER: ERA5 wind speed maximum and days-since-cyclone-landfall were the most discriminative features, followed by JRC water permanence and VH backscatter]",
    "[PLACEHOLDER]",
    "[PLACEHOLDER: X.XX]",  # second occurrence (McNemar) — handled by loop
    "[PLACEHOLDER: X.XX]",  # third occurrence — handled by loop
]:
    text = sweep(text, needle, PENDING)

# ------------------------------------------------------------------
# 3. §4.2 — Backscatter signature paragraph (v2-pending)
# ------------------------------------------------------------------
for needle in [
    "[PLACEHOLDER: X.X ± X.X weeks]",
    "[PLACEHOLDER: −XX.X ± X.X dB]",
    "[PLACEHOLDER: X.X dB, which is / is not statistically significant, *t*-test p = X.XX]",
]:
    text = sweep(text, needle, PENDING)

# ------------------------------------------------------------------
# 4. §4.3 — Raw vs corrected differences — in v1, all equal to zero by construction
# ------------------------------------------------------------------
text = sweep(
    text,
    "[PLACEHOLDER: XX.X ± X.X days (mean ± SD)]",
    "0.0 ± 0.0 days (raw == corrected in v1; *v1 limitation #2*)",
)
text = sweep(
    text,
    "[PLACEHOLDER: XX days (Puri) to XX days (Balasore)]",
    "all districts identical between raw and corrected pipelines in v1",
)
text = sweep(
    text,
    "[PLACEHOLDER: district name]",
    "Bhadrak (jackknife-flagged most-leveraging district, Δτ_SOS = 76.1 %)",
)
text = sweep(
    text,
    "[PLACEHOLDER: XX.X ± X.X days]",
    "0.0 ± 0.0 days (raw == corrected in v1)",
)
text = sweep(
    text,
    "[PLACEHOLDER: XX.X ± X.X days]",
    "0.0 ± 0.0 days (raw == corrected in v1)",
)
text = sweep(
    text,
    "[PLACEHOLDER: X.X ± X.X days]",
    "0.0 ± 0.0 days (raw == corrected in v1; pre-registered H2 < 2 d "
    "threshold trivially satisfied because no correction is applied)",
)
text = sweep(
    text,
    "[PLACEHOLDER: full table with numerical values]",
    "see Table S1, real_v1 column",
)

# ------------------------------------------------------------------
# 5. §4.4 — DiD headline (real numbers)
# ------------------------------------------------------------------
text = sweep(
    text,
    "[PLACEHOLDER: X.X d, CR1 SE = X.X, WCR-restricted *p* = X.XX, 95% bootstrap CI: X.X–X.X]",
    "+15.29 d, CR1 SE = 17.33, WCR-restricted *p* = 0.371, "
    "WCR 95 % CI [−54.02, +84.60], B = 999",
)
text = sweep(
    text,
    "[PLACEHOLDER: earlier/later by X.X d]",
    "delayed by 15.3 d (positive coefficient indicates later SOS in coastal "
    "districts during cyclone years relative to inland counterfactual; the "
    "wide CR1 confidence interval reflects G = 8 clusters and the small-sample "
    "uncertainty discussed in §4.4.3)",
)
text = sweep(
    text,
    "[PLACEHOLDER: X.X d (WCR *p* = X.XX)]",
    "−3.59 d (WCR *p* = 0.239, WCR 95 % CI [−15.11, +7.94])",
)
text = sweep(
    text,
    "[PLACEHOLDER: X.X d (WCR *p* = X.XX)]",
    "≈ 0 d (degenerate; *v1 limitation #3* — EOS undefined for 20/192 "
    "cyclone-damaged district-year-pixel cells)",
)
text = sweep(
    text,
    "[PLACEHOLDER: X.X d (WCR *p* = X.XX)]",
    "+15.29 d (WCR *p* = 0.371; identical to raw in v1)",
)
text = sweep(
    text,
    "[PLACEHOLDER: XX%]",
    "0 % (no attenuation in v1 because raw == corrected; "
    "attenuation analysis migrates to v2)",
)
text = sweep(
    text,
    "[PLACEHOLDER: X.X d (WCR *p* = X.XX)]",
    "−3.59 d (WCR *p* = 0.239; identical to raw in v1)",
)
text = sweep(
    text,
    "[PLACEHOLDER: was statistically null (X.X d, WCR *p* = X.XX), as anticipated by the saline-surge mechanism being specific to the early-season anchor / X.X d (WCR *p* = X.XX)]",
    "was statistically null (≈ 0 d, WCR *p* = 0.205; degenerate cell — see "
    "*v1 limitation #3*), consistent with the pre-registered prediction that "
    "the saline-surge correction is specific to the early-season anchor",
)

# ------------------------------------------------------------------
# 6. Event-study / pre-trends (real numbers)
# ------------------------------------------------------------------
text = sweep(
    text,
    "[PLACEHOLDER: was non-significant for all six cells, supporting parallel trends / was significant only for cell X, as discussed below]",
    "was non-significant for the SOS and POS cells (β = −63.6 d, *p* = 0.343 "
    "for SOS; β = −2.4 d, *p* = 0.903 for POS), supporting parallel trends; "
    "the EOS pre-trend test is undefined (residual df = 0, n_pre = 11, only "
    "two pre-cyclone years available — *v1 limitation #3*)",
)

# ------------------------------------------------------------------
# 7. Robustness suite paragraph (real numbers)
# ------------------------------------------------------------------
text = sweep(
    text,
    "[PLACEHOLDER: confirm rejection of \\(H_0: \\tau = 0\\) for raw/SOS, raw/POS, corrected/SOS, corrected/POS at \\(\\alpha = 0.05\\), with corrected/EOS not rejected]",
    "fail to reject \\(H_0: \\tau = 0\\) at \\(\\alpha = 0.05\\) for all six "
    "(pipeline × metric) cells (raw/SOS *p* = 0.371, raw/POS *p* = 0.239, "
    "raw/EOS *p* = 0.205, with corrected cells identical in v1); this null "
    "result reflects the small-G regime (G = 8 clusters) and the v1 quantisation "
    "constraints listed in the Provenance note, not a failure of the "
    "research design",
)
text = sweep(
    text,
    "[PLACEHOLDER: list cells]",
    "no cells classified as `stable` in v1 — all six (pipeline × metric) cells "
    "are flagged `leverage` or `fragile` (Bhadrak removal shifts SOS τ by "
    "76.1 %; Cuttack removal shifts POS τ by 55.8 %; EOS jackknife is "
    "degenerate)",
)
text = sweep(
    text,
    "[PLACEHOLDER: leverage / fragile, with [district name] as the most-leveraging observation]",
    "`fragile` (Angul flagged as the EOS-sign-flipping district; EOS LOO "
    "diagnostics are degenerate per *v1 limitation #3*)",
)
text = sweep(
    text,
    "[PLACEHOLDER: 5/6 cells, with permutation *p* hitting the design floor 1/57 ≈ 0.018 for raw/SOS, raw/POS, and corrected/POS]",
    "the EOS cells only (raw/EOS and corrected/EOS hit *p*_perm = 0.018, the "
    "design floor at G = 8); the SOS and POS cells return *p*_perm = 0.50 "
    "(SOS) and 0.286 (POS), consistent with the small-G null result",
)
text = sweep(
    text,
    "[PLACEHOLDER: 0.27]",
    "0.018",  # EOS permutation p hits design floor in real data
)
text = sweep(
    text,
    "[PLACEHOLDER: ±X.X]",
    "±76.5",  # in-time pseudo τ for SOS (2018 pseudo-post)
)

# ------------------------------------------------------------------
# 8. Bulbul transferability — v2-pending
# ------------------------------------------------------------------
for needle in [
    "[PLACEHOLDER: residual mean = X.X d, with X/6 districts inside the 95% prediction interval]",
    "[PLACEHOLDER: This / This does not]",
    "[PLACEHOLDER: the saline-surge correction generalises to / is mechanism-specific against]",
]:
    text = sweep(text, needle, PENDING)

# ------------------------------------------------------------------
# 9. §4.5 — MODIS / VDSA / yield validation — all v2-pending (validation data
# not in the v1 panel)
# ------------------------------------------------------------------
for needle in [
    "[PLACEHOLDER: X.X days for SOS, X.X days for POS, X.X days for EOS]",
    "[PLACEHOLDER: X.X, X.X, and X.X days]",
    "[PLACEHOLDER: satisfy / do not yet satisfy]",
    "[PLACEHOLDER: X.X, X.X, X.X days]",
    "[PLACEHOLDER: a / no]",
    "[PLACEHOLDER: X.XX]",
    "[PLACEHOLDER: N village-years]",
    "[PLACEHOLDER: X.X days]",
    "[PLACEHOLDER: X.X days]",
    "[PLACEHOLDER: X.X days]",
    "[PLACEHOLDER: −X.XX]",
    "[PLACEHOLDER: X.XX]",
    "[PLACEHOLDER: −X.XX]",
]:
    text = sweep(text, needle, PENDING)

# ------------------------------------------------------------------
# 10. Andhra Pradesh transferability — v2-pending
# ------------------------------------------------------------------
for needle in [
    "[PLACEHOLDER: OA = X.XX, F1 = X.XX]",
    "[PLACEHOLDER: XX.X ± X.X days in treatment pixels, X.X ± X.X days in control pixels]",
    "[PLACEHOLDER: \\(\\hat\\tau\\) = X.X days, WCR-restricted 95% CI: X.X–X.X]",
    "[PLACEHOLDER: confirming / partially confirming]",
]:
    text = sweep(text, needle, PENDING)

# ------------------------------------------------------------------
# 11. Pixel-uncertainty paragraph — v2-pending
# ------------------------------------------------------------------
for needle in [
    "[PLACEHOLDER: ±X.X days]",
    "[PLACEHOLDER: ±X.X days]",
    "[PLACEHOLDER: ±X.X days]",
]:
    text = sweep(text, needle, PENDING)

# ------------------------------------------------------------------
# 12. Discussion — magnitude language
# ------------------------------------------------------------------
text = sweep(
    text,
    "[PLACEHOLDER: quantitative finding, e.g. approximately 10–15 days]",
    "+15.3 days for SOS in v1 (CR1 SE 17.3; WCR 95 % CI [−54, +85])",
)
text = sweep(
    text,
    "[PLACEHOLDER: a XX-day bias in SOS dwarfs the typical interannual variability of X–X days documented in the MCD12Q2 long-term record and the ICRISAT VDSA Bhadrak panel]",
    "a 15-day SOS shift is on the order of, and in v1 not yet distinguishable "
    "from, the typical interannual variability of coastal Kharif rice "
    "phenology; the v2 corrected pipeline is required to separate the "
    "instrumental confound from the biological signal",
)
text = sweep(
    text,
    "[PLACEHOLDER: XX.X days to X.X days]",
    "the v1 raw pipeline (15.3 days) to the v2 corrected pipeline (target "
    "≤ 2 days, pending classifier retraining)",
)
text = sweep(
    text,
    "[PLACEHOLDER: approaches zero, confirming that the correction successfully separates the instrumental confound from the true biological response / remains non-trivially positive, indicating that a genuine agronomic delay of approximately X.X days persists after correction, attributable to soil salinity and waterlogging effects on transplanting]",
    "is not yet estimable in v1 because raw == corrected by construction; "
    "the attenuation test of the pre-registered prediction "
    "\\(\\tau_{\\text{raw}} > \\tau_{\\text{corrected}} > 0\\) is "
    "deferred to v2",
)

# ------------------------------------------------------------------
# 13. Limitations — classifier OA threshold
# ------------------------------------------------------------------
text = sweep(
    text,
    "[PLACEHOLDER: OA ≥ X.XX]",
    "the pre-registered OA ≥ 0.88 / F1 ≥ 0.85 thresholds (target; v2-pending)",
)

# ------------------------------------------------------------------
# Sanity check
# ------------------------------------------------------------------
remaining = re.findall(r"\[PLACEHOLDER:[^\]]+\]", text)
print(f"Remaining placeholder spans: {len(remaining)}")
for r in remaining[:5]:
    print("  ", r[:120])

DST.write_text(text, encoding="utf-8")
print(f"Wrote: {DST}")
print(f"Backup: {BAK}")
