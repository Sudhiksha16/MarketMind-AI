# Import pandas for reading and manipulating the sales data.
import pandas as pd

# Import Path for creating reliable project paths.
from pathlib import Path


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD DAILY SALES DATA
# ---------------------------------------------------------

input_file = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
    / "daily_sales.csv"
)

print("Loading daily sales data...")

df = pd.read_csv(input_file)

# Convert Date from text into datetime.
df["Date"] = pd.to_datetime(df["Date"])

# Make sure the data is in chronological order.
df = df.sort_values("Date").reset_index(drop=True)

print(f"Daily records loaded: {len(df)}")


# ---------------------------------------------------------
# 3. CREATE CALENDAR FEATURES
# ---------------------------------------------------------

# Day of the week:
# Monday = 0
# Sunday = 6
df["day_of_week"] = df["Date"].dt.dayofweek

# Day number within the month.
df["day_of_month"] = df["Date"].dt.day

# Month number.
df["month"] = df["Date"].dt.month


# ---------------------------------------------------------
# 4. CREATE LAG FEATURES
# ---------------------------------------------------------

# Revenue from the previous recorded day.
df["lag_1"] = df["TotalAmount"].shift(1)

# Revenue from the previous 7 recorded observations.
df["lag_7"] = df["TotalAmount"].shift(7)


# ---------------------------------------------------------
# 5. CREATE 7-DAY ROLLING AVERAGE
# ---------------------------------------------------------

# Average revenue from the previous 7 observations.
#
# shift(1) prevents the current day's revenue from being
# included in its own input features.

df["rolling_7"] = (
    df["TotalAmount"]
    .shift(1)
    .rolling(window=7)
    .mean()
)


# ---------------------------------------------------------
# 6. REMOVE ROWS WITH MISSING FEATURES
# ---------------------------------------------------------

# lag_7 and rolling_7 cannot be calculated for the first
# few observations because there aren't enough previous
# records.

df = df.dropna().reset_index(drop=True)


# ---------------------------------------------------------
# 7. DISPLAY THE RESULT
# ---------------------------------------------------------

print("\nML feature dataset:")

print(
    df[
        [
            "Date",
            "TotalAmount",
            "day_of_week",
            "day_of_month",
            "month",
            "lag_1",
            "lag_7",
            "rolling_7"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 8. DISPLAY DATASET SIZE
# ---------------------------------------------------------

print("\nRecords after feature engineering:")
print(len(df))


# ---------------------------------------------------------
# 9. SAVE THE ML FEATURE DATASET
# ---------------------------------------------------------

output_file = (
    BASE_DIR
    / "Milestone2"
    / "forecasting"
    / "processed"
    / "ml_features.csv"
)

df.to_csv(
    output_file,
    index=False
)

print("\nML feature preparation completed successfully!")

print(f"Saved to: {output_file}")