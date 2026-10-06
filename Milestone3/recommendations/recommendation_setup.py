# ============================================================
# MarketMind AI - Milestone 3
# Day 1-2: Recommendation Engine Setup
# Collaborative Filtering
# ============================================================

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# 1. Find the project folders
# ------------------------------------------------------------

# __file__ gives the location of this Python file.
# .parent = recommendations folder
# .parent.parent = Milestone3
# .parent.parent.parent = MarketMind AI

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Location of the cleaned sales data created in Milestone 1
SALES_FILE = (
    PROJECT_ROOT
    / "Milestone1"
    / "preprocessing"
    / "processed"
    / "cleaned_sales.csv"
)

# Folder where Milestone 3 recommendation outputs will be stored
OUTPUT_DIR = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
)

# Create the output folder if it does not already exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Load cleaned sales data
# ------------------------------------------------------------

print("=" * 60)
print("LOADING CLEANED SALES DATA")
print("=" * 60)

sales_df = pd.read_csv(SALES_FILE, encoding="latin1")

print(f"Total sales records: {len(sales_df):,}")
print(f"Columns: {list(sales_df.columns)}")


# ------------------------------------------------------------
# 3. Keep the columns needed for recommendations
# ------------------------------------------------------------

recommendation_df = sales_df[
    [
        "CustomerID",
        "StockCode",
        "Description",
        "Quantity"
    ]
].copy()


# ------------------------------------------------------------
# 4. Remove transactions without a customer ID
# ------------------------------------------------------------

# Collaborative filtering needs to know WHICH customer
# purchased WHICH product.
#
# Therefore, transactions without CustomerID cannot be
# directly used for customer-based recommendations.

recommendation_df = recommendation_df.dropna(
    subset=["CustomerID"]
)


# ------------------------------------------------------------
# 5. Remove records without product information
# ------------------------------------------------------------

recommendation_df = recommendation_df.dropna(
    subset=["StockCode", "Description"]
)


# ------------------------------------------------------------
# 6. Convert CustomerID into a consistent format
# ------------------------------------------------------------

recommendation_df["CustomerID"] = (
    recommendation_df["CustomerID"]
    .astype(int)
    .astype(str)
)


# ------------------------------------------------------------
# 7. Create customer-product purchase interactions
# ------------------------------------------------------------

# A customer may purchase the same product multiple times.
#
# Instead of keeping every transaction separately,
# we combine them.
#
# Example:
#
# Customer 1001 buys Product A 3 times
# Customer 1001 buys Product A 2 times
#
# becomes:
#
# Customer 1001 -> Product A -> Quantity 5

customer_product = (
    recommendation_df
    .groupby(
        ["CustomerID", "StockCode", "Description"],
        as_index=False
    )["Quantity"]
    .sum()
)


# ------------------------------------------------------------
# 8. Display the interaction data
# ------------------------------------------------------------

print("\nCustomer-Product Interaction Data")
print("-" * 60)

print(customer_product.head(10).to_string(index=False))


# ------------------------------------------------------------
# 9. Create a customer-product matrix
# ------------------------------------------------------------

# Rows    = Customers
# Columns = Products
# Values  = Quantity purchased
#
# Example:
#
#             Product A   Product B   Product C
# Customer 1      5           0           2
# Customer 2      3           4           0
# Customer 3      0           2           7

interaction_matrix = customer_product.pivot_table(
    index="CustomerID",
    columns="StockCode",
    values="Quantity",
    aggfunc="sum",
    fill_value=0
)


# ------------------------------------------------------------
# 10. Display matrix information
# ------------------------------------------------------------

print("\nInteraction Matrix")
print("-" * 60)

print(
    f"Number of customers: {interaction_matrix.shape[0]:,}"
)

print(
    f"Number of products: {interaction_matrix.shape[1]:,}"
)


# ------------------------------------------------------------
# 11. Save the interaction matrix
# ------------------------------------------------------------

matrix_file = OUTPUT_DIR / "customer_product_matrix.csv"

interaction_matrix.to_csv(matrix_file)


# ------------------------------------------------------------
# 12. Save the cleaned recommendation input
# ------------------------------------------------------------

interaction_file = (
    OUTPUT_DIR / "customer_product_interactions.csv"
)

customer_product.to_csv(
    interaction_file,
    index=False
)


# ------------------------------------------------------------
# 13. Final status
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("RECOMMENDATION DATA PREPARATION COMPLETED")
print("=" * 60)

print(f"Interaction data saved to:")
print(interaction_file)

print(f"\nCustomer-product matrix saved to:")
print(matrix_file)