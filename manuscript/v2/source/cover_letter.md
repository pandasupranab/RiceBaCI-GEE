# Cover Letter

Supranab Panda
Center for Environment and Climate
Institute of Technical Education and Research
Siksha 'O' Anusandhan (Deemed to be) University
Bhubaneswar 751030, Odisha, India
pandasupranab@gmail.com
ORCID: 0009-0009-6496-6545

*Bhubaneswar, India*

The Editor-in-Chief
*Remote Sensing of Environment*
Elsevier

---

Dear Editor,

We submit for consideration in *Remote Sensing of Environment* a research article entitled:

**"Quantisation and seasonal-boundary artefacts in Sentinel-2 rice phenology: a reproducible quality-control framework for cyclone-impact studies"**

by Supranab Panda and Sarat Chandra Sahu (Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar, India).

**Why this paper is suitable for RSE.** *Remote Sensing of Environment* is the premier venue for methodological advances in quantitative remote sensing. This manuscript addresses a reproducible failure mode in Sentinel-2 time-series phenometric extraction — day-of-year (DOY) quantisation at fitting-window boundaries — that has direct consequences for any study using phenological metrics as outcome variables in causal impact research. The topic sits squarely within RSE's scope: it combines a satellite data quality analysis, a methodological contribution (the three-gate QC framework), and a regional application (Odisha Kharif rice, coastal cyclone impact).

**The core contribution.** Using a 48-observation district-year panel spanning 8 Odisha districts and 6 Kharif seasons (2019–2024), we demonstrate that the standard Sentinel-2 double-logistic pipeline concentrates 72.7% of end-of-season (EOS) phenometric values at a single boundary DOY (349) and 65.6% of peak-of-season (POS) values at a single DOY (288) — two distinct quantisation artefacts. After applying the three-gate QC framework we propose, all three mode-shares collapse to 8.3% and the SOS mode-share falls from 20.3% to 8.3%; the resulting panel passes all distributional plausibility checks. We then apply a difference-in-differences design — using three inland Odisha districts as controls — to test whether Cyclones Fani, Amphan, and Yaas (three consecutive May-window landfalls, 2019–2021) produced detectable shifts in Kharif rice phenology. All three phenometrics return null effects after QC, which we interpret as validation of the QC framework rather than evidence that cyclones never affect rice: the boundary artefacts generated false-positive treatment variance in the pre-QC panel, which the framework eliminates.

**Pre-registration and open data.** The study is pre-registered on the Open Science Framework (DOI 10.17605/OSF.IO/C4MP8). All code, panel data, and analysis scripts are publicly archived at GitHub (https://github.com/pandasupranab/RiceBaCI-GEE, tag v2.0-rse), Zenodo (DOI 10.5281/zenodo.20587316), and Mendeley Data (DOI 10.17632/z3zxk4xy3c.1). The analysis is fully reproducible from a single `run_all.sh` command.

**No competing interests.** We declare no competing financial interests. The manuscript has not been submitted elsewhere and is not under consideration at any other journal.

We suggest the following potential reviewers with expertise in satellite phenology, time-series methods, and causal inference in agronomic remote sensing:

(Reviewer suggestions will be provided through the submission portal.)

We look forward to the editorial assessment.

Yours sincerely,

**Supranab Panda** (corresponding author)
on behalf of all authors

---

*Supervisor co-author:*
Sarat Chandra Sahu, Director, Center for Environment and Climate, ITER, SOA University, Bhubaneswar
ORCID: 0000-0002-8048-1910
