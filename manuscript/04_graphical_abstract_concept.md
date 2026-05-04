# Graphical Abstract — Design Brief

RSE specifies the graphical abstract must be **531 × 1328 pixels (h × w)** and readable at 5 × 13 cm physical size. Preferred file types: TIFF, EPS, PDF, or MS Office.

## Concept

A horizontal three-panel composition reading left-to-right, telling the story in one image:

### Panel 1 (left, ~33% width) — *The Problem*

- Background: muted satellite-style backdrop showing a stylised coastline with a cyclone symbol (spiral)
- Foreground: two paired SAR backscatter time-series curves
  - Top curve: "Cyclone-induced flood" — sharp drop in late May (Amphan landfall)
  - Bottom curve: "Agronomic transplanting" — drop in late July
- Caption: *"Two physically different flood events. One SAR signal."*

### Panel 2 (centre, ~33% width) — *The Solution*

- Schematic flow showing the eight input features (icons for VH, VV, NDWI, LSWI, JRC water, ERA5 wind, distance-to-storm)
- Funnel into a "Random Forest" box
- Output: pixel labelled either *cyclone-flood* (red) or *agronomic-flood* (green)
- Caption: *"An 8-feature classifier separates them."*

### Panel 3 (right, ~33% width) — *The Outcome*

- Two miniature maps of coastal Odisha, side by side
  - Left: SOS map with raw pipeline (showing biased early dates near coast)
  - Right: SOS map with corrected pipeline (showing accurate dates)
- Below the maps: a small bar chart showing MAE reduction (raw vs. corrected) — labelled *[PLACEHOLDER: X days]*
- Caption: *"Corrected SOS/POS/EOS dates for cyclone-impacted years."*

## Title strip

A thin horizontal title strip across the top:

> *Decoupling cyclone storm-surge from agronomic flooding in Sentinel-1/2 rice phenology — coastal Odisha, 2017–2024.*

## Colour palette

- Primary: deep teal `#01696F` (RSE-friendly, matches the strategy document)
- Secondary: warm orange `#E07B00` (cyclone events)
- Neutral: charcoal `#222222` text on near-white `#FAFAFA` background
- Avoid pure red/green pairing for accessibility (use red-orange + teal for labels)

## How to produce it

1. Use Inkscape (free, vector) or Adobe Illustrator
2. Set canvas to 1328 × 531 px
3. Build each panel as a group; align with a 16-px gutter between panels
4. Export as TIFF at 300 DPI
5. Final filename: `Graphical_Abstract.tiff`

## Compliance notes

- Per Elsevier policy, no generative-AI imagery is permitted in the graphical abstract
- All third-party material (e.g. cyclone basemap, map outline) must be rights-cleared — Natural Earth public-domain shapefiles satisfy this
- Avoid embedding the article title verbatim in the image; the title appears separately on ScienceDirect
