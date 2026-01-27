import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Path to the unified master dataset
DATA_FILE = "data_new/weather_data_all.csv"

# Column Mapping (matches weather_data_all.csv)
TARGET_COLUMN = "temperature"


# ==========================================
# 2. METRICS
# ==========================================
def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def print_metrics(y_true, y_pred, title: str) -> None:
    print(f"\n=== {title} ===")
    print(f"Global RMSE: {rmse(y_true, y_pred):.4f}")
    print(f"Global MAE : {mean_absolute_error(y_true, y_pred):.4f}")


# ==========================================
# 3. MODEL PIPELINE
# ==========================================
def build_location_time_baseline_pipeline(numeric_features: List[str]) -> Pipeline:
    """
    Numeric-only pipeline: impute median + scale + RandomForest.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), numeric_features),
        ],
        remainder="drop",
    )

    # Random Forest Configuration
    reg = RandomForestRegressor(
        n_estimators=150,
        max_depth=None,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", reg),
    ])


def run_leave_one_station_out_cv(
        data: pd.DataFrame,
        target_column: str,
        group_column: str,
        feature_columns: List[str],
) -> Tuple[Pipeline, pd.DataFrame]:
    """
    Leave-One-Station-Out evaluation using LeaveOneGroupOut.
    """
    # Filter data
    needed = set(feature_columns + [target_column, group_column])
    missing = [c for c in needed if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = data.dropna(subset=[target_column, group_column]).copy()

    X = df[feature_columns].copy()
    y = df[target_column].values
    groups = df[group_column].values

    # Build Pipeline
    model = build_location_time_baseline_pipeline(numeric_features=feature_columns)
    logo = LeaveOneGroupOut()

    print("🔄 Running Leave-One-Group-Out CV (Random Forest Baseline)...")
    # Hier wird für jede Station einmal trainiert (auf den anderen 9) und vorhergesagt
    y_pred = cross_val_predict(model, X, y, cv=logo, groups=groups, n_jobs=-1)

    # Globale Metriken ausgeben
    print_metrics(y, y_pred, title="GLOBAL RESULTS (Random Forest)")

    # Return results
    out = df.copy()
    out[f"{target_column}_pred"] = y_pred
    out[f"{target_column}_error"] = out[f"{target_column}_pred"] - out[target_column]

    return model, out


# ==========================================
# 4. MAIN
# ==========================================
if __name__ == "__main__":
    print(f"📂 Loading data from {DATA_FILE}...")
    try:
        data = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print("❌ Error: 'weather_data_all.csv' not found. Run 'unify_data.py' first!")
        exit()

    # Define Features
    FEATURE_COLUMNS = [
        "longitude",
        "latitude",
        "elevation",
        "hour",
        "dayofyear",
        "month",
        "weekday",
    ]

    print("\nFeature columns used:")
    print(FEATURE_COLUMNS)

    # Run Baseline
    model, df_with_preds = run_leave_one_station_out_cv(
        data=data,
        target_column=TARGET_COLUMN,
        group_column="station_id",
        feature_columns=FEATURE_COLUMNS,
    )

    # --- NEU: Detaillierte Ausgabe pro Station (wie beim CNN) ---
    print("\n" + "=" * 40)
    print("DETAILED STATION RESULTS")
    print("=" * 40)

    unique_stations = sorted(df_with_preds['station_id'].unique())
    station_stats = []

    for station in unique_stations:
        # Filter Data for this station
        subset = df_with_preds[df_with_preds['station_id'] == station]

        # Calculate RMSE & MAE specific to this station
        s_rmse = rmse(subset[TARGET_COLUMN], subset[f"{TARGET_COLUMN}_pred"])
        s_mae = mean_absolute_error(subset[TARGET_COLUMN], subset[f"{TARGET_COLUMN}_pred"])

        print(f"  -> Station {station} RMSE: {s_rmse:.4f}°C")

        station_stats.append({
            'station_id': station,
            'RMSE': s_rmse,
            'MAE': s_mae
        })

    # Summary Table
    print("\n" + "=" * 40)
    print("SUMMARY TABLE (Random Forest)")
    print("=" * 40)
    stats_df = pd.DataFrame(station_stats).set_index('station_id')
    print(stats_df)

    # Durchschnitt über alle Stationen
    avg_rmse = stats_df['RMSE'].mean()
    print("-" * 40)
    print(f"Average RMSE across all stations: {avg_rmse:.4f}°C")
    print("=" * 40)

    # Save CSV
    df_with_preds.to_csv("baseline_rf_results.csv", index=False)
    print("\n✅ Results saved to 'baseline_rf_results.csv'")