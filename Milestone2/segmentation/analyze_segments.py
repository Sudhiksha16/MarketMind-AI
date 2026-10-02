# Import pandas for reading and analyzing the clustering results.
import pandas as pd

# Import Path so we can create reliable file paths.
from pathlib import Path


# ---------------------------------------------------------
# 1. FIND THE PROJECT FOLDER
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------
# 2. LOAD HIERARCHICAL CLUSTERING RESULTS
# ---------------------------------------------------------

input_file = (
    BASE_DIR
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "customer_segments_hierarchical.csv"
)

print("Loading hierarchical clustering results...")

customer_data = pd.read_csv(input_file)

print(f"Customers loaded: {len(customer_data)}")


# ---------------------------------------------------------
# 3. ASSIGN BUSINESS-FRIENDLY SEGMENT NAMES
# ---------------------------------------------------------

# These names are based on the average behavior observed
# in each hierarchical cluster.
#
# Cluster 0:
# Low frequency + low spending + high inactivity
# → At-Risk / Fading Customers
#
# Cluster 1:
# Very high frequency + extremely high spending
# → VIP Customers
#
# Cluster 2:
# High frequency + high spending + recent activity
# → Loyal / High-Value Customers
#
# Cluster 3:
# Moderate frequency + moderate spending
# → Regular Customers

segment_names = {
    0: "VIP Customers",
    1: "Regular Customers",
    2: "At-Risk / Fading Customers",
    3: "Loyal / High-Value Customers"
}


# Apply the names to every customer.
customer_data["customer_segment"] = (
    customer_data["hierarchical_cluster"]
    .map(segment_names)
)


# ---------------------------------------------------------
# 4. CREATE A SEGMENT SUMMARY
# ---------------------------------------------------------

# Calculate the number of customers and their average
# purchasing behavior for each business segment.

segment_summary = (
    customer_data
    .groupby("customer_segment")
    .agg(
        customer_count=("CustomerID", "count"),
        average_purchase_frequency=("purchase_frequency", "mean"),
        average_purchase_value=("purchase_value", "mean"),
        average_activity_days=("customer_activity_days", "mean")
    )
    .round(2)
    .reset_index()
)


# ---------------------------------------------------------
# 5. DISPLAY THE SEGMENT SUMMARY
# ---------------------------------------------------------

print("\nCustomer Segment Summary:")
print(segment_summary.to_string(index=False))


# ---------------------------------------------------------
# 6. DISPLAY SEGMENT COUNTS
# ---------------------------------------------------------

print("\nCustomer count by segment:")

print(
    customer_data["customer_segment"]
    .value_counts()
)


# ---------------------------------------------------------
# 7. SAVE THE NAMED CUSTOMER SEGMENTS
# ---------------------------------------------------------

output_file = (
    BASE_DIR
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "customer_segments_final.csv"
)

customer_data.to_csv(
    output_file,
    index=False
)


# ---------------------------------------------------------
# 8. SAVE THE SEGMENT SUMMARY
# ---------------------------------------------------------

summary_file = (
    BASE_DIR
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "segment_summary.csv"
)

segment_summary.to_csv(
    summary_file,
    index=False
)


# ---------------------------------------------------------
# 9. COMPLETION MESSAGE
# ---------------------------------------------------------

print("\nCustomer segmentation analysis completed successfully!")

print(f"Customer segments saved to: {output_file}")

print(f"Segment summary saved to: {summary_file}")