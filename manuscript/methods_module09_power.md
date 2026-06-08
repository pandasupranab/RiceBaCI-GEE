# Methods §3.Y.4 — Post-hoc power and minimum detectable effect

The panel size is fixed by geography: G=8 districts (5 coastal-treated,
3 inland-control) is the universe of districts where rice phenology and
cyclone exposure can both be observed in our study window. We therefore
report **post-hoc** power and the minimum detectable effect (MDE)
transparently, alongside the inferential results, so reviewers can
assess what could and could not be learned from this design. Power is
**not** used to recompute p-values (those come from the wild-cluster
restricted bootstrap, §3.Y.3).

## 3.Y.4.1 Minimum detectable effect (analytical)

For each (pipeline × phenometric) cell we compute the two-sided MDE at
α = 0.05 and power = 0.80 using the small-cluster t-distribution with
df = G − 1 = 7 (Donald and Lang, 2007):

\[
\mathrm{MDE} \;=\; \bigl(t_{\alpha/2,\,G-1} + t_{1-\beta,\,G-1}\bigr)\cdot\widehat{SE}(\hat\tau)
\]

where \(\widehat{SE}(\hat\tau)\) is the cluster-robust standard error
recovered in §3.Y.3 (Module 05a). Results land in
`analysis/results/power_mde.csv` and Table S6.

For the six cells in our specification the MDE ranges from **1.04 d**
(raw / POS) to **2.49 d** (raw / SOS); five of six observed effects
exceed their MDE (`detectable = "yes"`). The single cell that does not —
**corrected / EOS, |τ̂| = 0.56 d vs MDE = 1.31 d** — is precisely the
cell our wild-cluster bootstrap fails to reject (p = 0.20, §3.Y.3).
Power and inference therefore tell the same story.

## 3.Y.4.2 Power curves (Monte-Carlo)

To map sensitivity to the cluster count itself, we simulate the data-
generating process

\[
y_{it} \;=\; \alpha_i + \delta_t + \tau\cdot D_{it} + \varepsilon_{it},
\]

with district FE \(\alpha_i\!\sim\!N(0,\sigma_u^2)\) (\(\sigma_u=13.06\) d),
year FE \(\delta_t\!\sim\!N(0,\sigma_t^2)\) (\(\sigma_t=41.75\) d), and
idiosyncratic noise
\(\varepsilon_{it}\!\sim\!N(0,\sigma_\varepsilon^2)\)
(\(\sigma_\varepsilon = 31.28\) d). Variance components are **empirical
point estimates** obtained from a two-way fixed-effects decomposition of
the real v2.1 corrected-SOS panel (`analysis/17_estimate_panel_variance_components.py`;
output `analysis/results/real_v21/variance_components_real_v21.csv`):
district means and year means are removed sequentially with `ddof=1` and
the residual variance gives \(\sigma_\varepsilon^2\). No synthetic or
literature-derived values enter the simulator.
Half the districts are treated, with the post-period covering the
second half of T = 8 years. We test \(H_0\!:\,\tau = 0\) using OLS with
CR1-corrected cluster-robust SE on G clusters and a t-test at df = G−1.

For each (G, τ) grid point we run R = 999 replications and report the
empirical rejection rate. Grid: τ ∈ {0, 5, 10, 15, 20, 30, 40, 60, 80, 100} d,
G ∈ {4, 6, 8, 12}.
Results in `analysis/results/power_curves.csv`; visualisation in
**Figure S1** (`figures/fig5_power_curves.pdf`).

Findings (real-σ simulator):
- **At G = 8 (this study)**: power 0.80 is **not** reached until
  τ ≈ 60 d — a far larger MDE than the previous synthetic-σ analysis
  had implied, because the empirical idiosyncratic SD (σ_ε ≈ 31 d) and
  year-FE SD (σ_t ≈ 42 d) are an order of magnitude larger than the
  earlier hand-set values. The type-I rate under \(H_0\) is 0.07
  (close to nominal 0.05, indicating CR1 with df = G−1 is well-sized).
- **At G = 4 (counterfactual minimum)**: 0.80 power not reached within
  the τ ≤ 100 d grid.
- **At G = 12 (counterfactual roster)**: 0.80 power reached at
  τ ≈ 40 d — a useful upper bound for any future replication that
  pools across state boundaries.

Implication for the present manuscript: the 15.1 d τ̂_corrected_SOS
point estimate is **well below** the G = 8 / R = 999 MDE of ~60 d, so
the non-rejection (p = 0.38, WCR p = 0.41) is **inferentially expected**
rather than evidence against an underlying effect. This is the central
rationale for our re-framing of v2.1 as a transparent null with
pre-registered exploratory mechanisms, rather than a confirmatory test
of Δ SOS.

## 3.Y.4.3 What this analysis does not claim

- It does **not** retroactively justify the p-values; it only describes
  what the design could have detected.
- It does **not** substitute for replication. The corrected/EOS cell is
  reported as null both by inference and by power analysis; future work
  with a longer time series or additional districts could revisit it.
- The variance components used here are **empirical point estimates**
  from the real v2.1 corrected-SOS panel (Module 17); sensitivity to
  ±50 % perturbations of σ_u, σ_t, σ_ε remains a future extension via
  `python3 09_power_analysis.py --sensitivity`.

---

**Reference**: Donald, S. G., & Lang, K. (2007). Inference with
difference-in-differences and other panel data. *Review of Economics
and Statistics*, 89(2), 221–233.
