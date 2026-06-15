"""
Made by Claude AI.
Predictive Model - Part II
Predicts Republican/Democratic vote share per block using a
neighborhood-aware SVM (approach #2 from the spec).

CSV columns (training): ID, Longitude, Latitude, Population, Total Votes,
                         Republican Vote Share, Democratic Vote Share
CSV columns (testing):  ID, Longitude, Latitude, Population
                        (no vote columns — those are what we predict)
"""

import numpy as np
from pathlib import Path as path

# These are all from the scikit-learn library (sklearn).
# Pipeline       : chains multiple steps (scaling + model) into one object
# StandardScaler : normalizes feature values so the SVM treats them equally
# train_test_split: randomly splits data into training and validation sets
# MultiOutputRegressor: lets SVR predict two values (rep% and dem%) at once
# SVR            : Support Vector Regressor — the core prediction model
# BallTree       : efficient spatial data structure for finding nearby blocks
# mean_absolute_error: measures how far off our predictions are on average
from sklearn.pipeline        import Pipeline
from sklearn.preprocessing   import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.multioutput     import MultiOutputRegressor
from sklearn.svm             import SVR
from sklearn.neighbors       import BallTree
from sklearn.metrics         import mean_absolute_error


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — FILE DISCOVERY
# Locates the training and testing folders on disk.
# If the expected folder structure isn't found automatically, the user is
# prompted to type in the folder paths manually.
# Debug here if: the program can't find your CSV files, or crashes on startup
#   with a FileNotFoundError or "No CSV files found" message.
# ════════════════════════════════════════════════════════════════════════════

def findFiles():
    """
    Tries to auto-detect the Data_Collection_and_Formatting folder that
    should live one level above this script's working directory.
    Falls back to asking the user to type paths if it can't find them.
    Returns (training_path, testing_path) as Path objects.
    """
    working_dir = path.cwd()

    # Walk one level up and look for the expected sibling folder
    candidate = working_dir.parent / "Data_Collection_and_Formatting"

    # Set paths only if the parent folder actually exists
    training_path = candidate / "training" if candidate.exists() else None
    testing_path  = candidate / "testing"  if candidate.exists() else None

    # If auto-detection failed for training, ask the user directly
    if training_path is None or not training_path.exists():
        print("Could not auto-detect training folder.")
        training_path = path(input("Enter the full path to the TRAINING folder: ").strip())

    # If auto-detection failed for testing, ask the user directly
    if testing_path is None or not testing_path.exists():
        print("Could not auto-detect testing folder.")
        testing_path = path(input("Enter the full path to the TESTING folder: ").strip())

    return training_path, testing_path


def pick_csv(folder: path, label: str) -> path:
    """
    Scans the given folder for all .csv files (including subfolders),
    prints a numbered list, and returns whichever one the user picks.
    'label' is just a display string like "training" or "testing".
    """
    # rglob("*.csv") finds CSVs in this folder AND any subfolders
    csvs = sorted(folder.rglob("*.csv"))

    # If no CSVs were found at all, raise an error immediately
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in {folder}")

    # Print the list so the user can pick by number
    print(f"\nAvailable {label} files:")
    for i, p in enumerate(csvs):
        print(f"  {i}: {p}")

    idx = int(input(f"Enter index for {label} file (0-{len(csvs)-1}): "))
    return csvs[idx]


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DATA LOADING
# Reads the CSV files into numpy arrays.
# The training CSV has 7 columns; the testing CSV has only 4 (no vote data).
# Debug here if: you see NaN values in your data, shape mismatches, or errors
#   about wrong numbers of columns. Also check here if your column order ever
#   changes — the indices (data[:, 0], etc.) will need updating.
# ════════════════════════════════════════════════════════════════════════════

def load_training_csv(filepath: path):
    """
    Reads a training CSV and splits it into four arrays:
      ids        — the block ID numbers                        shape (N,)
      coords_rad — [lat, lon] converted to radians            shape (N, 2)
      features   — [lon, lat, population] for each block      shape (N, 3)
      targets    — [rep_share, dem_share] to train against    shape (N, 2)

    Coordinates are converted to radians because the BallTree spatial lookup
    in Section 3 requires radian inputs when using haversine distance.
    """
    # genfromtxt parses the CSV into a 2D float array, skipping the header row
    data = np.genfromtxt(filepath, delimiter=",", skip_header=1)

    # Pull each column out by index — update these if your column order changes
    # Column:  0=ID  1=Lon  2=Lat  3=Pop  4=TotalVotes  5=RepShare  6=DemShare
    ids = data[:, 0]
    lon = data[:, 1]
    lat = data[:, 2]
    pop = data[:, 3]

    # Stack lon, lat, pop side-by-side into a single (N, 3) feature matrix
    features = np.column_stack([lon, lat, pop])

    # Columns 5 and 6 are the labels (what we want to learn to predict)
    targets = data[:, 5:7]

    # Convert degrees to radians for haversine distance calculations later
    coords_rad = np.deg2rad(np.column_stack([lat, lon]))

    return ids, coords_rad, features, targets


def load_testing_csv(filepath: path):
    """
    Same as load_training_csv but for test files, which only have 4 columns
    (no vote share columns — those are what we're trying to predict).
    Returns ids, coords_rad, and features (no targets).
    """
    data = np.genfromtxt(filepath, delimiter=",", skip_header=1)

    # Column:  0=ID  1=Lon  2=Lat  3=Pop
    ids = data[:, 0]
    lon = data[:, 1]
    lat = data[:, 2]
    pop = data[:, 3]

    features   = np.column_stack([lon, lat, pop])
    coords_rad = np.deg2rad(np.column_stack([lat, lon]))

    return ids, coords_rad, features


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — NEIGHBOURHOOD BUILDER
# For each block, finds its N nearest neighbours and combines their features
# into one flat input row. This is how the model gains spatial context —
# instead of predicting from a single block's data alone, it sees the
# surrounding area.
# Debug here if: predictions seem spatially random, or you get shape errors
#   when feeding data into the SVM. Also adjust N_NEIGHBORS here if you want
#   to experiment with how much neighbourhood context to include.
# ════════════════════════════════════════════════════════════════════════════

# How many nearby blocks to include in each sample's context.
# Increasing this gives the model more spatial info but makes it slower to fit.
N_NEIGHBORS = 8

# Number of features stored per block: [longitude, latitude, population]
FEAT_DIM = 3


def build_neighborhood_matrix(
        query_coords:    np.ndarray,   # Blocks we want to build context for  (M, 2) radians
        source_coords:   np.ndarray,   # Pool of blocks to search for neighbours  (N, 2) radians
        source_features: np.ndarray,   # Feature vectors of the source pool  (N, FEAT_DIM)
        n_neighbors:     int  = N_NEIGHBORS,
        exclude_self:    bool = False,
) -> np.ndarray:
    """
    For each query block, finds the n_neighbors closest blocks in the source
    pool (using real geographic distance) and flattens their features into
    one row. The output shape is (M, n_neighbors * FEAT_DIM).

    exclude_self=True is used during training to prevent a block from using
    its own data as a neighbour — that would be data leakage, letting the
    model "cheat" by seeing information it shouldn't have at prediction time.

    Any block with fewer than n_neighbors neighbours gets zero-padded to keep
    all rows the same length (required by the SVM).
    """
    # Build the spatial index from the source pool.
    # BallTree with haversine gives true great-circle distances on Earth's surface.
    tree = BallTree(source_coords, metric="haversine")

    # Query one extra neighbour so we have a spare to discard if the block
    # itself shows up in the results (distance == 0)
    k = n_neighbors + 1
    distances, indices = tree.query(query_coords, k=k)

    # Allocate the output matrix filled with zeros (handles padding automatically)
    M   = query_coords.shape[0]
    out = np.zeros((M, n_neighbors * FEAT_DIM), dtype=np.float32)

    for i in range(M):
        neighbours = []

        for dist, j in zip(distances[i], indices[i]):
            # If exclude_self is on and this result is the block itself
            # (distance is essentially zero), skip it
            if exclude_self and dist < 1e-10:
                continue

            neighbours.append(source_features[j])

            # Stop once we have enough neighbours
            if len(neighbours) == n_neighbors:
                break

        # Write each neighbour's features into the correct slice of the row
        for k_idx, feat in enumerate(neighbours):
            out[i, k_idx * FEAT_DIM : (k_idx + 1) * FEAT_DIM] = feat

    return out


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SVM MODEL DEFINITION
# Defines the prediction model as a two-step pipeline:
#   Step 1: StandardScaler  — re-centers and rescales every feature to have
#           mean 0 and std 1. SVMs are very sensitive to scale differences,
#           so this step is critical.
#   Step 2: MultiOutputRegressor(SVR) — fits one SVR per output column
#           (one for rep_share, one for dem_share) and packages them together.
# Debug here if: the model fits but predictions are wildly off. Try lowering C
#   (more regularisation) if it overfits, or raising it if it underfits.
#   Switching kernel to "linear" will make it faster but less flexible.
# ════════════════════════════════════════════════════════════════════════════

def build_svm_pipeline() -> Pipeline:
    """
    Creates and returns the untrained sklearn Pipeline.
    Hyperparameters to tune:
      C       : how hard the SVM tries to fit every point (higher = less regularised)
      epsilon : predictions within this margin of the true value incur no penalty
      kernel  : 'rbf' handles non-linear patterns; 'linear' is faster but simpler
      gamma   : 'scale' auto-sets this based on input variance (usually fine to leave)
    """
    # SVR is the core regression model
    svr = SVR(kernel="rbf", C=10.0, epsilon=0.05, gamma="scale")

    return Pipeline([
        # Scale all input features to the same range before the SVM sees them
        ("scaler", StandardScaler()),
        # n_jobs=-1 uses all available CPU cores to fit the two SVRs in parallel
        ("svm",    MultiOutputRegressor(svr, n_jobs=-1)),
    ])


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — TRAINING PIPELINE
# Orchestrates the full training process:
#   1. Load training CSV
#   2. Scale features
#   3. Build neighbourhood matrices (the actual SVM inputs)
#   4. Split into train / validation sets
#   5. Fit the SVM pipeline
#   6. Report validation MAE so you can judge model quality
# Debug here if: training crashes, MAE is unexpectedly high, or the split
#   sizes look wrong. The feat_scaler created here must be reused in predict()
#   — if you create a new one there the scaling will be inconsistent.
# ════════════════════════════════════════════════════════════════════════════

def train(training_csv: path):
    print("\n── Loading training data ──────────────────────────────────────")
    ids, coords_rad, raw_features, targets = load_training_csv(training_csv)
    print(f"   {len(ids)} blocks loaded.")

    # Fit a scaler on the raw features and transform them.
    # We do this BEFORE building neighbourhood matrices so that all neighbour
    # feature vectors are already on the same scale when they get concatenated.
    feat_scaler     = StandardScaler()
    scaled_features = feat_scaler.fit_transform(raw_features)

    print("── Building neighbourhood matrices ────────────────────────────")
    # Each row of X will be the flattened features of a block's 8 nearest neighbours.
    # exclude_self=True prevents the block from being its own neighbour during training.
    X = build_neighborhood_matrix(
        query_coords    = coords_rad,
        source_coords   = coords_rad,
        source_features = scaled_features,
        n_neighbors     = N_NEIGHBORS,
        exclude_self    = True,
    )

    # y holds the two target values we want to predict for each block
    y = targets.astype(np.float32)   # shape (N, 2): col 0 = rep%, col 1 = dem%

    # Split 85% of data for training the SVM, 15% for validation.
    # random_state=42 makes the split reproducible — same split every run.
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    print(f"   Train samples: {X_train.shape[0]}   Val samples: {X_val.shape[0]}")

    print("── Fitting SVM (this may take a moment on large datasets) ──────")
    model = build_svm_pipeline()
    model.fit(X_train, y_train)   # this is where the actual learning happens

    # Run predictions on the validation set (data the SVM never trained on)
    # to get an honest estimate of real-world accuracy
    y_pred_val = model.predict(X_val)
    mae = mean_absolute_error(y_val, y_pred_val)
    print(f"   Validation MAE: {mae:.4f}")
    # MAE is in the same units as the vote shares (0.0–1.0).
    # e.g. MAE of 0.05 means predictions are off by about 5 percentage points on average.

    # Return everything predict() will need later
    return model, feat_scaler, coords_rad, scaled_features


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6 — PREDICTION PIPELINE
# Uses the trained model to predict vote shares for the test blocks.
# Test blocks look up their neighbours from the TRAINING set — they don't
# have vote data of their own to learn from, but they can still borrow
# spatial context from the blocks around them.
# Debug here if: predictions are all the same value, all NaN, or outside
#   [0, 1]. Also check here if the output CSV is missing rows or columns.
# ════════════════════════════════════════════════════════════════════════════

def predict(
        model,
        feat_scaler,
        train_coords_rad:   np.ndarray,
        train_scaled_feats: np.ndarray,
        testing_csv:        path,
):
    print("\n── Loading test data ──────────────────────────────────────────")
    ids, test_coords_rad, test_raw_features = load_testing_csv(testing_csv)
    print(f"   {len(ids)} test blocks loaded.")

    # Transform test features using the scaler fitted on TRAINING data.
    # We must NOT call fit_transform here — that would compute new statistics
    # from the test set and make the scaling inconsistent with training.
    test_scaled = feat_scaler.transform(test_raw_features)

    print("── Building test neighbourhood matrices ───────────────────────")
    # For each test block, find its nearest neighbours in the TRAINING set.
    # exclude_self=False because test blocks are not present in the training
    # pool, so there's no risk of a block finding itself.
    X_test = build_neighborhood_matrix(
        query_coords    = test_coords_rad,
        source_coords   = train_coords_rad,
        source_features = train_scaled_feats,
        n_neighbors     = N_NEIGHBORS,
        exclude_self    = False,
    )

    print("── Running predictions ─────────────────────────────────────────")
    preds = model.predict(X_test)   # output shape: (M, 2)

    # SVR has no built-in output constraint, so raw predictions can sometimes
    # drift slightly outside [0, 1]. Clip them back into a valid range.
    preds = np.clip(preds, 0.0, 1.0)

    # Normalise each row so rep_share + dem_share = 1.0 exactly.
    # This mirrors the real-world constraint that vote shares must sum to 100%.
    row_sums = preds.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)   # guard against all-zero rows
    preds    = preds / row_sums

    # Print the first 10 predictions as a quick sanity check
    print("\nSample predictions (ID | Rep% | Dem%):")
    print(f"{'ID':>12}  {'Rep Share':>10}  {'Dem Share':>10}")
    print("-" * 38)
    for i in range(min(10, len(ids))):
        print(f"{ids[i]:>12.0f}  {preds[i, 0]:>10.4f}  {preds[i, 1]:>10.4f}")

    return ids, preds


# ════════════════════════════════════════════════════════════════════════════
# SECTION 7 — MAIN
# Entry point — runs everything in order:
#   1. Find folders and let the user pick CSV files
#   2. Train the model on the training CSV
#   3. Predict vote shares for the testing CSV
#   4. Save results to predictions.csv in the current working directory
# Debug here if: the program exits immediately, the output file isn't created,
#   or you want to change the output file name/location.
# ════════════════════════════════════════════════════════════════════════════

def main():
    # Locate folders and pick specific CSV files to use
    training_path, testing_path = findFiles()
    training_csv = pick_csv(training_path, "training")
    testing_csv  = pick_csv(testing_path,  "testing")

    # Train the SVM and get back everything needed for prediction
    model, feat_scaler, train_coords, train_feats = train(training_csv)

    # Generate predictions for all test blocks
    ids, predictions = predict(
        model, feat_scaler, train_coords, train_feats, testing_csv
    )

    # Write results to a CSV file with three columns: ID, rep share, dem share
    out_file = path("predictions.csv")
    rows = np.column_stack([ids, predictions])
    np.savetxt(
        out_file, rows, delimiter=",",
        header="ID,RepublicanVoteShare,DemocraticVoteShare",
        comments="",                                 # suppresses the default '#' prefix
        fmt=["%d", "%.6f", "%.6f"],                  # ID as integer, shares as decimals
    )
    print(f"\n✓ Predictions saved to {out_file.resolve()}")


if __name__ == "__main__":
    main()
