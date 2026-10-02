# Import pandas for reading and processing the datasets.
import pandas as pd

# Import Path for reliable project paths.
from pathlib import Path

# Import Prophet.
from prophet import Prophet

# Import the evaluation metrics.
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Import NumPy for calculating RMSE.
import numpy as np


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD THE PROPHET DATA
# ---------------------------------------------------------

prophet_file = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
    / "prophet_sales.csv"
)

prophet_data = pd.read_csv(prophet_file)

prophet_data["ds"] = pd.to_datetime(prophet_data["ds"])


# ---------------------------------------------------------
# 3. LOAD THE ML TEST DATA
# ---------------------------------------------------------

# This tells us exactly which 60 dates were used
# to evaluate Random Forest and XGBoost.

ml_file = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
    / "ml_features.csv"
)

ml_data = pd.read_csv(ml_file)

ml_data["Date"] = pd.to_datetime(ml_data["Date"])

# The ML script used the final 20% as its test period.
split_index = int(len(ml_data) * 0.80)

test_data = ml_data.iloc[split_index:].copy()

test_start_date = test_data["Date"].min()

print("Prophet evaluation test period:")
print("Start:", test_data["Date"].min())
print("End  :", test_data["Date"].max())
print("Test records:", len(test_data))


# ---------------------------------------------------------
# 4. CREATE PROPHET TRAINING DATA
# ---------------------------------------------------------

# Only use dates BEFORE the ML test period for training.
prophet_train = prophet_data[
    prophet_data["ds"] < test_start_date
].copy()

print("\nProphet training records:", len(prophet_train))


# ---------------------------------------------------------
# 5. TRAIN PROPHET
# ---------------------------------------------------------

print("\nTraining Prophet for evaluation...")

model = Prophet()

model.fit(
    prophet_train[
        ["ds", "y"]
    ]
)

print("Prophet evaluation model trained successfully.")


# ---------------------------------------------------------
# 6. CREATE TEST-DATE DATA
# ---------------------------------------------------------

# Ask Prophet to predict exactly the same dates
# used by Random Forest and XGBoost.

future_test = pd.DataFrame({
    "ds": test_data["Date"]
})


# ---------------------------------------------------------
# 7. GENERATE PROPHET PREDICTIONS
# ---------------------------------------------------------

forecast = model.predict(future_test)

prophet_predictions = forecast["yhat"].values

actual_values = test_data["TotalAmount"].values


# ---------------------------------------------------------
# 8. CALCULATE MAE
# ---------------------------------------------------------

prophet_mae = mean_absolute_error(
    actual_values,
    prophet_predictions
)


# ---------------------------------------------------------
# 9. CALCULATE RMSE
# ---------------------------------------------------------

prophet_rmse = np.sqrt(
    mean_squared_error(
        actual_values,
        prophet_predictions
    )
)


# ---------------------------------------------------------
# 10. DISPLAY RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("PROPHET TEST PERFORMANCE")
print("=" * 60)

print(f"MAE  : {prophet_mae:.2f}")
print(f"RMSE : {prophet_rmse:.2f}")


# ---------------------------------------------------------
# 11. SAVE PROPHET TEST PREDICTIONS
# ---------------------------------------------------------

predictions = pd.DataFrame({
    "Date": test_data["Date"],
    "Actual_Revenue": actual_values,
    "Prophet_Prediction": prophet_predictions
})

OUTPUT_DIR = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
)

prediction_file = (
    OUTPUT_DIR
    / "prophet_test_predictions.csv"
)

predictions.to_csv(
    prediction_file,
    index=False
)


# ---------------------------------------------------------
# 12. COMBINE ALL MODEL METRICS
# ---------------------------------------------------------

ml_metrics_file = (
    OUTPUT_DIR
    / "ml_model_metrics.csv"
)

ml_metrics = pd.read_csv(ml_metrics_file)

prophet_metrics = pd.DataFrame({
    "Model": ["Prophet"],
    "MAE": [prophet_mae],
    "RMSE": [prophet_rmse]
})

all_metrics = pd.concat(
    [
        ml_metrics,
        prophet_metrics
    ],
    ignore_index=True
)

all_metrics_file = (
    OUTPUT_DIR
    / "all_model_metrics.csv"
)

all_metrics.to_csv(
    all_metrics_file,
    index=False
)


# ---------------------------------------------------------
# 13. COMPLETION MESSAGE
# ---------------------------------------------------------

print("\nAll-model comparison saved successfully!")

print(all_metrics.to_string(index=False))

print(
    f"\nSaved to: {all_metrics_file}"
)

print(
    f"Prophet predictions saved to: {prediction_file}"
)