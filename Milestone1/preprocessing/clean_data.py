import pandas as pd
from pathlib import Path


# ==================================================
# Finding Milestone1 folder
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==================================================
# Input Dataset Locations
# ==================================================

sales_file = BASE_DIR / "datasets" / "OnlineRetail.csv"
inventory_file = BASE_DIR / "datasets" / "retail_store_inventory.csv"


# ==================================================
# Output Folder
# ==================================================

OUTPUT_DIR = BASE_DIR / "preprocessing" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 1. CLEAN SALES DATA
# ==================================================

print("Cleaning sales data...")

# Load sales dataset
sales_df = pd.read_csv(
    sales_file,
    encoding="latin1"
)

# Remove rows without essential product information
sales_df = sales_df.dropna(
    subset=["StockCode", "Description"]
)

# Remove duplicate transactions
sales_df = sales_df.drop_duplicates()

# Convert InvoiceDate to datetime
sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"],
    dayfirst=True,
    errors="coerce"
)

# Remove rows with invalid dates
sales_df = sales_df.dropna(
    subset=["InvoiceDate"]
)

# Keep only valid quantity and price values
sales_df = sales_df[
    (sales_df["Quantity"] > 0) &
    (sales_df["UnitPrice"] > 0)
]

# Calculate total transaction amount
sales_df["TotalAmount"] = (
    sales_df["Quantity"] *
    sales_df["UnitPrice"]
)

# Save cleaned sales data
sales_df.to_csv(
    OUTPUT_DIR / "cleaned_sales.csv",
    index=False
)

print(
    f"Cleaned sales records: {len(sales_df)}"
)


# ==================================================
# 2. CLEAN CUSTOMER DATA
# ==================================================

print("\nCleaning customer data...")

# Create customer data from cleaned sales data
customer_df = sales_df.dropna(
    subset=["CustomerID"]
).copy()

# Keep only one record for each customer
customer_df = customer_df.drop_duplicates(
    subset=["CustomerID"]
)

# Keep useful customer information
customer_df = customer_df[
    ["CustomerID", "Country"]
]

# Save cleaned customer data
customer_df.to_csv(
    OUTPUT_DIR / "cleaned_customer.csv",
    index=False
)

print(
    f"Cleaned customer records: {len(customer_df)}"
)


# ==================================================
# 3. CLEAN INVENTORY DATA
# ==================================================

print("\nCleaning inventory data...")

# Load inventory dataset
inventory_df = pd.read_csv(
    inventory_file
)

# Remove duplicate records
inventory_df = inventory_df.drop_duplicates()

# Convert Date to datetime
inventory_df["Date"] = pd.to_datetime(
    inventory_df["Date"],
    errors="coerce"
)

# Remove rows with invalid dates
inventory_df = inventory_df.dropna(
    subset=["Date"]
)

# Inventory level cannot be negative
inventory_df = inventory_df[
    inventory_df["Inventory Level"] >= 0
]

# Units sold and ordered cannot be negative
inventory_df = inventory_df[
    (inventory_df["Units Sold"] >= 0) &
    (inventory_df["Units Ordered"] >= 0)
]

# Save cleaned inventory data
inventory_df.to_csv(
    OUTPUT_DIR / "cleaned_inventory.csv",
    index=False
)

print(
    f"Cleaned inventory records: {len(inventory_df)}"
)


# ==================================================
# CLEANING COMPLETED
# ==================================================

print("\n" + "=" * 50)
print("DATA CLEANING COMPLETED")
print("=" * 50)

print(
    f"Cleaned files saved in: {OUTPUT_DIR}"
)