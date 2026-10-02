# Import pandas for reading and processing the dataset.
import pandas as pd

# Import Path for reliable file paths.
from pathlib import Path

# Random Forest regression model.
from sklearn.ensemble import RandomForestRegressor

# XGBoost regression model.
from xgboost import XGBRegressor

# Metrics used to measure forecasting error.
from sklearn.metrics import mean_absolute_error, mean_squared_error

# NumPy is used for calculating RMSE.
import numpy as np


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD ML FEATURE DATA
# ---------------------------------------------------------

input_file = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
    / "ml_features.csv"
)

print("Loading ML feature data...")

df = pd.read_csv(input_file)

df["Date"] = pd.to_datetime(df["Date"])

# Sort chronologically.
df = df.sort_values("Date").reset_index(drop=True)

print(f"Records loaded: {len(df)}")


# ---------------------------------------------------------
# 3. SELECT INPUT FEATURES
# ---------------------------------------------------------

feature_columns = [
    "day_of_week",
    "day_of_month",
    "month",
    "lag_1",
    "lag_7",
    "rolling_7"
]

# X = information used by the models to make predictions.
X = df[feature_columns]

# y = actual revenue that we want to predict.
y = df["TotalAmount"]


# ---------------------------------------------------------
# 4. CREATE A TIME-BASED TRAIN/TEST SPLIT
# ---------------------------------------------------------

# We must NOT randomly shuffle time-series data.
#
# Earlier data → training
# Later data  → testing
#
# Here, 80% of the historical observations are used
# for training and the final 20% are used for testing.

split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

dates_test = df["Date"].iloc[split_index:]


print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# ---------------------------------------------------------
# 5. TRAIN RANDOM FOREST
# ---------------------------------------------------------

print("\nTraining Random Forest...")

random_forest = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

random_forest.fit(
    X_train,
    y_train
)

# Predict revenue for the test period.
rf_predictions = random_forest.predict(X_test)

print("Random Forest training completed.")


# ---------------------------------------------------------
# 6. TRAIN XGBOOST
# ---------------------------------------------------------

print("\nTraining XGBoost...")

xgboost_model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    random_state=42,
    objective="reg:squarederror"
)

xgboost_model.fit(
    X_train,
    y_train
)

# Predict revenue for the test period.
xgb_predictions = xgboost_model.predict(X_test)

print("XGBoost training completed.")


# ---------------------------------------------------------
# 7. CALCULATE RANDOM FOREST METRICS
# ---------------------------------------------------------

rf_mae = mean_absolute_error(
    y_test,
    rf_predictions
)

rf_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        rf_predictions
    )
)


# ---------------------------------------------------------
# 8. CALCULATE XGBOOST METRICS
# ---------------------------------------------------------

xgb_mae = mean_absolute_error(
    y_test,
    xgb_predictions
)

xgb_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        xgb_predictions
    )
)


# ---------------------------------------------------------
# 9. DISPLAY MODEL PERFORMANCE
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print("\nRandom Forest:")
print(f"MAE  : {rf_mae:.2f}")
print(f"RMSE : {rf_rmse:.2f}")

print("\nXGBoost:")
print(f"MAE  : {xgb_mae:.2f}")
print(f"RMSE : {xgb_rmse:.2f}")


# ---------------------------------------------------------
# 10. SAVE TEST PREDICTIONS
# ---------------------------------------------------------

predictions = pd.DataFrame({
    "Date": dates_test,
    "Actual_Revenue": y_test.values,
    "Random_Forest_Prediction": rf_predictions,
    "XGBoost_Prediction": xgb_predictions
})


# ---------------------------------------------------------
# 11. SAVE MODEL RESULTS
# ---------------------------------------------------------

OUTPUT_DIR = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

prediction_file = (
    OUTPUT_DIR
    / "ml_forecast_predictions.csv"
)

predictions.to_csv(
    prediction_file,
    index=False
)


# ---------------------------------------------------------
# 12. SAVE METRICS
# ---------------------------------------------------------

metrics = pd.DataFrame({
    "Model": [
        "Random Forest",
        "XGBoost"
    ],
    "MAE": [
        rf_mae,
        xgb_mae
    ],
    "RMSE": [
        rf_rmse,
        xgb_rmse
    ]
})

metrics_file = (
    OUTPUT_DIR
    / "ml_model_metrics.csv"
)

metrics.to_csv(
    metrics_file,
    index=False
)


# ---------------------------------------------------------
# 13. COMPLETION MESSAGE
# ---------------------------------------------------------

print("\nML forecasting completed successfully!")

print(f"Predictions saved to: {prediction_file}")

print(f"Metrics saved to: {metrics_file}")