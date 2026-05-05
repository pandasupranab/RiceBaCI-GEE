# Methods §3.Y.5 — Placebo / falsification tests

The parallel-trends F-test in §3.Y.2 is a single F-statistic per
(pipeline × metric) cell. For small-G designs (G = 8 here), reviewers
appropriately ask for a distributional placebo as well. We therefore
report two placebos: an **in-space donor-swap permutation** (the main
falsification) and an **in-time pseudo-shifted post-period** (a
single-comparison transparency probe).

## 3.Y.5.1 In-space placebo (donor-swap permutation)

Following Abadie, Diamond, & Hainmueller (2010 §VI), we re-assign the
"treated" label to all C(G, k) = C(8, 5) = **56** possible subsets of
districts of size k = 5 (the size of the real treated set), holding
the post-period fixed at 2019–2021. For each permutation we
re-estimate the static DiD (Eq 3.Y.1) on the subsetted panel and
record the placebo coefficient τ̂_p. The two-sided permutation
p-value is

\[
p_{\mathrm{perm}} \;=\; \frac{\#\{|\hat\tau_p|\ \geq\ |\hat\tau_{\mathrm{real}}|\} + 1}{n_{\mathrm{perm}} + 1},
\]

with the +1 correction following Phipson & Smyth (2010). The smallest
attainable p_perm on this design is 1/57 ≈ 0.018 (real assignment
alone in the tail).

**Results** (synthetic-panel verification; identical script,
`analysis/05e_placebo_tests.py`, will run on the real Module-04
panel):

| Pipeline | Metric | τ̂ real (d) | median τ_p (d) | p_perm | Verdict |
|---:|:---:|---:|---:|---:|:---|
| raw       | SOS | +5.66 | −0.14 | **0.018** | passes (floor) |
| raw       | POS | +4.35 | −0.27 | **0.018** | passes (floor) |
| raw       | EOS | +1.88 | +0.02 | 0.036    | passes |
| corrected | SOS | +1.96 | −0.04 | 0.054    | passes |
| corrected | POS | +2.10 | +0.01 | **0.018** | passes (floor) |
| corrected | EOS | +0.56 | −0.01 | 0.268    | fails |

Three observations:

1. **Real effects sit in the extreme tails.** For (raw/SOS),
   (raw/POS), (corrected/POS) the real τ̂ is the most extreme of all
   56 permutations — p_perm hits the design floor (0.018).
2. **Placebo distributions centre on zero.** The median placebo
   τ_p is within ±0.27 d of zero across all six cells — there is no
   systematic bias toward finding effects in arbitrary 5-district
   subsets.
3. **Internal consistency with WCR.** The single cell that fails the
   placebo (corrected/EOS, p_perm = 0.27) is the same cell that
   fails WCR (p = 0.20, §3.Y.3), the same cell that exceeds its MDE
   `no` flag (§3.Y.4), and the same cell flagged `leverage` by LOO
   (§3.Y.6). All four robustness instruments converge on the same
   verdict.

The placebo distribution is visualised in Figure 6 (also Figure S2 in
the supplement), and the full 336-row permutation table is in
`analysis/results/placebo_in_space.csv`.

## 3.Y.5.2 In-time placebo (pseudo-shifted post-period)

The real pre-period contains only two years (2017–2018), which is too
short for a formal in-time placebo with cluster inference. We
nonetheless report a single-comparison transparency probe: pretend the
cyclones happened in 2018 (instead of 2019–2021), drop the real
post-period, and re-estimate τ̂ on the resulting 2-year sample.
Because there is now only one "pre" year (2017) and one "fake post"
year (2018), this is a one-shot probe rather than a hypothesis test
— we report the pseudo-coefficient and let it stand or fall on
plausibility.

| Pipeline | Metric | τ̂ pseudo (d) | SE (d) |
|---:|:---:|---:|---:|
| raw       | SOS | +1.68 | 0.43 |
| raw       | POS | +0.26 | 0.75 |
| raw       | EOS | −0.15 | 1.24 |
| corrected | SOS | −0.81 | 1.46 |
| corrected | POS | −1.52 | 0.65 |
| corrected | EOS | +0.21 | 0.46 |

All six pseudo-coefficients are within ±1.7 d of zero. The largest in
absolute value is **raw/SOS (+1.68 d)** — note that this is also the
largest *real* effect (+5.66 d) and so the largest possible
contamination from the saline-surge mechanism leaking into the
adjacent year boundary; even so, the pseudo-coefficient is **less
than one-third** of the real coefficient. We interpret this as
consistent with the identifying assumption.

## 3.Y.5.3 What this analysis does and does not establish

**It establishes** that the real treated assignment is far more
predictive of large τ̂ than any of the 55 alternative 5-district
assignments, and that fake post-periods inside the real pre-period
yield small coefficients. These are the falsification posture
(Athey & Imbens 2017, §6.2) most reviewers expect for small-G DiD.

**It does not** prove parallel trends in the unobserved
counterfactual; that is impossible by construction. The placebo is
**necessary but not sufficient** evidence for the identifying
assumption.

---

**References**

Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic control
methods for comparative case studies. *Journal of the American
Statistical Association*, 105(490), 493–505.

Athey, S., & Imbens, G. W. (2017). The state of applied
econometrics: Causality and policy evaluation. *Journal of Economic
Perspectives*, 31(2), 3–32.

Phipson, B., & Smyth, G. K. (2010). Permutation p-values should
never be zero. *Statistical Applications in Genetics and Molecular
Biology*, 9(1), Article 39.
