# ============================================================
# MarketMind AI - Milestone 3
# Day 3-4: Combined Recommendation Engine
# ============================================================

import pandas as pd
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

MATRIX_FILE = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
    / "customer_product_matrix.csv"
)

INTERACTION_FILE = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
    / "customer_product_interactions.csv"
)

RULES_FILE = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
    / "association_rules_order_based.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# 2. Load customer-product matrix
# ------------------------------------------------------------

print("=" * 60)
print("LOADING RECOMMENDATION DATA")
print("=" * 60)

interaction_matrix = pd.read_csv(
    MATRIX_FILE,
    index_col=0
)

# Keep customer IDs consistent
interaction_matrix.index = (
    interaction_matrix.index.astype(str)
)

print(
    f"Customers available: "
    f"{len(interaction_matrix):,}"
)

print(
    f"Products available: "
    f"{interaction_matrix.shape[1]:,}"
)


# ------------------------------------------------------------
# 3. Load purchase history
# ------------------------------------------------------------

interaction_df = pd.read_csv(
    INTERACTION_FILE,
    encoding="latin1"
)

interaction_df["CustomerID"] = (
    interaction_df["CustomerID"]
    .astype(str)
)

interaction_df["StockCode"] = (
    interaction_df["StockCode"]
    .astype(str)
)


# ------------------------------------------------------------
# 4. Load association rules
# ------------------------------------------------------------

rules = pd.read_csv(
    RULES_FILE
)

print(
    f"Association rules available: "
    f"{len(rules):,}"
)


# ------------------------------------------------------------
# 5. Calculate customer similarity
# ------------------------------------------------------------

print("\nCalculating customer similarity...")

similarity_matrix = cosine_similarity(
    interaction_matrix
)

customer_similarity = pd.DataFrame(
    similarity_matrix,
    index=interaction_matrix.index,
    columns=interaction_matrix.index
)


# ------------------------------------------------------------
# 6. Collaborative Filtering
# ------------------------------------------------------------

def recommend_for_you(
    customer_id,
    number_of_recommendations=5
):
    """
    Personalized recommendations using
    Collaborative Filtering.

    Finds customers with similar purchase
    behaviour and recommends products they
    purchased that the target customer has not.
    """

    customer_id = str(customer_id)

    if customer_id not in interaction_matrix.index:

        return pd.DataFrame()

    # Similarity scores for target customer
    similarity_scores = (
        customer_similarity
        .loc[customer_id]
        .sort_values(
            ascending=False
        )
    )

    # Remove the customer themselves
    similarity_scores = (
        similarity_scores[
            similarity_scores.index != customer_id
        ]
    )

    # Use the top similar customers
    similar_customers = (
        similarity_scores.head(10)
    )

    # Products already purchased
    customer_products = (
        interaction_matrix.loc[
            customer_id
        ]
    )

    purchased_products = set(
        customer_products[
            customer_products > 0
        ].index.astype(str)
    )

    recommendation_scores = {}

    # Look at products bought by similar customers
    for similar_customer, similarity_score in (
        similar_customers.items()
    ):

        similar_products = (
            interaction_matrix.loc[
                similar_customer
            ]
        )

        similar_products = (
            similar_products[
                similar_products > 0
            ]
        )

        for product, quantity in (
            similar_products.items()
        ):

            product = str(product)

            # Don't recommend products already bought
            if product in purchased_products:
                continue

            score = (
                similarity_score
                * quantity
            )

            recommendation_scores[product] = (
                recommendation_scores.get(
                    product,
                    0
                )
                + score
            )

    if not recommendation_scores:

        return pd.DataFrame()

    result = pd.DataFrame(
        recommendation_scores.items(),
        columns=[
            "StockCode",
            "RecommendationScore"
        ]
    )

    result = (
        result
        .sort_values(
            "RecommendationScore",
            ascending=False
        )
        .head(number_of_recommendations)
    )

    return result


# ------------------------------------------------------------
# 7. Association Rule Recommendations
# ------------------------------------------------------------

def recommend_frequently_bought(
    customer_id,
    current_product,
    number_of_recommendations=3
):
    """
    Generate cross-sell recommendations using
    Association Rules.

    Example:

    Customer has Product A

            ↓

    Rule:
    Product A -> Product B

            ↓

    Recommend Product B
    """

    customer_id = str(customer_id)
    current_product = str(current_product)

    # Find products already purchased
    customer_data = interaction_df[
        interaction_df["CustomerID"]
        == customer_id
    ]

    if customer_data.empty:

        return pd.DataFrame()

    purchased_products = set(
        customer_data["StockCode"]
        .astype(str)
    )

    # Find rules where the current product
    # appears in the antecedent.
    matching_rules = rules[
        rules["antecedents"]
        .astype(str)
        .apply(
            lambda value:
            current_product in [
                item.strip()
                for item in value.split(",")
            ]
        )
    ].copy()

    if matching_rules.empty:

        return pd.DataFrame()

    # Sort by strongest association
    matching_rules = (
        matching_rules
        .sort_values(
            "lift",
            ascending=False
        )
    )

    recommendation_rows = []

    for _, rule in matching_rules.iterrows():

        consequent_products = [
            item.strip()
            for item in str(
                rule["consequents"]
            ).split(",")
        ]

        for product in consequent_products:

            # Don't recommend something already bought
            if product in purchased_products:
                continue

            recommendation_rows.append(
                {
                    "StockCode": product,
                    "Support": rule["support"],
                    "Confidence": rule["confidence"],
                    "Lift": rule["lift"]
                }
            )

    if not recommendation_rows:

        return pd.DataFrame()

    result = pd.DataFrame(
        recommendation_rows
    )

    # Remove duplicate products
    result = (
        result
        .drop_duplicates(
            subset=["StockCode"]
        )
        .sort_values(
            "Lift",
            ascending=False
        )
        .head(
            number_of_recommendations
        )
    )

    return result


# ------------------------------------------------------------
# 8. Combined Recommendation Function
# ------------------------------------------------------------

def get_full_recommendations(
    customer_id,
    current_product=None
):
    """
    Combine both recommendation techniques.

    Output:

    recommended_for_you
        -> Collaborative Filtering

    frequently_bought_with
        -> Association Rule Mining
    """

    result = {}

    # --------------------------------------------------------
    # Personalized recommendations
    # --------------------------------------------------------

    personalized = recommend_for_you(
        customer_id,
        number_of_recommendations=5
    )

    result[
        "recommended_for_you"
    ] = personalized[
        "StockCode"
    ].tolist() if not personalized.empty else []


    # --------------------------------------------------------
    # Cross-sell recommendations
    # --------------------------------------------------------

    if current_product:

        cross_sell = recommend_frequently_bought(
            customer_id,
            current_product,
            number_of_recommendations=3
        )

        result[
            "frequently_bought_with"
        ] = cross_sell[
            "StockCode"
        ].tolist() if not cross_sell.empty else []

    else:

        result[
            "frequently_bought_with"
        ] = []


    return result


# ------------------------------------------------------------
# 9. Test the combined engine
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("TESTING COMBINED RECOMMENDATION ENGINE")
print("=" * 60)


# Use a real customer from our dataset
test_customer = (
    interaction_matrix.index[0]
)


# Find products already purchased by this customer
customer_products = (
    interaction_df[
        interaction_df["CustomerID"]
        == test_customer
    ]["StockCode"]
    .astype(str)
    .unique()
)


print(
    f"Test customer: {test_customer}"
)

print(
    f"Products purchased by customer: "
    f"{len(customer_products)}"
)


# ------------------------------------------------------------
# 10. Find a product that has association rules
# ------------------------------------------------------------

current_product = None

for product in customer_products:

    matching_rules = rules[
        rules["antecedents"]
        .astype(str)
        .apply(
            lambda value:
            product in [
                item.strip()
                for item in value.split(",")
            ]
        )
    ]

    if not matching_rules.empty:

        current_product = product
        break


print(
    f"Current product for cross-sell test: "
    f"{current_product}"
)


# ------------------------------------------------------------
# 11. Generate final recommendations
# ------------------------------------------------------------

final_recommendations = get_full_recommendations(
    test_customer,
    current_product
)


# ------------------------------------------------------------
# 12. Display personalized recommendations
# ------------------------------------------------------------

print("\nRecommended For You")
print("-" * 60)

for product in final_recommendations[
    "recommended_for_you"
]:

    print(
        f"- {product}"
    )


# ------------------------------------------------------------
# 13. Display cross-sell recommendations
# ------------------------------------------------------------

print("\nFrequently Bought Together")
print("-" * 60)

for product in final_recommendations[
    "frequently_bought_with"
]:

    print(
        f"- {product}"
    )


# ------------------------------------------------------------
# 14. Save combined output
# ------------------------------------------------------------

output_rows = []

for product in final_recommendations[
    "recommended_for_you"
]:

    output_rows.append(
        {
            "CustomerID": test_customer,
            "RecommendationType":
                "Recommended For You",
            "StockCode": product
        }
    )


for product in final_recommendations[
    "frequently_bought_with"
]:

    output_rows.append(
        {
            "CustomerID": test_customer,
            "RecommendationType":
                "Frequently Bought Together",
            "StockCode": product
        }
    )


combined_output = pd.DataFrame(
    output_rows
)

output_file = (
    OUTPUT_DIR
    / "combined_recommendations.csv"
)

combined_output.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------------------
# 15. Final status
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("COMBINED RECOMMENDATION ENGINE COMPLETED")
print("=" * 60)

print(
    f"Output saved to:\n{output_file}"
)