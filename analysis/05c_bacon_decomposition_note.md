# Module 05c — Goodman-Bacon decomposition: not applicable here

**Author:** Supranab Panda · **Date:** 2026-05-05

## Why the formal decomposition is skipped

Goodman-Bacon (2021, *J. Econometrics*) shows that a two-way fixed-
effects (TWFE) DiD estimator under **staggered adoption** is a weighted
average of all possible 2×2 DiD comparisons, including the
problematic "early-treated as control" comparison whose weights can be
negative and whose treatment-effect heterogeneity can flip the sign of
$\hat\tau$.

The RiceBaCI design is **not staggered.** All five coastal-treatment
districts are exposed simultaneously across 2019, 2020, and 2021;
the three inland-control districts are never treated.
Treatment timing is therefore degenerate:

| Cohort | Districts | Treatment years |
|---|---|---|
| Treated | Baleshwar, Bhadrak, Kendrapara, Jagatsinghpur, Puri | {2019, 2020, 2021} |
| Never-treated | Anugul, Cuttack, Dhenkanal | ∅ |

In a single-cohort design with a never-treated comparison group, the
Bacon decomposition collapses to a **single 2×2 comparison**
(treated × treatment-period vs. never-treated × treatment-period
+ pre-period). All weights on within-treated comparisons are zero
because every treated unit shares the same treatment timing; the
"forbidden" comparison (treated-vs-already-treated) does not exist.

Equivalently: the Callaway-Sant'Anna (2021) ATT(g,t) estimator with
$g$ = first-treatment year reduces to the standard DiD when
$|G| = 1$ and a never-treated group is available — which is our case.

## What replaces it

The binding robustness question — *"is $\hat\tau$ being driven by a
single district or a single year?"* — is addressed by the
leave-one-out (LOO) sensitivity in **Module 05d**
(`05d_jackknife_sensitivity.py`).  This:

1. Drops each of the 8 districts in turn and re-fits the DiD,
   reporting the percentage change in $\hat\tau$ (`jackknife_district.csv`).
2. Drops each of the 8 years in turn and re-fits, distinguishing
   treatment-year drops from control-year drops (`jackknife_year.csv`).
3. Classifies each cell as `stable` / `leverage` / `fragile` and
   writes a verdict summary (`jackknife_summary.txt`).

If reviewers explicitly ask for a Bacon decomposition, the response
is to state the single-cohort property above and cite
Goodman-Bacon §3.1 (the special case where decomposition reduces to
the canonical DiD).

## Bibliography

- Goodman-Bacon, A. (2021). Difference-in-differences with variation
  in treatment timing. *Journal of Econometrics*, 225(2), 254–277.
- Callaway, B. & Sant'Anna, P. H. C. (2021). Difference-in-differences
  with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.
- de Chaisemartin, C. & D'Haultfœuille, X. (2020). Two-way fixed
  effects estimators with heterogeneous treatment effects.
  *American Economic Review*, 110(9), 2964–2996.
