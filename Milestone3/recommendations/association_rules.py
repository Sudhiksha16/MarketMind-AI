# ============================================================
# MarketMind AI - Milestone 3
# Day 3-4: Association Rule Mining
# ============================================================

import pandas as pd
from pathlib import Path

from mlxtend.frequent_patterns import (
    apriori,
    association_rules
)


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Milestone 1 cleaned sales data
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
    / "recommendations"
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
    f"Sales records loaded: {len(sales_df):,}"
)

print(
    f"Unique orders: "
    f"{sales_df['InvoiceNo'].nunique():,}"
)

print(
    f"Unique products: "
    f"{sales_df['StockCode'].nunique():,}"
)


# ------------------------------------------------------------
# 3. Keep required columns
# ------------------------------------------------------------

sales_df = sales_df[
    [
        "InvoiceNo",
        "StockCode",
        "Quantity"
    ]
].copy()


# ------------------------------------------------------------
# 4. Remove invalid quantities
# ------------------------------------------------------------

# Association Rule Mining looks at whether a product
# appears in an order.
#
# Quantity must therefore be positive.

sales_df = sales_df[
    sales_df["Quantity"] > 0
]


# ------------------------------------------------------------
# 5. Build order-product basket
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("BUILDING ORDER-PRODUCT BASKET")
print("=" * 60)

# Each row = one invoice/order
# Each column = one product
# Value = total quantity purchased in that order

basket = sales_df.pivot_table(
    index="InvoiceNo",
    columns="StockCode",
    values="Quantity",
    aggfunc="sum",
    fill_value=0
)

print(
    f"Orders in basket: "
    f"{basket.shape[0]:,}"
)

print(
    f"Products in basket: "
    f"{basket.shape[1]:,}"
)


# ------------------------------------------------------------
# 6. Convert quantities into 0/1
# ------------------------------------------------------------

# Association Rule Mining cares about whether
# a product was present in the order.
#
# 1 = purchased
# 0 = not purchased

basket = (
    basket > 0
).astype(bool)

print("\nBasket created successfully.")


# ------------------------------------------------------------
# 7. Find frequent itemsets
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FINDING FREQUENT PRODUCT COMBINATIONS")
print("=" * 60)

# The mentor material uses min_support = 0.02.
#
# This means the product combination must occur
# in at least 2% of all orders.
#
# max_len=2 keeps the first implementation focused
# on product pairs and prevents unnecessary memory usage.

frequent_itemsets = apriori(
    basket,
    min_support=0.02,
    use_colnames=True,
    max_len=2,
    low_memory=True
)

print(
    f"Frequent itemsets found: "
    f"{len(frequent_itemsets):,}"
)


# ------------------------------------------------------------
# 8. Generate association rules
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("GENERATING ASSOCIATION RULES")
print("=" * 60)

if frequent_itemsets.empty:

    rules = pd.DataFrame()

else:

    # We use lift as the rule-selection metric,
    # following the mentor's Day 3-4 example.
    #
    # Lift > 1 means the products are associated
    # more strongly than random chance.

    rules = association_rules(
        frequent_itemsets,
        metric="lift",
        min_threshold=1.0
    )


# ------------------------------------------------------------
# 9. Select useful columns
# ------------------------------------------------------------

if rules.empty:

    print(
        "No association rules were generated."
    )

else:

    rules = rules[
        [
            "antecedents",
            "consequents",
            "support",
            "confidence",
            "lift"
        ]
    ].copy()

    rules = rules.sort_values(
        by="lift",
        ascending=False
    )

    print(
        f"Association rules generated: "
        f"{len(rules):,}"
    )


# ------------------------------------------------------------
# 10. Convert product sets to readable text
# ------------------------------------------------------------

def convert_products(product_set):
    """
    Convert a frozenset of product IDs into
    a comma-separated string.
    """

    return ", ".join(
        sorted(
            str(product)
            for product in product_set
        )
    )


if not rules.empty:

    rules["antecedents"] = (
        rules["antecedents"]
        .apply(convert_products)
    )

    rules["consequents"] = (
        rules["consequents"]
        .apply(convert_products)
    )


# ------------------------------------------------------------
# 11. Display top rules
# ------------------------------------------------------------

print("\nTop Association Rules")
print("-" * 70)

if rules.empty:

    print(
        "No useful association rules found."
    )

else:

    print(
        rules[
            [
                "antecedents",
                "consequents",
                "support",
                "confidence",
                "lift"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


# ------------------------------------------------------------
# 12. Save frequent itemsets
# ------------------------------------------------------------

itemset_file = (
    OUTPUT_DIR
    / "frequent_itemsets_order_based.csv"
)

frequent_itemsets.to_csv(
    itemset_file,
    index=False
)


# ------------------------------------------------------------
# 13. Save association rules
# ------------------------------------------------------------

rules_file = (
    OUTPUT_DIR
    / "association_rules_order_based.csv"
)

if not rules.empty:

    rules.to_csv(
        rules_file,
        index=False
    )


# ------------------------------------------------------------
# 14. Final status
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("ORDER-BASED ASSOCIATION RULE MINING COMPLETED")
print("=" * 60)

print(
    f"Frequent itemsets saved to:\n"
    f"{itemset_file}"
)

if not rules.empty:

    print(
        f"\nAssociation rules saved to:\n"
        f"{rules_file}"
    )