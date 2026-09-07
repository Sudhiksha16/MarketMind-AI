import pandas as pd
from pathlib import Path


# Find the project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset locations
sales_file = BASE_DIR / "datasets" / "OnlineRetail.csv"
customer_file = BASE_DIR / "datasets" / "customer.xlsx"
inventory_file = BASE_DIR / "datasets" / "retail_store_inventory.csv"


def explore_data(name, file_path, file_type="csv"):
    print("\n" + "=" * 60)
    print(f"{name}")
    print("=" * 60)

    # Load dataset
    if file_type == "excel":
        df = pd.read_excel(file_path)
    else:
         df = pd.read_csv(file_path, encoding="latin1")

    # Basic information
    print(f"\nNumber of rows: {df.shape[0]}")
    print(f"Number of columns: {df.shape[1]}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nData types:")
    print(df.dtypes)

    return df


# Explore Sales Dataset
sales_df = explore_data(
    "ONLINE RETAIL SALES DATASET",
    sales_file
)

# Explore Customer Dataset
customer_df = explore_data(
    "CUSTOMER DATASET",
    customer_file,
    "excel"
)

# Explore Inventory Dataset
inventory_df = explore_data(
    "RETAIL STORE INVENTORY DATASET",
    inventory_file
)

print("\n" + "=" * 60)
print("DATA EXPLORATION COMPLETED")
print("=" * 60)