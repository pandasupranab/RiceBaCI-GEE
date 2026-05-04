################################################################################
# RiceBaCI-GEE — R Analysis Script
# BACI Mixed-Effects Model: Cyclone Impact on Rice Phenological Dates
# -----------------------------------------------------------------------
# Author:   Subranab Panda (PhD, Agricultural Meteorology)
# Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
#           Flooding in Sentinel-1/2 Rice Phenology Retrieval
# Target:   Remote Sensing of Environment (Elsevier)
#
# Implements the BACI analysis specified in OSF pre-registration §E1:
#   phenology_date ~ year_type * cyclone_exposure + (1 | district) + (1 | year)
# fitted with lme4::lmer; p-values via pbkrtest::PBmodcomp (parametric bootstrap).
# Cohen's d effect sizes, McNemar's test (raw vs. corrected classifier labels),
# and Figure 6 (ggplot2 grouped bar chart of BACI shifts).
#
# Inputs:
#   analysis/baci_district_phenology.csv   (exported by Module 04)
#
# Outputs:
#   analysis/models/lmer_<metric>_<pipeline>.rds   (model objects)
#   manuscript/baci_results_table.csv              (summary table)
#   assets/fig06_baci_shifts.pdf                   (Figure 6)
#
# Reproducibility seed: 2026 (OSF §B2)
################################################################################

# ---------------------------------------------------------------------------- #
# 0. SETUP
# ---------------------------------------------------------------------------- #

set.seed(2026)

# Required packages (install once with install.packages(...))
library(lme4)       # Linear mixed-effects models
library(pbkrtest)   # Parametric-bootstrap model comparison
library(ggplot2)    # Publication-quality figures
library(dplyr)      # Data wrangling
library(tidyr)      # Reshaping
library(effsize)    # Cohen's d
library(broom.mixed) # tidy() method for lmer objects
library(scales)     # Axis formatting in ggplot2

# Create output directories if they do not exist
dir.create(file.path("analysis", "models"), showWarnings = FALSE, recursive = TRUE)
dir.create("manuscript",                    showWarnings = FALSE)
dir.create("assets",                        showWarnings = FALSE)

# ---------------------------------------------------------------------------- #
# 1. LOAD AND RESHAPE DATA
# ---------------------------------------------------------------------------- #

# Expected path relative to project root; adjust if running from a subdirectory
csv_path <- file.path("analysis", "baci_district_phenology.csv")

if (!file.exists(csv_path)) {
  stop(paste(
    "Input file not found:", csv_path,
    "\nDownload baci_district_phenology.csv from Google Drive (Module 04 output)",
    "and place it in the analysis/ directory."
  ))
}

raw_data <- read.csv(csv_path, stringsAsFactors = FALSE)

# Validate required columns (OSF §D3 schema)
expected_cols <- c("district", "year", "year_type", "cyclone_exposure",
                   "pipeline", "metric", "median_doy", "p25_doy",
                   "p75_doy", "n_pixels")
missing_cols <- setdiff(expected_cols, names(raw_data))
if (length(missing_cols) > 0) {
  stop(paste("Missing columns in CSV:", paste(missing_cols, collapse = ", ")))
}

# Coerce types
baci_long <- raw_data %>%
  mutate(
    district         = as.factor(district),
    year             = as.integer(year),
    year_type        = factor(year_type,        levels = c("control", "treatment")),
    cyclone_exposure = factor(cyclone_exposure,  levels = c("inland",  "coastal")),
    pipeline         = factor(pipeline,          levels = c("raw",     "corrected")),
    metric           = factor(metric,            levels = c("SOS",     "POS", "EOS")),
    phenology_date   = as.numeric(median_doy)    # outcome variable (OSF §D3)
  ) %>%
  filter(!is.na(phenology_date))                 # exclude pixels flagged as >50% missing

message(sprintf("Loaded %d rows after NA removal.", nrow(baci_long)))
message(sprintf("Districts: %s",
  paste(levels(baci_long$district), collapse = ", ")))

# ---------------------------------------------------------------------------- #
# 2. MIXED-EFFECTS BACI MODEL
# ---------------------------------------------------------------------------- #
#
# Full model (OSF §E1):
#   phenology_date ~ year_type * cyclone_exposure + (1 | district) + (1 | year)
#
# Null model (dropping interaction) for PBmodcomp likelihood-ratio test:
#   phenology_date ~ year_type + cyclone_exposure + (1 | district) + (1 | year)
#
# Parametric bootstrap p-value for the interaction term is the BACI test (OSF §E3).

metrics   <- c("SOS", "POS", "EOS")
pipelines <- c("raw", "corrected")

# Storage for all summary rows
results_rows <- list()

for (met in metrics) {
  for (pipe in pipelines) {

    message(sprintf("\n==== %s | %s ====", met, pipe))

    dat <- baci_long %>%
      filter(metric == met, pipeline == pipe)

    if (nrow(dat) < 10) {
      warning(sprintf("Insufficient data for %s / %s — skipping.", met, pipe))
      next
    }

    # Full model
    fit_full <- lmer(
      phenology_date ~ year_type * cyclone_exposure +
        (1 | district) + (1 | year),
      data    = dat,
      REML    = TRUE,
      control = lmerControl(optimizer = "bobyqa",
                            optCtrl   = list(maxfun = 2e5))
    )

    # Null model (no interaction)
    fit_null <- lmer(
      phenology_date ~ year_type + cyclone_exposure +
        (1 | district) + (1 | year),
      data    = dat,
      REML    = FALSE,    # ML for LRT comparison
      control = lmerControl(optimizer = "bobyqa",
                            optCtrl   = list(maxfun = 2e5))
    )

    fit_full_ml <- update(fit_full, REML = FALSE)

    # Parametric bootstrap comparison (OSF §E1)
    # nsim = 999 in production; reduced here for interactive speed
    pb_test <- PBmodcomp(fit_full_ml, fit_null, nsim = 499, seed = 2026)
    pb_pval <- summary(pb_test)$test["PBtest", "p.value"]

    message(sprintf("PBmodcomp interaction p = %.4f", pb_pval))

    # Fixed-effect coefficient for interaction term
    coefs <- fixef(fit_full)
    interact_name <- "year_typetreatment:cyclone_exposurecoastal"
    baci_shift    <- if (interact_name %in% names(coefs)) coefs[interact_name] else NA_real_

    # Random-effect variance summary
    vc <- as.data.frame(VarCorr(fit_full))
    var_district <- vc[vc$grp == "district", "vcov"]
    var_year     <- vc[vc$grp == "year",     "vcov"]

    message(sprintf("BACI shift = %.2f days; district var = %.2f; year var = %.2f",
      baci_shift, var_district, var_year))

    # Cohen's d: treatment-year coastal vs. control-year coastal
    d_data <- dat %>%
      filter(cyclone_exposure == "coastal")
    treat_vals   <- d_data %>% filter(year_type == "treatment") %>% pull(phenology_date)
    control_vals <- d_data %>% filter(year_type == "control")   %>% pull(phenology_date)

    cohens_d_val <- if (length(treat_vals) >= 2 && length(control_vals) >= 2) {
      cohen.d(treat_vals, control_vals)$estimate
    } else {
      NA_real_
    }

    message(sprintf("Cohen's d = %.3f", cohens_d_val))

    # Tidy fixed effects for reporting
    tidy_fe <- broom.mixed::tidy(fit_full, effects = "fixed", conf.int = TRUE)

    # Save model object
    rds_path <- file.path("analysis", "models",
                          sprintf("lmer_%s_%s.rds", met, pipe))
    saveRDS(fit_full, rds_path)
    message(sprintf("Model saved: %s", rds_path))

    # Accumulate summary row
    results_rows[[length(results_rows) + 1]] <- data.frame(
      metric              = met,
      pipeline            = pipe,
      baci_shift_days     = round(baci_shift,    2),
      pb_pval             = round(pb_pval,        4),
      cohens_d            = round(cohens_d_val,   3),
      ci_lower            = round(
        tidy_fe[tidy_fe$term == interact_name, "conf.low"],  2),
      ci_upper            = round(
        tidy_fe[tidy_fe$term == interact_name, "conf.high"], 2),
      var_district        = round(var_district,   2),
      var_year            = round(var_year,        2),
      n_obs               = nrow(dat),
      stringsAsFactors    = FALSE
    )
  }
}

results_table <- do.call(rbind, results_rows)

# ---------------------------------------------------------------------------- #
# 3. McNEMAR'S TEST: RAW VS. CORRECTED CLASSIFICATION LABELS  (OSF §E1 item 4)
# ---------------------------------------------------------------------------- #
#
# McNemar's test compares the proportion of pixels classified identically by
# raw and corrected pipelines. A significant result indicates the flood-
# correction meaningfully changes classification outcomes.
#
# Implementation: for each metric, pivot to wide (raw vs. corrected) and build
# a 2×2 contingency table of agreement / disagreement using a median-split
# binary classification (above/below median DOY = late/early season).

mcnemar_rows <- list()

for (met in metrics) {
  dat_wide <- baci_long %>%
    filter(metric == met) %>%
    select(district, year, year_type, cyclone_exposure, pipeline, phenology_date) %>%
    pivot_wider(names_from  = pipeline,
                values_from = phenology_date,
                values_fn   = mean) %>%     # aggregate if duplicates
    filter(!is.na(raw), !is.na(corrected))

  if (nrow(dat_wide) < 4) next

  global_median <- median(c(dat_wide$raw, dat_wide$corrected), na.rm = TRUE)
  raw_late      <- as.integer(dat_wide$raw       >= global_median)
  corr_late     <- as.integer(dat_wide$corrected >= global_median)

  ct <- table(raw_late, corr_late)
  if (all(dim(ct) == c(2, 2))) {
    mc <- mcnemar.test(ct)
    mcnemar_rows[[met]] <- data.frame(
      metric    = met,
      mcnemar_x2 = round(mc$statistic, 3),
      mcnemar_p  = round(mc$p.value,   4),
      n_pairs    = nrow(dat_wide)
    )
    message(sprintf("McNemar %s: X2=%.3f, p=%.4f", met, mc$statistic, mc$p.value))
  }
}

mcnemar_table <- do.call(rbind, mcnemar_rows)

# ---------------------------------------------------------------------------- #
# 4. WRITE SUMMARY TABLE  (OSF §F — code availability)
# ---------------------------------------------------------------------------- #

out_csv <- file.path("manuscript", "baci_results_table.csv")
write.csv(results_table, out_csv, row.names = FALSE)
message(sprintf("Summary table written: %s", out_csv))

if (!is.null(mcnemar_table) && nrow(mcnemar_table) > 0) {
  write.csv(mcnemar_table,
            file.path("manuscript", "mcnemar_results.csv"),
            row.names = FALSE)
}

# ---------------------------------------------------------------------------- #
# 5. FIGURE 6 — BACI SHIFTS  (OSF §E1 / manuscript Figure 6)
# ---------------------------------------------------------------------------- #
#
# Grouped bar chart with 95% CI error bars.
# Faceted by phenological metric (SOS / POS / EOS).
# Fill colour = pipeline (raw = #D55E00, corrected = #0072B2) — colour-blind safe.
# Error bars = 95% CI from fixed-effects profile.

plot_data <- results_table %>%
  mutate(
    pipeline    = factor(pipeline, levels = c("raw", "corrected"),
                         labels  = c("Raw (uncorrected)", "Corrected")),
    metric      = factor(metric,   levels = c("SOS", "POS", "EOS"),
                         labels  = c("Start of Season (SOS)",
                                     "Peak of Season (POS)",
                                     "End of Season (EOS)")),
    ci_lower    = as.numeric(unlist(ci_lower)),
    ci_upper    = as.numeric(unlist(ci_upper)),
    sig_label   = ifelse(pb_pval < 0.05, "*", "")
  )

fig6 <- ggplot(plot_data,
               aes(x = pipeline, y = baci_shift_days,
                   fill = pipeline, ymin = ci_lower, ymax = ci_upper)) +
  geom_col(width = 0.6, colour = "black", linewidth = 0.3) +
  geom_errorbar(width = 0.25, linewidth = 0.6) +
  geom_text(aes(label = sig_label,
                y = ifelse(baci_shift_days >= 0,
                           ci_upper + 0.5, ci_lower - 0.5)),
            size = 5, vjust = 0.5) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = "grey40") +
  facet_wrap(~ metric, ncol = 3) +
  scale_fill_manual(
    values = c("Raw (uncorrected)" = "#D55E00",
               "Corrected"         = "#0072B2"),
    guide  = guide_legend(title = "Pipeline")
  ) +
  scale_y_continuous(
    name   = "BACI shift (days; treatment \u2212 control)",
    labels = label_number(accuracy = 1)
  ) +
  scale_x_discrete(name = NULL) +
  labs(
    title    = "Fig. 6 — Cyclone impact on Kharif rice phenology (BACI shifts)",
    subtitle = paste0("Coastal Odisha 2019\u20132021 vs. control years 2017/18/22\u201324\n",
                      "lme4::lmer; p-values via parametric bootstrap (PBmodcomp); ",
                      "* p < 0.05; error bars = 95% CI"),
    caption  = paste0("Seed = 2026 | n districts = 8 | n years = 8\n",
                      "Source: Sentinel-1/2, JRC, ERA5 via Google Earth Engine")
  ) +
  theme_bw(base_size = 11) +
  theme(
    strip.background  = element_rect(fill = "grey92"),
    strip.text        = element_text(face = "bold"),
    legend.position   = "bottom",
    legend.title      = element_text(face = "bold"),
    plot.title        = element_text(face = "bold", size = 12),
    plot.subtitle     = element_text(size = 9,  colour = "grey30"),
    plot.caption      = element_text(size = 8,  colour = "grey50"),
    panel.grid.minor  = element_blank(),
    axis.text.x       = element_blank(),
    axis.ticks.x      = element_blank()
  )

fig6_path <- file.path("assets", "fig06_baci_shifts.pdf")
ggsave(fig6_path, fig6, width = 9, height = 5, device = "pdf")
message(sprintf("Figure 6 saved: %s", fig6_path))

# Also save as PNG for manuscript submission system
ggsave(file.path("assets", "fig06_baci_shifts.png"),
       fig6, width = 9, height = 5, dpi = 300)

# ---------------------------------------------------------------------------- #
# 6. SESSION INFO  (reproducibility record)
# ---------------------------------------------------------------------------- #

session_path <- file.path("analysis", "session_info.txt")
sink(session_path)
cat("RiceBaCI-GEE BACI analysis — session info\n")
cat("Date:", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"), "\n")
cat("Seed: 2026\n\n")
print(sessionInfo())
sink()

message("\n===== baci_mixed_effects.R complete =====")
message(sprintf("Results table : %s", out_csv))
message(sprintf("Model objects : analysis/models/*.rds"))
message(sprintf("Figure 6      : %s", fig6_path))
