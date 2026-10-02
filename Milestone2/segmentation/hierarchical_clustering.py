# Import pandas for reading and processing the customer data.
import pandas as pd

# Import Path for creating reliable file paths.
from pathlib import Path

# StandardScaler puts all features on a comparable scale.
from sklearn.preprocessing import StandardScaler

# AgglomerativeClustering performs hierarchical clustering.
from sklearn.cluster import AgglomerativeClustering


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD THE CUSTOMER FEATURES
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
# 3. SELECT THE SAME FEATURES USED BY K-MEANS
# ---------------------------------------------------------

feature_cols = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days"
]

X = customer_features[feature_cols]


# ---------------------------------------------------------
# 4. SCALE THE FEATURES
# ---------------------------------------------------------

# Hierarchical clustering also uses distances between
# customers, so the features must be scaled.

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print("Features scaled successfully.")


# ---------------------------------------------------------
# 5. CREATE THE HIERARCHICAL CLUSTERING MODEL
# ---------------------------------------------------------

# We use 4 clusters so that we can compare the result
# with our K-Means experiment.

hierarchical_model = AgglomerativeClustering(
    n_clusters=4,
    linkage="ward"
)


# ---------------------------------------------------------
# 6. CREATE HIERARCHICAL CLUSTERS
# ---------------------------------------------------------

customer_features["hierarchical_cluster"] = (
    hierarchical_model.fit_predict(X_scaled)
)


# ---------------------------------------------------------
# 7. DISPLAY SAMPLE RESULTS
# ---------------------------------------------------------

print("\nSample hierarchical clustering results:")

print(
    customer_features[
        [
            "CustomerID",
            "purchase_frequency",
            "purchase_value",
            "customer_activity_days",
            "hierarchical_cluster"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 8. SUMMARIZE EACH CLUSTER
# ---------------------------------------------------------

cluster_summary = (
    customer_features
    .groupby("hierarchical_cluster")[feature_cols]
    .mean()
    .round(2)
)

print("\nHierarchical cluster summary:")

print(cluster_summary)


# ---------------------------------------------------------
# 9. COUNT CUSTOMERS IN EACH CLUSTER
# ---------------------------------------------------------

cluster_counts = (
    customer_features["hierarchical_cluster"]
    .value_counts()
    .sort_index()
)

print("\nNumber of customers in each hierarchical cluster:")

print(cluster_counts)


# ---------------------------------------------------------
# 10. SAVE THE RESULTS
# ---------------------------------------------------------

output_file = (
    BASE_DIR
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "customer_segments_hierarchical.csv"
)

customer_features.to_csv(
    output_file,
    index=False
)

print("\nHierarchical clustering completed successfully!")

print(f"Saved to: {output_file}")