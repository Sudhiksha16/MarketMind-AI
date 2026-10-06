# ============================================================
# MarketMind AI - Milestone 3
# Day 5-6: Churn Prediction Setup
# ============================================================

import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Cleaned sales data created during Milestone 1
SALES_FILE = (
    PROJECT_ROOT
    / "Milestone1"
    / "preprocessing"
    / "processed"
    / "cleaned_sales.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Milestone3"
    / "churn"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# 2. Load cleaned sales data
# ------------------------------------------------------------

print("=" * 60)
print("LOADING CLEANED SALES DATA")
print("=" * 60)

sales_df = pd.read_csv(
    SALES_FILE,
    encoding="latin1"
)

print(
    f"Sales records loaded: "
    f"{len(sales_df):,}"
)


# ------------------------------------------------------------
# 3. Convert required columns
# ------------------------------------------------------------

# Convert InvoiceDate into a real datetime value
sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"],
    errors="coerce"
)

# Remove records where the date could not be converted
sales_df = sales_df.dropna(
    subset=["InvoiceDate"]
)

# Make sure TotalAmount exists
# Quantity × UnitPrice represents the transaction value.
if "TotalAmount" not in sales_df.columns:

    sales_df["TotalAmount"] = (
        sales_df["Quantity"]
        * sales_df["UnitPrice"]
    )


# ------------------------------------------------------------
# 4. Remove records without CustomerID
# ------------------------------------------------------------

# Churn prediction is customer-level analysis.
# Therefore, we need to know which customer made each order.

sales_df = sales_df.dropna(
    subset=["CustomerID"]
)

# Keep CustomerID consistent
sales_df["CustomerID"] = (
    sales_df["CustomerID"]
    .astype(int)
    .astype(str)
)


# ------------------------------------------------------------
# 5. Define the reference date
# ------------------------------------------------------------

# IMPORTANT:
#
# Our dataset contains historical transactions from 2010-2011.
# Using the actual current date would make almost every customer
# appear to have churned.
#
# Therefore, we use one day after the latest transaction date
# as the reference date.

reference_date = (
    sales_df["InvoiceDate"].max()
    + pd.Timedelta(days=1)
)

print(
    f"\nLatest transaction date: "
    f"{sales_df['InvoiceDate'].max()}"
)

print(
    f"Churn reference date: "
    f"{reference_date}"
)


# ------------------------------------------------------------
# 6. Build customer-level churn features
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("BUILDING CUSTOMER CHURN FEATURES")
print("=" * 60)

churn_features = (
    sales_df
    .groupby("CustomerID")
    .agg(
        # Number of unique invoices/orders
        order_frequency=(
            "InvoiceNo",
            "nunique"
        ),

        # Most recent purchase
        last_purchase_date=(
            "InvoiceDate",
            "max"
        ),

        # Average transaction/order value
        avg_order_value=(
            "TotalAmount",
            "mean"
        )
    )
    .reset_index()
)


# ------------------------------------------------------------
# 7. Calculate purchase inactivity
# ------------------------------------------------------------

churn_features[
    "purchase_inactivity_days"
] = (
    reference_date
    - churn_features["last_purchase_date"]
).dt.days


# ------------------------------------------------------------
# 8. Define churn label
# ------------------------------------------------------------

# Mentor definition:
#
# More than 90 days without a purchase
# = Churned
#
# 1 = Churned
# 0 = Still Active

churn_features["churned"] = (
    churn_features[
        "purchase_inactivity_days"
    ] > 90
).astype(int)


# ------------------------------------------------------------
# 9. Display churn distribution
# ------------------------------------------------------------

print("\nChurn distribution:")
print(
    churn_features[
        "churned"
    ].value_counts()
)

print("\nChurn percentage:")
print(
    (
        churn_features["churned"]
        .value_counts(normalize=True)
        * 100
    ).round(2)
)


# ------------------------------------------------------------
# 10. Display customer features
# ------------------------------------------------------------

print("\nCustomer Churn Features")
print("-" * 60)

print(
    churn_features[
        [
            "CustomerID",
            "order_frequency",
            "last_purchase_date",
            "avg_order_value",
            "purchase_inactivity_days",
            "churned"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 11. Save churn feature dataset
# ------------------------------------------------------------

FEATURE_FILE = (
    OUTPUT_DIR
    / "customer_churn_features.csv"
)

churn_features.to_csv(
    FEATURE_FILE,
    index=False
)

print(
    f"\nChurn features saved to:\n"
    f"{FEATURE_FILE}"
)


# ============================================================
# 12. Prepare features and target
# ============================================================

print("\n" + "=" * 60)
print("PREPARING MODEL DATA")
print("=" * 60)

feature_cols = [
    "order_frequency",
    "purchase_inactivity_days",
    "avg_order_value"
]

X = churn_features[
    feature_cols
]

y = churn_features[
    "churned"
]


# ------------------------------------------------------------
# 13. Train/test split
# ------------------------------------------------------------

# stratify=y keeps approximately the same proportion
# of churned and active customers in both datasets.

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
)

print(
    f"Training customers: {len(X_train):,}"
)

print(
    f"Testing customers: {len(X_test):,}"
)


# ------------------------------------------------------------
# 14. Scale features
# ------------------------------------------------------------

# Logistic Regression benefits from features
# being on comparable numerical scales.

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)


# ------------------------------------------------------------
# 15. Train Logistic Regression
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("TRAINING LOGISTIC REGRESSION")
print("=" * 60)

log_model = LogisticRegression(
    random_state=42
)

log_model.fit(
    X_train_scaled,
    y_train
)


# ------------------------------------------------------------
# 16. Generate predictions
# ------------------------------------------------------------

log_predictions = (
    log_model.predict(
        X_test_scaled
    )
)


# ------------------------------------------------------------
# 17. Calculate initial accuracy
# ------------------------------------------------------------

accuracy = accuracy_score(
    y_test,
    log_predictions
)

print(
    f"\nLogistic Regression Accuracy: "
    f"{accuracy:.2%}"
)


# ------------------------------------------------------------
# 18. Display sample predictions
# ------------------------------------------------------------

print("\nSample predictions:")
print(
    log_predictions[:10]
)


# ------------------------------------------------------------
# 19. Save test predictions
# ------------------------------------------------------------

test_results = X_test.copy()

test_results["actual_churn"] = (
    y_test.values
)

test_results["predicted_churn"] = (
    log_predictions
)

prediction_file = (
    OUTPUT_DIR
    / "logistic_regression_predictions.csv"
)

test_results.to_csv(
    prediction_file,
    index=False
)


# ------------------------------------------------------------
# 20. Final status
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CHURN PREDICTION SETUP COMPLETED")
print("=" * 60)

print(
    f"Feature dataset:\n"
    f"{FEATURE_FILE}"
)

print(
    f"\nPrediction dataset:\n"
    f"{prediction_file}"
)

print(
    "\nLogistic Regression baseline is ready "
    "for Day 7-8 model comparison."
)