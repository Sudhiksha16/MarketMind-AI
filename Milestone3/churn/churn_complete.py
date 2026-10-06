# ============================================================
# MarketMind AI - Milestone 3
# Day 7-8: Churn Prediction Complete
# ============================================================

import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

from xgboost import XGBClassifier


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

FEATURE_FILE = (
    PROJECT_ROOT
    / "Milestone3"
    / "churn"
    / "processed"
    / "customer_churn_features.csv"
)

# Milestone 2 customer-level segmentation file
SEGMENT_FILE = (
    PROJECT_ROOT
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "customer_segments_final.csv"
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
# 2. Load churn features
# ------------------------------------------------------------

print("=" * 60)
print("LOADING CUSTOMER CHURN FEATURES")
print("=" * 60)

churn_features = pd.read_csv(
    FEATURE_FILE
)

print(
    f"Customers available: "
    f"{len(churn_features):,}"
)


# ------------------------------------------------------------
# 3. Prepare features and target
# ------------------------------------------------------------

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
# 4. Train/test split
# ------------------------------------------------------------

# stratify=y keeps the churn proportion similar
# in both training and testing data.

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


# ============================================================
# 5. Logistic Regression
# ============================================================

print("\n" + "=" * 60)
print("TRAINING LOGISTIC REGRESSION")
print("=" * 60)

# Logistic Regression benefits from scaled features.

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)

log_model = LogisticRegression(
    random_state=42
)

log_model.fit(
    X_train_scaled,
    y_train
)

log_predictions = (
    log_model.predict(
        X_test_scaled
    )
)


# ============================================================
# 6. Random Forest
# ============================================================

print("\n" + "=" * 60)
print("TRAINING RANDOM FOREST")
print("=" * 60)

# Tree-based models do not require feature scaling.

rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

rf_model.fit(
    X_train,
    y_train
)

rf_predictions = (
    rf_model.predict(
        X_test
    )
)


# ============================================================
# 7. XGBoost
# ============================================================

print("\n" + "=" * 60)
print("TRAINING XGBOOST")
print("=" * 60)

xgb_model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss"
)

xgb_model.fit(
    X_train,
    y_train
)

xgb_predictions = (
    xgb_model.predict(
        X_test
    )
)


# ============================================================
# 8. Evaluate models
# ============================================================

def evaluate_model(
    name,
    actual,
    predicted
):
    """
    Calculate Precision, Recall and F1-score.

    Precision:
    Of the customers predicted as churned,
    how many actually churned?

    Recall:
    Of the customers who actually churned,
    how many did the model catch?

    F1:
    Balance between Precision and Recall.
    """

    precision = precision_score(
        actual,
        predicted,
        zero_division=0
    )

    recall = recall_score(
        actual,
        predicted,
        zero_division=0
    )

    f1 = f1_score(
        actual,
        predicted,
        zero_division=0
    )

    return {
        "Model": name,
        "Precision": round(
            precision, 4
        ),
        "Recall": round(
            recall, 4
        ),
        "F1_Score": round(
            f1, 4
        )
    }


results = []

results.append(
    evaluate_model(
        "Logistic Regression",
        y_test,
        log_predictions
    )
)

results.append(
    evaluate_model(
        "Random Forest",
        y_test,
        rf_predictions
    )
)

results.append(
    evaluate_model(
        "XGBoost",
        y_test,
        xgb_predictions
    )
)

metrics_df = pd.DataFrame(
    results
)


# ------------------------------------------------------------
# 9. Display comparison
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CHURN MODEL COMPARISON")
print("=" * 60)

print(
    metrics_df.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 10. Select best model using F1
# ------------------------------------------------------------

best_model_name = (
    metrics_df
    .sort_values(
        "F1_Score",
        ascending=False
    )
    .iloc[0]["Model"]
)

print(
    f"\nBest model based on F1-score: "
    f"{best_model_name}"
)


# ------------------------------------------------------------
# 11. Generate churn probabilities
# ------------------------------------------------------------

# We use the model with the highest F1-score.
#
# predict_proba(... )[:, 1]
# gives the probability of class 1 = churned.

if best_model_name == "Logistic Regression":

    best_model = log_model

    churn_probabilities = (
        best_model
        .predict_proba(
            X_test_scaled
        )[:, 1]
    )

elif best_model_name == "Random Forest":

    best_model = rf_model

    churn_probabilities = (
        best_model
        .predict_proba(
            X_test
        )[:, 1]
    )

else:

    best_model = xgb_model

    churn_probabilities = (
        best_model
        .predict_proba(
            X_test
        )[:, 1]
    )


# ------------------------------------------------------------
# 12. Create prediction results
# ------------------------------------------------------------

churn_results = X_test.copy()

churn_results["actual_churn"] = (
    y_test.values
)

churn_results["churn_probability"] = (
    churn_probabilities.round(4)
)


# ------------------------------------------------------------
# 13. Create retention risk categories
# ------------------------------------------------------------

def categorize_risk(probability):
    """
    Convert churn probability into a
    business-friendly risk category.

    >= 0.70 -> High Risk
    >= 0.40 -> Medium Risk
    < 0.40  -> Low Risk
    """

    if probability >= 0.70:
        return "High Risk"

    elif probability >= 0.40:
        return "Medium Risk"

    else:
        return "Low Risk"


churn_results["retention_risk"] = (
    churn_results[
        "churn_probability"
    ]
    .apply(categorize_risk)
)


# ------------------------------------------------------------
# 14. Preserve CustomerID
# ------------------------------------------------------------

# X_test retains the original DataFrame index,
# so use those indices to recover the corresponding
# customer IDs from the original churn feature dataset.

churn_results["CustomerID"] = (
    churn_features
    .loc[
        X_test.index,
        "CustomerID"
    ]
    .values
)


# ------------------------------------------------------------
# 15. Reorder columns
# ------------------------------------------------------------

churn_results = churn_results[
    [
        "CustomerID",
        "order_frequency",
        "purchase_inactivity_days",
        "avg_order_value",
        "actual_churn",
        "churn_probability",
        "retention_risk"
    ]
]


# ============================================================
# 16. Connect churn results to Milestone 2 segments
# ============================================================

print("\n" + "=" * 60)
print("CONNECTING CHURN RESULTS TO CUSTOMER SEGMENTS")
print("=" * 60)

if SEGMENT_FILE.exists():

    segment_df = pd.read_csv(
        SEGMENT_FILE
    )

    # Make sure CustomerID has the same data type
    # in both datasets.
    churn_results["CustomerID"] = (
    pd.to_numeric(
        churn_results["CustomerID"],
        errors="coerce"
    )
    .astype("Int64")
    .astype(str)
)

    segment_df["CustomerID"] = (
    pd.to_numeric(
        segment_df["CustomerID"],
        errors="coerce"
    )
    .astype("Int64")
    .astype(str)
)

    # Find the segment column automatically.
    possible_segment_columns = [
        "customer_segment",
        "segment",
        "CustomerSegment"
    ]

    segment_column = None

    for column in possible_segment_columns:

        if column in segment_df.columns:

            segment_column = column
            break

    if segment_column:

        segment_lookup = segment_df[
            [
                "CustomerID",
                segment_column
            ]
        ].drop_duplicates(
            subset=["CustomerID"]
        )

        segment_lookup = (
            segment_lookup.rename(
                columns={
                    segment_column:
                    "customer_segment"
                }
            )
        )

        churn_results = churn_results.merge(
            segment_lookup,
            on="CustomerID",
            how="left"
        )

        print(
            "Milestone 2 customer segments "
            "successfully connected."
        )

    else:

        print(
            "Segment column was not found."
        )

else:

    print(
        "Milestone 2 segment file was not found."
    )


# ============================================================
# 17. Display risk distribution
# ============================================================

print("\nRetention Risk Distribution")
print("-" * 60)

print(
    churn_results[
        "retention_risk"
    ]
    .value_counts()
)


# ============================================================
# 18. Display sample results
# ============================================================

print("\nSample Churn Predictions")
print("-" * 60)

display_columns = [
    "CustomerID",
    "churn_probability",
    "retention_risk"
]

if "customer_segment" in churn_results.columns:

    display_columns.append(
        "customer_segment"
    )

print(
    churn_results[
        display_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 19. Save model comparison
# ============================================================

metrics_file = (
    OUTPUT_DIR
    / "churn_model_comparison.csv"
)

metrics_df.to_csv(
    metrics_file,
    index=False
)


# ============================================================
# 20. Save final churn predictions
# ============================================================

results_file = (
    OUTPUT_DIR
    / "customer_churn_predictions.csv"
)

churn_results.to_csv(
    results_file,
    index=False
)


# ============================================================
# 21. Final status
# ============================================================

print("\n" + "=" * 60)
print("CHURN PREDICTION COMPLETE")
print("=" * 60)

print(
    f"Model comparison saved to:\n"
    f"{metrics_file}"
)

print(
    f"\nCustomer churn predictions saved to:\n"
    f"{results_file}"
)

print(
    f"\nSelected model: "
    f"{best_model_name}"
)