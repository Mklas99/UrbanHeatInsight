import json
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# -------------------------------------------------------------------
# GeoJSON utilities
# -------------------------------------------------------------------

def load_geojson(path: str) -> dict:
    """Load a GeoJSON file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def geojson_to_dataframe(gj: dict) -> pd.DataFrame:
    """
    Convert GeoJSON features to a flat pandas DataFrame:
    - flattens 'properties'
    - extracts longitude/latitude from geometry
    - if geometry is not Point, it uses an approximate centroid
    """
    features = gj.get("features", [])
    if not features:
        raise ValueError("GeoJSON has no 'features'.")

    # Flatten 'properties'
    props_df = pd.json_normalize([feat.get("properties", {}) for feat in features])

    # Extract lon/lat
    def geom_to_lonlat(geom):
        if geom is None:
            return (np.nan, np.nan)
        gtype = geom.get("type")
        coords = geom.get("coordinates")

        # Simple Point
        if gtype == "Point" and isinstance(coords, (list, tuple)) and len(coords) >= 2:
            return coords[0], coords[1]

        # Fallback: compute a rough centroid for polygons/lines/etc.
        def flatten(coord_list):
            if isinstance(coord_list[0], (float, int)):
                return [coord_list]
            out = []
            for x in coord_list:
                out.extend(flatten(x))
            return out

        try:
            flat = flatten(coords)
            arr = np.array(flat)
            return float(np.nanmean(arr[:, 0])), float(np.nanmean(arr[:, 1]))
        except Exception:
            return (np.nan, np.nan)

    lon_lat = [geom_to_lonlat(feat.get("geometry")) for feat in features]
    lon = [xy[0] for xy in lon_lat]
    lat = [xy[1] for xy in lon_lat]

    df = props_df.copy()
    df["longitude"] = lon
    df["latitude"] = lat
    return df


# -------------------------------------------------------------------
# Preprocessing & model
# -------------------------------------------------------------------

def build_preprocessor(X: pd.DataFrame) -> Tuple[ColumnTransformer, List[str], List[str]]:
    """
    Build a ColumnTransformer that:
    - imputes and scales numeric features,
    - imputes and one-hot encodes categorical features.
    """
    numeric_features = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [c for c in X.columns if c not in numeric_features]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    return preprocessor, numeric_features, categorical_features


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def evaluate_split(name: str, y_true, y_pred) -> None:
    """Print RMSE and MAE for one split."""
    print(f"\n=== {name} ===")
    print(f"RMSE: {rmse(y_true, y_pred):.4f}")
    print(f"MAE : {mean_absolute_error(y_true, y_pred):.4f}")


# -------------------------------------------------------------------
# Main training logic
# -------------------------------------------------------------------

def run_baseline_regression(
    df: pd.DataFrame,
    target_column: str,
    feature_columns: Optional[List[str]] = None,
    model_type: str = "ridge",
    test_size: float = 0.2,
    val_size: float = 0.2,
    random_state: int = 42,
):
    """
    Run a baseline regression with a train/val/test split.

    Parameters
    ----------
    df : pd.DataFrame
        Input data with all columns (features + target).
    target_column : str
        Name of the column to predict.
    feature_columns : list of str, optional
        List of feature column names to use.
        If None, all columns except the target are used.
    model_type : str
        "ridge" (default) or "linear".
    test_size : float
        Fraction of data used for test set.
    val_size : float
        Fraction of data used for validation set (relative to full dataset).
    random_state : int
        Random seed for reproducibility.
    """

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in DataFrame columns.")

    # Drop rows with missing target (you could also handle this differently)
    df = df[df[target_column].notna()].copy()
    if df.empty:
        raise ValueError("No rows with non-missing target values.")

    # Select features
    if feature_columns is None:
        feature_columns = [c for c in df.columns if c != target_column]
        print("Using all columns as features except the target:")
        print(feature_columns)
    else:
        # Check that requested features exist
        missing = [c for c in feature_columns if c not in df.columns]
        if missing:
            raise ValueError(f"The following feature columns are missing in the DataFrame: {missing}")
        print("Using specified feature columns:")
        print(feature_columns)

    X = df[feature_columns].copy()
    y = df[target_column].values

    # --- train / test split ---
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # --- train / validation split ---
    # val_size is fraction of total dataset; adjust relative to train_full
    val_relative = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=val_relative, random_state=random_state
    )

    print(f"\nData split:")
    print(f"  Train size: {len(X_train)}")
    print(f"  Val   size: {len(X_val)}")
    print(f"  Test  size: {len(X_test)}")

    # Build preprocessing based on training data only
    preprocessor, num_cols, cat_cols = build_preprocessor(X_train)
    print("\nDetected numeric features:", num_cols)
    print("Detected categorical features:", cat_cols)

    # Choose model
    if model_type == "linear":
        reg = LinearRegression()
        print("\nUsing LinearRegression as baseline.")
    elif model_type == "ridge":
        # RidgeCV tries multiple alphas and selects the best
        alphas = np.logspace(-3, 3, 13)
        reg = RidgeCV(alphas=alphas)
        print("\nUsing RidgeCV as baseline. Alphas:", alphas)
    else:
        raise ValueError("model_type must be 'linear' or 'ridge'.")

    # Full pipeline
    model = Pipeline(steps=[("preprocessor", preprocessor), ("model", reg)])

    # Train on training split
    model.fit(X_train, y_train)

    # Predictions
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)
    y_test_pred = model.predict(X_test)

    # Evaluation
    evaluate_split("Train", y_train, y_train_pred)
    evaluate_split("Validation", y_val, y_val_pred)
    evaluate_split("Test", y_test, y_test_pred)

    return model

if __name__ == "__main__":
    GEOJSON_PATH = "data/example.geojson"
    TARGET_COLUMN = "temperature"  # e.g., the meteorological variable you want to predict

    # You can specify feature columns explicitly, for example:
    # FEATURE_COLUMNS = ["longitude", "latitude", "elevation", "land_use"]
    # If None, all columns except TARGET_COLUMN will be used.
    FEATURE_COLUMNS = None

    # Load and prepare data
    gj = load_geojson(GEOJSON_PATH)
    df = geojson_to_dataframe(gj)

    print("First few columns of the DataFrame:")
    print(df.head())

    # Run baseline
    model = run_baseline_regression(
        df=df,
        target_column=TARGET_COLUMN,
        feature_columns=FEATURE_COLUMNS,
        model_type="ridge",
        test_size=0.2,
        val_size=0.2,
        random_state=42,
    )