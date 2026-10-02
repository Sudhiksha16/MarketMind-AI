# Import pandas so we can work with the sales dataset.
import pandas as pd

# Import Path so our file paths work correctly.
from pathlib import Path


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

# __file__ gives the location of this Python file.
# parent = segmentation folder
# parent.parent = Milestone2 folder
# parent.parent.parent = MarketMind AI folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD THE CLEANED SALES DATA
# ---------------------------------------------------------

# This is the cleaned sales file created during Milestone 1.
sales_file = (
    BASE_DIR
    / "Milestone1"
    / "preprocessing"
    / "processed"
    / "cleaned_sales.csv"
)

print("Loading cleaned sales data...")

# Read the CSV file.
# low_memory=False prevents the mixed-type warning for InvoiceNo
# while reading the complete dataset.
sales_df = pd.read_csv(
    sales_file,
    encoding="latin1",
    low_memory=False
)

print(f"Total sales records loaded: {len(sales_df)}")


# ---------------------------------------------------------
# 3. PREPARE THE DATE COLUMN
# ---------------------------------------------------------

# Convert InvoiceDate from text into pandas datetime format.
# This allows us to calculate how recently each customer purchased.
sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"],
    errors="coerce"
)


# ---------------------------------------------------------
# 4. REMOVE RECORDS WITHOUT A CUSTOMER ID
# ---------------------------------------------------------

# Customer segmentation requires a known customer.
# Therefore, transactions without CustomerID cannot be
# assigned to a customer segment.
sales_df = sales_df.dropna(subset=["CustomerID"])

print(f"Records with customer IDs: {len(sales_df)}")


# ---------------------------------------------------------
# 5. CREATE CUSTOMER-LEVEL FEATURES
# ---------------------------------------------------------

# We start with today's date based on the latest date
# available in our dataset.
reference_date = sales_df["InvoiceDate"].max()

# groupby("CustomerID") changes the data from:
#
#       ONE ROW = ONE TRANSACTION
#
# into:
#
#       ONE ROW = ONE CUSTOMER
#
# We calculate the three features required for segmentation.
customer_features = (
    sales_df
    .groupby("CustomerID")
    .agg(
        # How many invoices/orders the customer has made.
        purchase_frequency=("InvoiceNo", "nunique"),

        # Total amount spent by the customer.
        purchase_value=("TotalAmount", "sum"),

        # Most recent purchase date.
        last_purchase_date=("InvoiceDate", "max")
    )
    .reset_index()
)


# ---------------------------------------------------------
# 6. CALCULATE CUSTOMER ACTIVITY
# ---------------------------------------------------------

# Calculate how many days have passed since each customer's
# last purchase.
#
# Smaller value = more recently active customer.
# Larger value = customer has been inactive for longer.
customer_features["customer_activity_days"] = (
    reference_date - customer_features["last_purchase_date"]
).dt.days


# ---------------------------------------------------------
# 7. SELECT THE FINAL FEATURES
# ---------------------------------------------------------

# Keep only the columns needed for Milestone 2
# customer segmentation.
customer_features = customer_features[
    [
        "CustomerID",
        "purchase_frequency",
        "purchase_value",
        "customer_activity_days"
    ]
]


# ---------------------------------------------------------
# 8. DISPLAY THE RESULT
# ---------------------------------------------------------

print("\nCustomer-level features:")
print(customer_features.head(10).to_string(index=False))

print("\nNumber of customers:")
print(len(customer_features))

print("\nFeature information:")
print(customer_features.info())


# ---------------------------------------------------------
# 9. SAVE THE CUSTOMER FEATURES
# ---------------------------------------------------------

# Create a folder for Milestone 2 processed data.
OUTPUT_DIR = BASE_DIR / "Milestone2" / "segmentation" / "processed"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# Save the customer-level dataset.
output_file = OUTPUT_DIR / "customer_features.csv"

customer_features.to_csv(
    output_file,
    index=False
)

print("\nCustomer feature file created successfully!")
print(f"Saved to: {output_file}")