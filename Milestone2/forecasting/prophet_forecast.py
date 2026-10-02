# Import pandas to read and process the Prophet-ready data.
import pandas as pd

# Import Path to create reliable project file paths.
from pathlib import Path

# Import Prophet, the time-series forecasting model.
from prophet import Prophet


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD PROPHET-READY DATA
# ---------------------------------------------------------

input_file = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
    / "prophet_sales.csv"
)

print("Loading Prophet-ready sales data...")

prophet_df = pd.read_csv(input_file)

# Convert the ds column back into datetime format.
prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])

print(f"Historical records loaded: {len(prophet_df)}")

print("\nHistorical data:")
print(prophet_df.head(10).to_string(index=False))


# ---------------------------------------------------------
# 3. CREATE THE PROPHET MODEL
# ---------------------------------------------------------

# Prophet will learn the historical trend and seasonality
# from our sales data.

model = Prophet()


# ---------------------------------------------------------
# 4. TRAIN THE MODEL
# ---------------------------------------------------------

print("\nTraining Prophet model...")

model.fit(prophet_df)

print("Prophet model trained successfully!")


# ---------------------------------------------------------
# 5. CREATE FUTURE DATES
# ---------------------------------------------------------

# The Milestone 2 guide uses a 30-day forecast horizon.

future = model.make_future_dataframe(
    periods=30
)

print("\nFuture dates created.")


# ---------------------------------------------------------
# 6. GENERATE THE FORECAST
# ---------------------------------------------------------

print("Generating 30-day sales forecast...")

forecast = model.predict(future)


# ---------------------------------------------------------
# 7. DISPLAY FORECAST RESULTS
# ---------------------------------------------------------

# yhat       = predicted revenue
# yhat_lower = lower uncertainty estimate
# yhat_upper = upper uncertainty estimate

print("\nNext 10 forecast values:")

print(
    forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper"
        ]
    ]
    .tail(10)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 8. CREATE OUTPUT DIRECTORY
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


# ---------------------------------------------------------
# 9. SAVE FORECAST DATA
# ---------------------------------------------------------

forecast_file = (
    OUTPUT_DIR
    / "prophet_forecast.csv"
)

forecast[
    [
        "ds",
        "yhat",
        "yhat_lower",
        "yhat_upper"
    ]
].to_csv(
    forecast_file,
    index=False
)


# ---------------------------------------------------------
# 10. CREATE FORECAST VISUALIZATION
# ---------------------------------------------------------

print("\nCreating forecast graph...")

fig = model.plot(forecast)

forecast_image = (
    OUTPUT_DIR
    / "revenue_forecast.png"
)

fig.savefig(
    forecast_image,
    bbox_inches="tight"
)


# ---------------------------------------------------------
# 11. CREATE TREND/SEASONALITY VISUALIZATION
# ---------------------------------------------------------

print("Creating forecast components graph...")

fig2 = model.plot_components(forecast)

components_image = (
    OUTPUT_DIR
    / "forecast_components.png"
)

fig2.savefig(
    components_image,
    bbox_inches="tight"
)


# ---------------------------------------------------------
# 12. COMPLETION MESSAGE
# ---------------------------------------------------------

print("\nProphet forecasting completed successfully!")

print(f"Forecast data saved to: {forecast_file}")

print(f"Forecast graph saved to: {forecast_image}")

print(f"Forecast components saved to: {components_image}")