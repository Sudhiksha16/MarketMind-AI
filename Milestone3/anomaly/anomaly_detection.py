# ============================================================
# MarketMind AI - Milestone 3
# Day 9-10: Anomaly Detection
# ============================================================

import pandas as pd
from pathlib import Path

from sklearn.ensemble import IsolationForest


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

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
    / "anomaly"
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
# 3. Prepare required columns
# ------------------------------------------------------------

sales_df["Quantity"] = pd.to_numeric(
    sales_df["Quantity"],
    errors="coerce"
)

sales_df["UnitPrice"] = pd.to_numeric(
    sales_df["UnitPrice"],
    errors="coerce"
)

sales_df = sales_df.dropna(
    subset=[
        "Quantity",
        "UnitPrice"
    ]
)


# ------------------------------------------------------------
# 4. Calculate transaction amount
# ------------------------------------------------------------

sales_df["TotalAmount"] = (
    sales_df["Quantity"]
    * sales_df["UnitPrice"]
)

print(
    f"Valid transactions: "
    f"{len(sales_df):,}"
)


# ============================================================
# 5. Statistical Outlier Detection - Z-score
# ============================================================

print("\n" + "=" * 60)
print("STATISTICAL OUTLIER DETECTION")
print("=" * 60)

# Calculate mean and standard deviation
# of transaction revenue.

mean_amount = (
    sales_df["TotalAmount"]
    .mean()
)

std_amount = (
    sales_df["TotalAmount"]
    .std()
)

# Calculate Z-score.
#
# Z-score tells us how many standard deviations
# a transaction is away from the average.

sales_df["z_score"] = (
    sales_df["TotalAmount"]
    - mean_amount
) / std_amount


# Flag transactions beyond 3 standard deviations.

sales_df["statistical_anomaly"] = (
    sales_df["z_score"].abs() > 3
)


statistical_anomalies = sales_df[
    sales_df["statistical_anomaly"]
].copy()


print(
    f"Statistical anomalies found: "
    f"{len(statistical_anomalies):,}"
)


# ------------------------------------------------------------
# 6. Isolation Forest
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("ISOLATION FOREST DETECTION")
print("=" * 60)

# Isolation Forest can examine multiple features
# at the same time.

feature_cols = [
    "Quantity",
    "UnitPrice",
    "TotalAmount"
]

X = sales_df[
    feature_cols
]


# contamination=0.02 means we expect roughly
# 2% of transactions to be unusual.

iso_model = IsolationForest(
    contamination=0.02,
    random_state=42
)


sales_df["isolation_flag"] = (
    iso_model.fit_predict(X)
)


# Isolation Forest:
#
# -1 = anomaly
#  1 = normal

isolation_anomalies = sales_df[
    sales_df["isolation_flag"] == -1
].copy()


print(
    f"Isolation Forest anomalies found: "
    f"{len(isolation_anomalies):,}"
)


# ============================================================
# 7. Generate anomaly alerts
# ============================================================

print("\n" + "=" * 60)
print("GENERATING ANOMALY ALERTS")
print("=" * 60)


def generate_alert(row):
    """
    Convert an anomalous transaction into
    a business-friendly alert.
    """

    # Very large transactions are treated
    # as high severity.

    if row["TotalAmount"] > (
        mean_amount * 5
    ):

        severity = "High"

    else:

        severity = "Medium"


    return {
        "InvoiceNo": row["InvoiceNo"],
        "StockCode": row["StockCode"],
        "Quantity": row["Quantity"],
        "UnitPrice": row["UnitPrice"],
        "TotalAmount": row["TotalAmount"],
        "ZScore": row["z_score"],
        "Severity": severity,
        "AlertType": "Unusual Sales Activity",
        "Message": (
            f"Invoice {row['InvoiceNo']} flagged: "
            f"quantity={row['Quantity']}, "
            f"amount=Rs {row['TotalAmount']:.2f}"
        )
    }


# Use Isolation Forest anomalies for the
# final alert list.

alerts = []

for _, row in isolation_anomalies.iterrows():

    alerts.append(
        generate_alert(row)
    )


alerts_df = pd.DataFrame(
    alerts
)


# ============================================================
# 8. Display sample alerts
# ============================================================

print("\nSample Anomaly Alerts")
print("-" * 60)

if alerts_df.empty:

    print(
        "No anomaly alerts generated."
    )

else:

    print(
        alerts_df
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# 9. Save statistical anomalies
# ============================================================

statistical_file = (
    OUTPUT_DIR
    / "statistical_anomalies.csv"
)

statistical_anomalies.to_csv(
    statistical_file,
    index=False
)


# ============================================================
# 10. Save Isolation Forest anomalies
# ============================================================

isolation_file = (
    OUTPUT_DIR
    / "isolation_forest_anomalies.csv"
)

isolation_anomalies.to_csv(
    isolation_file,
    index=False
)


# ============================================================
# 11. Save final alerts
# ============================================================

alerts_file = (
    OUTPUT_DIR
    / "anomaly_alerts.csv"
)

alerts_df.to_csv(
    alerts_file,
    index=False
)


# ============================================================
# 12. Final status
# ============================================================

print("\n" + "=" * 60)
print("ANOMALY DETECTION COMPLETED")
print("=" * 60)

print(
    f"Statistical anomalies saved to:\n"
    f"{statistical_file}"
)

print(
    f"\nIsolation Forest anomalies saved to:\n"
    f"{isolation_file}"
)

print(
    f"\nAnomaly alerts saved to:\n"
    f"{alerts_file}"
)