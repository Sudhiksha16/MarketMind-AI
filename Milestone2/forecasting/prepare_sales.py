# Import pandas for reading and processing the sales data.
import pandas as pd

# Import Path so we can create reliable project file paths.
from pathlib import Path


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

# This file is inside:
# MarketMind AI/Milestone2/forecasting/
#
# parent          -> forecasting
# parent.parent   -> Milestone2
# parent.parent.parent -> MarketMind AI

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD CLEANED SALES DATA
# ---------------------------------------------------------

sales_file = (
    BASE_DIR
    / "Milestone1"
    / "preprocessing"
    / "processed"
    / "cleaned_sales.csv"
)

print("Loading cleaned sales data...")

sales_df = pd.read_csv(
    sales_file,
    encoding="latin1",
    low_memory=False
)

print(f"Sales records loaded: {len(sales_df)}")


# ---------------------------------------------------------
# 3. CONVERT INVOICE DATE
# ---------------------------------------------------------

# Convert InvoiceDate from text into a datetime value.
sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"],
    errors="coerce"
)

# Remove records where the date could not be converted.
sales_df = sales_df.dropna(subset=["InvoiceDate"])


# ---------------------------------------------------------
# 4. CREATE A DATE-ONLY COLUMN
# ---------------------------------------------------------

# We only need the date for daily forecasting.
# The time part (hours/minutes/seconds) is removed.
sales_df["Date"] = sales_df["InvoiceDate"].dt.date


# ---------------------------------------------------------
# 5. CALCULATE DAILY REVENUE
# ---------------------------------------------------------

# Group all transactions belonging to the same date.
#
# Example:
#
# 2010-01-12 → ₹10,000
# 2010-01-13 → ₹12,500
# 2010-01-14 → ₹8,700
#
# This gives us one row per day.

daily_sales = (
    sales_df
    .groupby("Date")["TotalAmount"]
    .sum()
    .reset_index()
)


# ---------------------------------------------------------
# 6. CONVERT DATE BACK TO DATETIME
# ---------------------------------------------------------

daily_sales["Date"] = pd.to_datetime(
    daily_sales["Date"]
)


# ---------------------------------------------------------
# 7. SORT BY DATE
# ---------------------------------------------------------

# Time-series data must be in chronological order.
daily_sales = daily_sales.sort_values("Date")


# ---------------------------------------------------------
# 8. DISPLAY BASIC INFORMATION
# ---------------------------------------------------------

print("\nDaily sales data:")
print(daily_sales.head(10).to_string(index=False))

print("\nNumber of days with recorded sales:")
print(len(daily_sales))

print("\nFirst available date:")
print(daily_sales["Date"].min())

print("\nLast available date:")
print(daily_sales["Date"].max())


# ---------------------------------------------------------
# 9. CHECK FOR MISSING CALENDAR DATES
# ---------------------------------------------------------

# Create a complete calendar from the first date to
# the last date in the dataset.

complete_dates = pd.date_range(
    start=daily_sales["Date"].min(),
    end=daily_sales["Date"].max(),
    freq="D"
)

# Find dates that are present in the calendar but missing
# from the sales dataset.
missing_dates = complete_dates.difference(
    daily_sales["Date"]
)

print("\nNumber of missing calendar dates:")
print(len(missing_dates))

if len(missing_dates) > 0:
    print("\nFirst 20 missing dates:")
    print(missing_dates[:20])
else:
    print("No missing calendar dates found.")


# ---------------------------------------------------------
# 10. PREPARE PROPHET FORMAT
# ---------------------------------------------------------

# Prophet requires:
#
# ds = date
# y  = value being predicted
#
# So we rename our columns accordingly.

prophet_data = daily_sales.rename(
    columns={
        "Date": "ds",
        "TotalAmount": "y"
    }
)


# ---------------------------------------------------------
# 11. DISPLAY PROPHET DATA
# ---------------------------------------------------------

print("\nProphet-ready data:")
print(
    prophet_data
    .head(10)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 12. CREATE OUTPUT DIRECTORY
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
# 13. SAVE DAILY SALES DATA
# ---------------------------------------------------------

daily_sales_file = (
    OUTPUT_DIR
    / "daily_sales.csv"
)

daily_sales.to_csv(
    daily_sales_file,
    index=False
)


# ---------------------------------------------------------
# 14. SAVE PROPHET-READY DATA
# ---------------------------------------------------------

prophet_file = (
    OUTPUT_DIR
    / "prophet_sales.csv"
)

prophet_data.to_csv(
    prophet_file,
    index=False
)


# ---------------------------------------------------------
# 15. COMPLETION MESSAGE
# ---------------------------------------------------------

print("\nSales forecasting data preparation completed successfully!")

print(f"Daily sales saved to: {daily_sales_file}")
print(f"Prophet data saved to: {prophet_file}")