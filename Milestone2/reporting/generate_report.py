# Import pandas for reading and processing our CSV files.
import pandas as pd

# Import Path so that file paths work correctly from the project folder.
from pathlib import Path


# ---------------------------------------------------------
# 1. FIND THE PROJECT ROOT
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. DEFINE THE PROCESSED DATA LOCATION
# ---------------------------------------------------------

PROCESSED_DIR = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
)

SEGMENT_DIR = (
    BASE_DIR
    / "Milestone2"
    / "segmentation"
    / "processed"
)


# ---------------------------------------------------------
# 3. LOAD CUSTOMER SEGMENT DATA
# ---------------------------------------------------------

print("Loading customer segmentation results...")

segment_file = (
    SEGMENT_DIR
    / "customer_segments_final.csv"
)

segment_df = pd.read_csv(segment_file)

print(f"Customers loaded: {len(segment_df)}")


# ---------------------------------------------------------
# 4. CREATE CUSTOMER SEGMENT SUMMARY
# ---------------------------------------------------------

segment_summary = (
    segment_df
    .groupby("customer_segment")
    .agg(
        customer_count=("CustomerID", "count"),
        average_purchase_frequency=(
            "purchase_frequency",
            "mean"
        ),
        average_purchase_value=(
            "purchase_value",
            "mean"
        ),
        average_activity_days=(
            "customer_activity_days",
            "mean"
        )
    )
    .reset_index()
)


# Round numerical values to make the report easier to read.

segment_summary[
    "average_purchase_frequency"
] = segment_summary[
    "average_purchase_frequency"
].round(2)

segment_summary[
    "average_purchase_value"
] = segment_summary[
    "average_purchase_value"
].round(2)

segment_summary[
    "average_activity_days"
] = segment_summary[
    "average_activity_days"
].round(2)


# ---------------------------------------------------------
# 5. LOAD FORECASTING MODEL COMPARISON
# ---------------------------------------------------------

print("Loading forecasting model results...")

metrics_file = (
    PROCESSED_DIR
    / "all_model_metrics.csv"
)

metrics_df = pd.read_csv(metrics_file)

metrics_df["MAE"] = metrics_df["MAE"].round(2)
metrics_df["RMSE"] = metrics_df["RMSE"].round(2)


# ---------------------------------------------------------
# 6. LOAD PROPHET FORECAST
# ---------------------------------------------------------

print("Loading sales forecast...")

forecast_file = (
    PROCESSED_DIR
    / "prophet_forecast.csv"
)

forecast_df = pd.read_csv(forecast_file)

forecast_df["ds"] = pd.to_datetime(
    forecast_df["ds"]
)


# Keep the final 30 forecast records.
sales_forecast = forecast_df.tail(30).copy()

sales_forecast = sales_forecast[
    [
        "ds",
        "yhat",
        "yhat_lower",
        "yhat_upper"
    ]
]

sales_forecast["yhat"] = sales_forecast[
    "yhat"
].round(2)

sales_forecast["yhat_lower"] = sales_forecast[
    "yhat_lower"
].round(2)

sales_forecast["yhat_upper"] = sales_forecast[
    "yhat_upper"
].round(2)


# ---------------------------------------------------------
# 7. CREATE REPORT FOLDER
# ---------------------------------------------------------

REPORT_DIR = (
    BASE_DIR
    / "Milestone2"
    / "reporting"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# 8. CREATE EXCEL REPORT
# ---------------------------------------------------------

report_file = (
    REPORT_DIR
    / "business_report.xlsx"
)

print("\nCreating business report...")


with pd.ExcelWriter(
    report_file,
    engine="openpyxl"
) as writer:

    # Sheet 1: Customer Segments
    segment_summary.to_excel(
        writer,
        sheet_name="Customer Segments",
        index=False
    )

    # Sheet 2: Model Comparison
    metrics_df.to_excel(
        writer,
        sheet_name="Model Comparison",
        index=False
    )

    # Sheet 3: Sales Forecast
    sales_forecast.to_excel(
        writer,
        sheet_name="Sales Forecast",
        index=False
    )


# ---------------------------------------------------------
# 9. DISPLAY SUMMARY
# ---------------------------------------------------------

print("\nCustomer Segment Summary:")
print(
    segment_summary.to_string(
        index=False
    )
)

print("\nForecasting Model Comparison:")
print(
    metrics_df.to_string(
        index=False
    )
)

print("\nBusiness report created successfully!")

print(
    f"Saved to: {report_file}"
)