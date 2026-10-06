# ============================================================
# MarketMind AI - Milestone 3
# Day 3-4: Association Rule Recommendations
# ============================================================

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RULES_FILE = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
    / "association_rules.csv"
)

INTERACTION_FILE = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
    / "customer_product_interactions.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Load association rules
# ------------------------------------------------------------

print("=" * 60)
print("LOADING ASSOCIATION RULES")
print("=" * 60)

rules = pd.read_csv(
    RULES_FILE
)

print(
    f"Association rules available: {len(rules):,}"
)


# ------------------------------------------------------------
# 3. Load customer purchase history
# ------------------------------------------------------------

interaction_df = pd.read_csv(
    INTERACTION_FILE,
    encoding="latin1"
)

print(
    f"Customers available: "
    f"{interaction_df['CustomerID'].nunique():,}"
)


# ------------------------------------------------------------
# 4. Convert rule product text back into product IDs
# ------------------------------------------------------------

def split_products(product_text):
    """
    Convert a product string such as:

        21094, 21086

    into a list:

        ['21094', '21086']
    """

    return [
        product.strip()
        for product in str(product_text).split(",")
    ]


rules["antecedent_products"] = (
    rules["antecedents"]
    .apply(split_products)
)

rules["consequent_products"] = (
    rules["consequents"]
    .apply(split_products)
)


# ------------------------------------------------------------
# 5. Create a recommendation function
# ------------------------------------------------------------

def recommend_from_rules(
    customer_id,
    number_of_recommendations=5
):
    """
    Generate recommendations using association rules.

    The system:
    1. Finds products already purchased by the customer.
    2. Finds rules where those products appear
       in the antecedent.
    3. Recommends the associated consequent products.
    4. Removes products the customer already purchased.
    5. Ranks recommendations using confidence and lift.
    """

    customer_id = str(customer_id)

    customer_data = interaction_df[
        interaction_df["CustomerID"].astype(str)
        == customer_id
    ]

    if customer_data.empty:

        print(
            f"Customer {customer_id} was not found."
        )

        return pd.DataFrame()

    # Products already purchased
    purchased_products = set(
        customer_data["StockCode"]
        .astype(str)
    )

    recommendation_scores = {}

    for _, rule in rules.iterrows():

        antecedents = set(
            rule["antecedent_products"]
        )

        consequents = (
            rule["consequent_products"]
        )

        # Apply the rule only when the customer
        # has purchased the antecedent product.
        if antecedents.issubset(
            purchased_products
        ):

            for product in consequents:

                # Never recommend a product the
                # customer already purchased.
                if product in purchased_products:
                    continue

                # Combine confidence and lift
                # into a ranking score.
                score = (
                    rule["confidence"]
                    * rule["lift"]
                )

                recommendation_scores[product] = (
                    recommendation_scores.get(
                        product, 0
                    )
                    + score
                )

    # No recommendations
    if not recommendation_scores:
        return pd.DataFrame()

    recommendations = pd.DataFrame(
        recommendation_scores.items(),
        columns=[
            "StockCode",
            "RecommendationScore"
        ]
    )

    recommendations = (
        recommendations
        .sort_values(
            "RecommendationScore",
            ascending=False
        )
        .head(number_of_recommendations)
    )

    return recommendations


# ------------------------------------------------------------
# 6. Test with a real customer
# ------------------------------------------------------------

test_customer = (
    interaction_df["CustomerID"]
    .astype(str)
    .iloc[0]
)

print("\n" + "=" * 60)
print("GENERATING RULE-BASED RECOMMENDATIONS")
print("=" * 60)

print(
    f"Test customer: {test_customer}"
)


recommendations = recommend_from_rules(
    test_customer,
    number_of_recommendations=5
)


# ------------------------------------------------------------
# 7. Add product descriptions
# ------------------------------------------------------------

if not recommendations.empty:

    product_names = (
        interaction_df[
            [
                "StockCode",
                "Description"
            ]
        ]
        .drop_duplicates(
            subset=["StockCode"]
        )
    )

    product_names["StockCode"] = (
        product_names["StockCode"]
        .astype(str)
    )

    recommendations = recommendations.merge(
        product_names,
        on="StockCode",
        how="left"
    )


# ------------------------------------------------------------
# 8. Display results
# ------------------------------------------------------------

print("\nRecommended Products")
print("-" * 60)

if recommendations.empty:

    print(
        "No rule-based recommendations "
        "could be generated."
    )

else:

    print(
        recommendations[
            [
                "StockCode",
                "Description",
                "RecommendationScore"
            ]
        ].to_string(index=False)
    )


# ------------------------------------------------------------
# 9. Save results
# ------------------------------------------------------------

output_file = (
    OUTPUT_DIR
    / "rule_based_recommendations.csv"
)

recommendations.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------------------
# 10. Final status
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("RULE-BASED RECOMMENDATION COMPLETED")
print("=" * 60)

print(
    f"Results saved to:\n{output_file}"
)