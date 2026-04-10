import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"None of these columns found: {candidates}. "
        f"Available: {list(df.columns)}"
    )


def format_transactions(
    df: pd.DataFrame,
    top_n_products: int = 100
) -> tuple[list[list[str]], list[str]]:
    """
    Convert transaction-level data to basket format.
    Limits to top N most popular products to keep
    the basket matrix manageable in memory.

    Returns:
        transactions: list of product lists per invoice
        top_products: list of top product names used
    """
    df = _normalize_columns(df)

    invoice_col     = _pick_column(df, ["invoice","invoiceno","invoice_no","order_id","transaction_id","id","sku","product_id"])
    description_col = _pick_column(df, ["description", "product", "item", "product_name", "product_category", "product_description", "name", "title"])

    # Drop missing
    df = df.dropna(subset=[invoice_col, description_col])

    # Remove returns (invoices starting with C)
    df = df[~df[invoice_col].astype(str).str.startswith("C")]

    # Clean descriptions
    df[description_col] = df[description_col].astype(str).str.strip().str.upper()

    # Keep only top N most popular products
    # This prevents memory explosion with 4000+ unique products
    top_products = (
        df[description_col]
        .value_counts()
        .head(top_n_products)
        .index
        .tolist()
    )
    df_filtered = df[df[description_col].isin(top_products)]

    # Group by invoice → list of products
    transactions = (
        df_filtered
        .groupby(invoice_col)[description_col]
        .apply(lambda x: list(x.unique()))
        .tolist()
    )

    return transactions, top_products


def translate_rules_to_english(rules_df: pd.DataFrame) -> list[dict]:
    """
    Convert technical association rules to plain English
    business recommendations.
    """
    results = []

    for _, row in rules_df.iterrows():
        antecedents = list(row["antecedents"])
        consequents = list(row["consequents"])

        support    = round(float(row["support"]),    4)
        confidence = round(float(row["confidence"]), 4)
        lift       = round(float(row["lift"]),       4)

        # Build English sentence
        if len(antecedents) == 1:
            ant_str = f'"{antecedents[0]}"'
        else:
            ant_str = ", ".join(f'"{a}"' for a in antecedents[:-1])
            ant_str += f' and "{antecedents[-1]}"'

        if len(consequents) == 1:
            con_str = f'"{consequents[0]}"'
        else:
            con_str = ", ".join(f'"{c}"' for c in consequents)

        confidence_pct = round(confidence * 100, 1)
        support_pct    = round(support    * 100, 1)

        english = (
            f"{confidence_pct}% of customers who buy {ant_str} "
            f"also buy {con_str}. "
            f"This pattern appears in {support_pct}% of all transactions "
            f"and is {lift:.1f}x more likely than random chance."
        )

        # Strength label
        if lift >= 3:
            strength = "Very Strong"
        elif lift >= 2:
            strength = "Strong"
        elif lift >= 1.5:
            strength = "Moderate"
        else:
            strength = "Weak"

        results.append({
            "antecedents":    antecedents,
            "consequents":    consequents,
            "support":        support,
            "confidence":     confidence,
            "lift":           lift,
            "support_pct":    support_pct,
            "confidence_pct": confidence_pct,
            "strength":       strength,
            "english":        english,
        })

    return results


def run_apriori(
    df: pd.DataFrame,
    min_support:    float = 0.01,
    min_confidence: float = 0.1,
    max_rules:      int   = 20,
    top_n_products: int   = 100,
) -> dict:
    """
    Full Apriori pipeline:
    1. Format transactions (top N products only)
    2. Encode to binary matrix
    3. Run Apriori with progressive support fallback
    4. Generate association rules with progressive confidence fallback
    5. Sort by lift, take top N rules
    6. Translate to English
    7. Return results
    """

    # Step 1 — Format transactions
    transactions, top_products = format_transactions(df, top_n_products)

    # Keep only multi-item baskets
    transactions = [t for t in transactions if len(t) >= 2]

    if len(transactions) < 10:
        raise ValueError(
            f"Not enough multi-item transactions: {len(transactions)}. "
            f"Need at least 10."
        )

    # Step 2 — Encode to binary matrix
    te        = TransactionEncoder()
    te_array  = te.fit_transform(transactions)
    basket_df = pd.DataFrame(te_array, columns=te.columns_)

    # Step 3 — Run Apriori with progressive fallback
    frequent_itemsets = pd.DataFrame()
    support_used      = min_support

    for attempt in [min_support, 0.02, 0.01, 0.005, 0.003]:
        frequent_itemsets = apriori(
            basket_df,
            min_support=attempt,
            use_colnames=True
        )
        pairs = frequent_itemsets[
            frequent_itemsets["itemsets"].apply(len) >= 2
        ]
        if not pairs.empty:
            support_used = attempt
            break

    if frequent_itemsets.empty:
        raise ValueError("No frequent itemsets found.")

    # Step 4 — Generate rules with progressive confidence fallback
    rules = pd.DataFrame()

    for attempt_conf in [min_confidence, 0.1, 0.05, 0.01]:
        try:
            rules = association_rules(
                frequent_itemsets,
                metric="confidence",
                min_threshold=attempt_conf,
                num_itemsets=len(frequent_itemsets)
            )
            if not rules.empty:
                break
        except TypeError:
            try:
                rules = association_rules(
                    frequent_itemsets,
                    metric="confidence",
                    min_threshold=attempt_conf
                )
                if not rules.empty:
                    break
            except Exception:
                continue
        except Exception:
            continue

    if rules.empty:
        raise ValueError(
            "No association rules found. "
            "Dataset products may be too diverse for association mining."
        )

    # Step 5 — Sort by lift, take top N
    rules = rules.sort_values("lift", ascending=False).head(max_rules)

    # Step 6 — Translate to English
    english_rules = translate_rules_to_english(rules)

    # Step 7 — Return results
    return {
        "total_transactions": len(transactions),
        "total_products":     len(te.columns_),
        "top_products_used":  top_n_products,
        "frequent_itemsets":  len(frequent_itemsets),
        "total_rules_found":  len(rules),
        "parameters": {
            "min_support":    support_used,
            "min_confidence": min_confidence,
        },
        "top_rules": english_rules,
        "summary": {
            "avg_confidence": round(float(rules["confidence"].mean()), 4),
            "avg_lift":       round(float(rules["lift"].mean()),       4),
            "max_lift":       round(float(rules["lift"].max()),        4),
            "strongest_rule": english_rules[0]["english"] if english_rules else None,
        }
    }

def run_apriori_generic(df: pd.DataFrame, max_rules: int = 20) -> dict:
    """
    For non-transaction datasets: find correlations between
    categorical columns instead of basket analysis.
    Groups by category columns and finds co-occurrence patterns.
    """
    df = _normalize_columns(df)

    # Find categorical columns
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    cat_cols = [c for c in cat_cols if df[c].nunique() < 50 and df[c].nunique() > 1]

    if len(cat_cols) < 1:
        raise ValueError("No suitable categorical columns found for association analysis.")

    # Use first categorical column as item column
    item_col = cat_cols[0]

    # Find numeric column for grouping
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    # Build pseudo-transactions: each row is a "basket" of category values
    transactions = []
    for _, row in df.iterrows():
        basket = []
        for col in cat_cols:
            val = str(row[col]).strip()
            if val and val.lower() not in ["nan","none",""]:
                basket.append(f"{col}={val}")
        if len(basket) >= 2:
            transactions.append(basket)

    if len(transactions) < 5:
        # Fallback: just return top value combinations
        result_rules = []
        for col in cat_cols[:3]:
            top_vals = df[col].value_counts().head(5)
            for val, count in top_vals.items():
                pct = round(count / len(df) * 100, 1)
                result_rules.append({
                    "antecedents": [col],
                    "consequents": [str(val)],
                    "support": round(count / len(df), 4),
                    "confidence": round(count / len(df), 4),
                    "lift": 1.0,
                    "support_pct": pct,
                    "confidence_pct": pct,
                    "strength": "Moderate",
                    "english": f"{pct}% of records have {col} = {val}."
                })
        return {
            "total_transactions": len(df),
            "total_products": len(cat_cols),
            "top_products_used": len(cat_cols),
            "frequent_itemsets": len(result_rules),
            "total_rules_found": len(result_rules),
            "parameters": {"min_support": 0.01, "min_confidence": 0.1},
            "top_rules": result_rules[:max_rules],
            "summary": {
                "avg_confidence": 0.5,
                "avg_lift": 1.0,
                "max_lift": 1.0,
                "strongest_rule": result_rules[0]["english"] if result_rules else None
            }
        }

    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    basket_df = pd.DataFrame(te_array, columns=te.columns_)

    frequent_itemsets = pd.DataFrame()
    for attempt in [0.3, 0.2, 0.1, 0.05, 0.01]:
        frequent_itemsets = apriori(basket_df, min_support=attempt, use_colnames=True)
        if not frequent_itemsets.empty:
            break

    if frequent_itemsets.empty:
        raise ValueError("No patterns found in this dataset.")

    rules = pd.DataFrame()
    for attempt_conf in [0.5, 0.3, 0.1, 0.05]:
        try:
            rules = association_rules(frequent_itemsets, metric="confidence",
                                      min_threshold=attempt_conf, num_itemsets=len(frequent_itemsets))
            if not rules.empty:
                break
        except Exception:
            try:
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=attempt_conf)
                if not rules.empty:
                    break
            except Exception:
                continue

    if rules.empty:
        raise ValueError("No association rules found for this dataset.")

    rules = rules.sort_values("lift", ascending=False).head(max_rules)
    english_rules = translate_rules_to_english(rules)

    return {
        "total_transactions": len(transactions),
        "total_products": len(te.columns_),
        "top_products_used": len(cat_cols),
        "frequent_itemsets": len(frequent_itemsets),
        "total_rules_found": len(rules),
        "parameters": {"min_support": 0.01, "min_confidence": 0.1},
        "top_rules": english_rules,
        "summary": {
            "avg_confidence": round(float(rules["confidence"].mean()), 4),
            "avg_lift": round(float(rules["lift"].mean()), 4),
            "max_lift": round(float(rules["lift"].max()), 4),
            "strongest_rule": english_rules[0]["english"] if english_rules else None
        }
    }


def run_apriori_auto(df: pd.DataFrame, min_support: float = 0.01,
                     min_confidence: float = 0.1, max_rules: int = 20,
                     top_n_products: int = 100) -> dict:
    """Auto-detect dataset type and run appropriate Apriori."""
    df_norm = _normalize_columns(df)
    has_invoice = any(c in df_norm.columns for c in ["invoice","invoiceno","invoice_no","order_id","transaction_id"])
    has_desc    = any(c in df_norm.columns for c in ["description","product","item","product_name","product_category"])

    if has_invoice and has_desc:
        return run_apriori(df, min_support=min_support, min_confidence=min_confidence,
                           max_rules=max_rules, top_n_products=top_n_products)
    else:
        return run_apriori_generic(df, max_rules=max_rules)
