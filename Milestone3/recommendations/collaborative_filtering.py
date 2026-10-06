# ============================================================
# MarketMind AI - Milestone 3
# Day 1-2: Collaborative Filtering
# ============================================================

import pandas as pd
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

INPUT_FILE = (
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Milestone3"
    / "recommendations"
    / "processed"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Load customer-product matrix
# ------------------------------------------------------------

print("=" * 60)
print("LOADING CUSTOMER-PRODUCT MATRIX")
print("=" * 60)

interaction_matrix = pd.read_csv(
    INPUT_FILE,
    index_col=0
)
interaction_matrix.index = interaction_matrix.index.astype(str)

print(
    f"Customers available: {interaction_matrix.shape[0]:,}"
)

print(
    f"Products available: {interaction_matrix.shape[1]:,}"
)


# ------------------------------------------------------------
# 3. Calculate customer similarity
# ------------------------------------------------------------

# Cosine similarity compares customers based on
# their purchase patterns.
#
# Similarity:
#     1.0 -> very similar
#     0.0 -> not similar
#
# The result is a matrix where:
#
#             Customer 1  Customer 2  Customer 3
# Customer 1      1.0        0.7         0.1
# Customer 2      0.7        1.0         0.2
# Customer 3      0.1        0.2         1.0

print("\nCalculating customer similarities...")

customer_similarity = cosine_similarity(
    interaction_matrix
)

customer_similarity_df = pd.DataFrame(
    customer_similarity,
    index=interaction_matrix.index,
    columns=interaction_matrix.index
)


# ------------------------------------------------------------
# 4. Recommendation function
# ------------------------------------------------------------

def recommend_products(customer_id, number_of_recommendations=5):
    """
    Generate product recommendations for one customer.

    Steps:
    1. Find customers similar to the selected customer.
    2. Look at products purchased by those customers.
    3. Remove products already purchased by the target customer.
    4. Rank remaining products.
    5. Return the top recommendations.
    """

    customer_id = str(customer_id)

    # Make sure the requested customer exists
    if customer_id not in interaction_matrix.index:
        print(
            f"Customer {customer_id} was not found."
        )
        return pd.DataFrame()

    # --------------------------------------------------------
    # Find similarity scores for the selected customer
    # --------------------------------------------------------

    similarity_scores = customer_similarity_df.loc[
        customer_id
    ]

    # Sort from most similar to least similar
    similarity_scores = similarity_scores.sort_values(
        ascending=False
    )

    # Remove the customer themselves
    similarity_scores = similarity_scores[
        similarity_scores.index != customer_id
    ]

    # --------------------------------------------------------
    # Select the most similar customers
    # --------------------------------------------------------

    similar_customers = similarity_scores.head(10)

    print("\nMost similar customers:")
    print(similar_customers.to_string())


    # --------------------------------------------------------
    # Get products already purchased by target customer
    # --------------------------------------------------------

    customer_purchases = interaction_matrix.loc[
        customer_id
    ]

    purchased_products = set(
        customer_purchases[
            customer_purchases > 0
        ].index
    )


    # --------------------------------------------------------
    # Calculate recommendation scores
    # --------------------------------------------------------

    recommendation_scores = {}

    for similar_customer, similarity_score in (
        similar_customers.items()
    ):

        # Get products purchased by similar customer
        similar_customer_products = (
            interaction_matrix.loc[
                similar_customer
            ]
        )

        purchased_by_similar_customer = (
            similar_customer_products[
                similar_customer_products > 0
            ]
        )

        # Give more importance to products purchased by
        # highly similar customers.
        for product, quantity in (
            purchased_by_similar_customer.items()
        ):

            # Don't recommend something the customer
            # already purchased.
            if product in purchased_products:
                continue

            score = (
                similarity_score * quantity
            )

            recommendation_scores[product] = (
                recommendation_scores.get(product, 0)
                + score
            )


    # --------------------------------------------------------
    # Convert scores into a DataFrame
    # --------------------------------------------------------

    recommendations = pd.DataFrame(
        recommendation_scores.items(),
        columns=[
            "StockCode",
            "RecommendationScore"
        ]
    )

    # --------------------------------------------------------
    # Sort recommendations
    # --------------------------------------------------------

    recommendations = recommendations.sort_values(
        by="RecommendationScore",
        ascending=False
    )

    # Return top N recommendations
    return recommendations.head(
        number_of_recommendations
    )


# ------------------------------------------------------------
# 5. Choose a real customer
# ------------------------------------------------------------

# We use the first customer available in our dataset
# so that the script works with the actual data.

test_customer = interaction_matrix.index[0]

print("\n" + "=" * 60)
print("GENERATING RECOMMENDATIONS")
print("=" * 60)

print(f"Test customer: {test_customer}")


# ------------------------------------------------------------
# 6. Generate recommendations
# ------------------------------------------------------------

recommendations = recommend_products(
    test_customer,
    number_of_recommendations=5
)


# ------------------------------------------------------------
# 7. Add product descriptions
# ------------------------------------------------------------

if not recommendations.empty:

    interaction_data = pd.read_csv(
        INTERACTION_FILE,
        encoding="latin1"
    )

    product_names = (
        interaction_data[
            [
                "StockCode",
                "Description"
            ]
        ]
        .drop_duplicates(
            subset=["StockCode"]
        )
    )

    recommendations = recommendations.merge(
        product_names,
        on="StockCode",
        how="left"
    )


# ------------------------------------------------------------
# 8. Display final recommendations
# ------------------------------------------------------------

print("\nRecommended Products:")
print("-" * 60)

if recommendations.empty:

    print(
        "No recommendations could be generated."
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
# 9. Save recommendations
# ------------------------------------------------------------

output_file = (
    OUTPUT_DIR
    / "sample_recommendations.csv"
)

recommendations.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------------------
# 10. Final status
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("COLLABORATIVE FILTERING COMPLETED")
print("=" * 60)

print(
    f"Recommendations saved to:\n{output_file}"
)

# ============================================================
# 11. Validate Recommendations
# ============================================================

print("\n" + "=" * 60)
print("VALIDATING RECOMMENDATIONS")
print("=" * 60)

# Get all products already purchased by the test customer
customer_purchased_products = set(
    interaction_matrix.loc[test_customer][
        interaction_matrix.loc[test_customer] > 0
    ].index
)

print(
    f"Products already purchased by customer: "
    f"{len(customer_purchased_products)}"
)

# Check whether recommendations were generated
if recommendations.empty:

    print(
        "\nWARNING: No recommendations were generated."
    )

else:

    # Get the products recommended by the model
    recommended_products = set(
        recommendations["StockCode"]
    )

    # Check whether any recommended product
    # was already purchased by the customer
    already_purchased = (
        recommended_products
        & customer_purchased_products
    )

    print(
        f"Products recommended: "
        f"{len(recommended_products)}"
    )

    print(
        f"Recommended products already purchased: "
        f"{len(already_purchased)}"
    )

    if already_purchased:

        print(
            "\nWARNING: Some recommended products "
            "were already purchased:"
        )

        print(already_purchased)

    else:

        print(
            "\nSUCCESS: All recommended products are "
            "new to this customer."
        )

# ============================================================
# 12. Test Recommendations for Multiple Customers
# ============================================================

print("\n" + "=" * 60)
print("TESTING MULTIPLE CUSTOMERS")
print("=" * 60)

# Select the first 5 customers from our real dataset.
# Testing multiple customers helps us verify that the
# recommendation engine works beyond a single example.
test_customers = interaction_matrix.index[:5]

all_test_results = []

for customer_id in test_customers:

    print("\n" + "-" * 60)
    print(f"Testing customer: {customer_id}")
    print("-" * 60)

    customer_recommendations = recommend_products(
        customer_id,
        number_of_recommendations=5
    )

    # Continue only if recommendations were generated
    if not customer_recommendations.empty:

        # Add the customer ID so we know who received
        # each recommendation.
        customer_recommendations = (
            customer_recommendations.copy()
        )

        customer_recommendations["CustomerID"] = (
            customer_id
        )

        all_test_results.append(
            customer_recommendations
        )

        print("\nRecommended products:")

        print(
            customer_recommendations[
                [
                    "StockCode",
                    "RecommendationScore"
                ]
            ].to_string(index=False)
        )

    else:

        print(
            "No recommendations generated "
            "for this customer."
        )


# ------------------------------------------------------------
# Combine all customer recommendations
# ------------------------------------------------------------

if all_test_results:

    multiple_customer_results = pd.concat(
        all_test_results,
        ignore_index=True
    )

    # Put CustomerID first
    multiple_customer_results = (
        multiple_customer_results[
            [
                "CustomerID",
                "StockCode",
                "RecommendationScore"
            ]
        ]
    )

    # Save the results
    multiple_customer_file = (
        OUTPUT_DIR
        / "multiple_customer_recommendations.csv"
    )

    multiple_customer_results.to_csv(
        multiple_customer_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("MULTIPLE-CUSTOMER TEST COMPLETED")
    print("=" * 60)

    print(
        f"Customers tested: "
        f"{len(test_customers)}"
    )

    print(
        f"Recommendation rows generated: "
        f"{len(multiple_customer_results)}"
    )

    print(
        f"\nResults saved to:\n"
        f"{multiple_customer_file}"
    )

else:

    print(
        "\nNo recommendations were generated "
        "for the tested customers."
    )