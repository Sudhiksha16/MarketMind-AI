# Import pandas to read and work with our customer feature data.
import pandas as pd

# Import Path to create reliable file paths.
from pathlib import Path

# StandardScaler puts all features on a comparable scale.
from sklearn.preprocessing import StandardScaler

# KMeans is the clustering algorithm we are going to use.
from sklearn.cluster import KMeans


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

# This file is inside:
# MarketMind AI/Milestone2/segmentation/
#
# parent       -> segmentation
# parent.parent -> Milestone2
# parent.parent.parent -> MarketMind AI

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD CUSTOMER FEATURES
# ---------------------------------------------------------

customer_file = (
    BASE_DIR
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "customer_features.csv"
)

print("Loading customer features...")

customer_features = pd.read_csv(customer_file)

print(f"Customers loaded: {len(customer_features)}")


# ---------------------------------------------------------
# 3. SELECT FEATURES FOR CLUSTERING
# ---------------------------------------------------------

# These are the three features specified in the
# Milestone 2 Day 1-2 guide.
feature_cols = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days"
]

X = customer_features[feature_cols]


# ---------------------------------------------------------
# 4. SCALE THE FEATURES
# ---------------------------------------------------------

# K-Means uses distance to decide which customers are
# similar to each other.
#
# Purchase value can have much larger numbers than
# purchase frequency.
#
# StandardScaler puts all three features onto a
# comparable scale.

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print("\nFeatures scaled successfully.")


# ---------------------------------------------------------
# 5. CREATE THE K-MEANS MODEL
# ---------------------------------------------------------

# The learning material uses K = 4 as the initial
# number of customer groups.

kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)


# ---------------------------------------------------------
# 6. TRAIN K-MEANS AND ASSIGN CLUSTERS
# ---------------------------------------------------------

# fit_predict() learns the customer groups and then
# assigns every customer to one of the four clusters.

customer_features["cluster"] = kmeans.fit_predict(X_scaled)


# ---------------------------------------------------------
# 7. DISPLAY SAMPLE RESULTS
# ---------------------------------------------------------

print("\nSample customer cluster assignments:")

print(
    customer_features[
        [
            "CustomerID",
            "purchase_frequency",
            "purchase_value",
            "customer_activity_days",
            "cluster"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 8. CREATE A CLUSTER SUMMARY
# ---------------------------------------------------------

# Calculate the average behavior of customers
# inside each cluster.

cluster_summary = (
    customer_features
    .groupby("cluster")[feature_cols]
    .mean()
    .round(2)
)

print("\nCluster summary:")
print(cluster_summary)


# ---------------------------------------------------------
# 9. COUNT CUSTOMERS IN EACH CLUSTER
# ---------------------------------------------------------

cluster_counts = (
    customer_features["cluster"]
    .value_counts()
    .sort_index()
)

print("\nNumber of customers in each cluster:")

print(cluster_counts)


# ---------------------------------------------------------
# 10. SAVE THE RESULTS
# ---------------------------------------------------------

output_file = (
    BASE_DIR
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "customer_segments_kmeans.csv"
)

customer_features.to_csv(
    output_file,
    index=False
)

print("\nK-Means clustering completed successfully!")

print(f"Saved to: {output_file}")