#!/bin/bash
# RiceBaCI-GEE GitHub Repository Initialization Script
# ====================================================
# Run this script ONCE on your local machine to publish the project to GitHub.
#
# Prerequisites:
#   1. Git installed: https://git-scm.com/downloads
#   2. GitHub CLI installed: https://cli.github.com (or use HTTPS push instead)
#   3. You are logged in: `gh auth login` (or have a Personal Access Token)
#
# Usage:
#   cd /path/to/RiceBaCI-GEE
#   bash scripts/init_github_repo.sh

set -e

REPO_NAME="RiceBaCI-GEE"
GITHUB_USER="pandasupranab"
DESCRIPTION="Open-source framework to decouple cyclone-induced saline inundation from agronomic flooding in Sentinel-1/2 rice phenology retrieval. Bay of Bengal coastal Odisha, 2017-2024."

echo "================================================"
echo "RiceBaCI-GEE GitHub Repository Initialization"
echo "================================================"
echo ""

# Step 1: Initialize git
if [ -d ".git" ]; then
    echo "[skip] Git already initialized."
else
    echo "[1/6] Initializing git repository..."
    git init
    git branch -M main
fi

# Step 2: Create .gitignore
echo "[2/6] Writing .gitignore..."
cat > .gitignore <<'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# R
.Rhistory
.RData
.Ruserdata

# OS
.DS_Store
Thumbs.db
*.swp

# IDE
.vscode/
.idea/
*.iml

# Build artifacts
dist/
build/
*.egg-info/

# Outputs (regenerable)
outputs/raw/
outputs/intermediate/
*.tif
*.tiff
*.geotiff

# Large data files
data/raw/
data/processed/
*.csv.gz
*.parquet

# Sensitive
*.json
!package.json
!package-lock.json
credentials/
.gee_credentials

# OS
*.log
.cache/

# Pandoc temp
*.tmp
EOF

# Step 3: Create LICENSE (MIT)
echo "[3/6] Writing MIT LICENSE..."
cat > LICENSE <<EOF
MIT License

Copyright (c) $(date +%Y) Supranab Panda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Step 4: Stage and commit
echo "[4/6] Staging and committing files..."
git add -A
git -c user.name="Supranab Panda" -c user.email="pandasupranab@gmail.com" \
    commit -m "Initial commit: RiceBaCI-GEE submission package

- Manuscript draft for Remote Sensing of Environment
- GEE JavaScript modules (study area, classifier, phenology, BACI)
- R analysis scripts (mixed-effects model)
- Documentation (OSF pre-registration, data sources, setup guide)
- Cover letter, declarations, highlights, submission checklist

Pre-registration: https://osf.io/[OSF-id-pending]
Author: Supranab Panda (ORCID 0009-0009-6496-6545)
Supervisor: Dr. Sarat Chandra Sahu (ORCID 0000-0002-8048-1910)
Affiliation: Center for Environment and Climate, Institute of Technical
Education and Research, Siksha 'O' Anusandhan (Deemed to be) University,
Bhubaneswar 751030, Odisha, India

Open-data-only validation strategy. No external permissions required.
Licence: MIT (code), CC-BY 4.0 (dataset on Mendeley Data, pending DOI)."

# Step 5: Create remote (using gh CLI) and push
echo "[5/6] Creating GitHub remote..."
if command -v gh &> /dev/null; then
    gh repo create "$GITHUB_USER/$REPO_NAME" \
        --public \
        --description "$DESCRIPTION" \
        --source=. \
        --remote=origin \
        --push
    echo ""
    echo "Repository created and pushed: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo ""
    echo "GitHub CLI (gh) not found."
    echo "MANUAL STEP: Create the repo at https://github.com/new"
    echo "  Repository name: $REPO_NAME"
    echo "  Description: $DESCRIPTION"
    echo "  Public, no README/LICENSE/gitignore (we already have them)"
    echo ""
    echo "Then run:"
    echo "  git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "  git push -u origin main"
fi

# Step 6: Tag the initial release
echo "[6/6] Creating v0.1.0-prereg tag..."
git tag -a v0.1.0-prereg -m "Pre-registration baseline. Manuscript submitted to OSF, pipeline not yet executed."
if command -v gh &> /dev/null; then
    git push origin v0.1.0-prereg 2>/dev/null || echo "  (push tag manually with: git push origin v0.1.0-prereg)"
fi

echo ""
echo "================================================"
echo "DONE."
echo ""
echo "Next steps:"
echo "  1. Visit https://github.com/$GITHUB_USER/$REPO_NAME — verify repo is live"
echo "  2. Add topic tags: 'rice-phenology', 'sentinel-1', 'cyclone', 'remote-sensing', 'google-earth-engine'"
echo "  3. In repo Settings, enable: Issues, Wiki (optional), Discussions"
echo "  4. Connect Zenodo: https://zenodo.org/account/settings/github/ — toggle ON next to RiceBaCI-GEE"
echo "  5. Publish the v0.1.0-prereg release on GitHub UI (Releases -> Draft a new release -> select tag v0.1.0-prereg)"
echo "  6. Wait ~2 min, then copy the Zenodo concept DOI from the Zenodo page"
echo "  7. Update OSF pre-registration to point to this GitHub URL + Zenodo DOI"
echo "================================================"
