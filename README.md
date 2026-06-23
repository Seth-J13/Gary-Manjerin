# Gary-Manjerin

**SU26 AI Project 1** — A three-stage pipeline for electoral data processing, vote share prediction, and algorithmic redistricting.

---

## Overview

Gary-Manjerin takes raw geographic shapefile data, trains a Support Vector Regression model on historical voting records, and uses those predictions to generate "reasonable" congressional district maps via a greedy population-balancing algorithm.

The workflow is broken into three sequential steps, controlled through an interactive CLI (`main.py`).

---

## Pipeline

### Step 1 — Format Shapefile Data (`Data_Collection_and_Formatting`)

Ingests `.shp` files containing census block geometry and demographic data. Outputs formatted CSV files split into `training/` and `testing/` directories.

Input options:
- Auto-scan the system for all `.shp` files
- Use a GUI file-picker dialog
- Use a cached list from a previous scan (`shapefiles.csv`)

### Step 2 — Train Model & Predict (`Predictive_Model`)

Trains an SVR pipeline (scikit-learn) on the formatted training CSVs and predicts precinct-level Democratic/Republican vote shares for the test set.

- Default kernel: `LinearSVR` (loss: `squared_epsilon_insensitive`, C=1.5, ε=0.1)
- Alternate kernels: RBF, polynomial, etc. via `SVR` (C=10, γ=0.1)
- Features: longitude, latitude, population, total votes
- Output: Republican/Democratic share per block, written to `Predictive_Model/prediction/`
- Reports per-precinct error and final average accuracy

### Step 3 — Redistrict (`Reasonable_Gerrymandering`)

Reads prediction CSVs and builds district maps using a greedy frontier-expansion algorithm that balances population across districts toward an ideal target.

- User specifies number of districts
- Districts expand block-by-block, prioritizing whichever district is furthest below ideal population
- Stalled districts dump remaining unassigned blocks into the smallest district
- Outputs a CSV representing the final district assignments

---

## Requirements

- Python 3.x
- `numpy`
- `scikit-learn`
- `pyshp` (`shapefile`)
- `tkinter` (standard library, required for file-picker dialog)

Install dependencies:

```bash
pip install numpy scikit-learn pyshp
```

---

## Usage

```bash
python main.py
```

Follow the interactive prompts to move through the three steps. Steps must be run in order (1 → 2 → 3), but you can re-run individual steps without restarting from scratch.

---

## Project Structure

```
Gary-Manjerin/
├── main.py
├── shapefiles.csv                          # Auto-generated shapefile cache
├── Data_Collection_and_Formatting/
│   ├── format_file.py
│   ├── training/                           # Formatted training CSVs
│   └── testing/                            # Formatted testing CSVs
├── Predictive_Model/
│   ├── predict.py
│   └── prediction/                         # SVR output CSVs
└── Reasonable_Gerrymandering/
    └── gerrymander.py
```

---

## Notes

- The model currently predicts a two-party split only (Democrat + Republican = 1.0). Third-party modeling would require additional regressors.
- Democrat share is clamped to [0.0001, 0.9999] to avoid degenerate outputs.
- The gerrymandering algorithm includes debug logging that prints progress every 100 blocks assigned.
- This is a dev branch — expect rough edges and debug output in the console.
