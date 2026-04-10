import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import warnings
warnings.filterwarnings("ignore")


def _normalize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str).str.strip().str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def _pick_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"None of these columns exist: {candidates}. "
        f"Available: {list(df.columns)}"
    )


def _is_retail_dataset(df):
    """Check if dataset has transaction/customer structure for RFM."""
    df = _normalize_columns(df)
    has_customer = any(c in df.columns for c in ["customer_id","customerid","customer"])
    has_date     = any(c in df.columns for c in ["invoicedate","invoice_date","date","order_date","purchase_date"])
    has_price    = any(c in df.columns for c in ["price","unitprice","unit_price"])
    has_qty      = any(c in df.columns for c in ["quantity","qty"])
    return has_customer and has_date and has_price and has_qty


def build_customer_features(df):
    """RFM features for retail/transaction datasets."""
    df = _normalize_columns(df)

    invoice_col  = _pick_column(df, ["invoice","invoiceno","invoice_no","order_id","transaction_id","id"])
    customer_col = _pick_column(df, ["customer_id","customerid","customer"])
    date_col     = _pick_column(df, ["invoicedate","invoice_date","date","order_date","purchase_date"])
    qty_col      = _pick_column(df, ["quantity","qty"])
    price_col    = _pick_column(df, ["price","unitprice","unit_price"])

    df[date_col]  = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[customer_col, date_col, qty_col, price_col])
    df[qty_col]   = pd.to_numeric(df[qty_col],   errors="coerce")
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[qty_col, price_col])
    df = df[(df[qty_col] > 0) & (df[price_col] >= 0)]
    df["revenue"] = df[qty_col] * df[price_col]

    ref_date = df[date_col].max()
    rfm = (
        df.groupby(customer_col)
        .agg(
            Recency  =(date_col,    lambda x: (ref_date - x.max()).days),
            Frequency=(invoice_col, "nunique"),
            Monetary =("revenue",   "sum"),
        )
        .reset_index()
        .rename(columns={customer_col: "CustomerID"})
    )
    rfm["Recency"] = rfm["Recency"].clip(lower=0)

    # Remove extreme outliers (top 1% per metric) before clustering
    for col in ["Recency", "Frequency", "Monetary"]:
        upper = rfm[col].quantile(0.99)
        rfm = rfm[rfm[col] <= upper]

    return rfm


def build_generic_features(df):
    """
    For non-retail datasets: cluster on all numeric columns.
    Returns a features dataframe with an ID column.
    """
    df = _normalize_columns(df)

    # Pick numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Drop columns that are IDs or have too many nulls
    numeric_cols = [c for c in numeric_cols if df[c].isnull().mean() < 0.5]
    numeric_cols = [c for c in numeric_cols if df[c].nunique() > 1]

    if len(numeric_cols) < 2:
        raise ValueError(
            f"Need at least 2 numeric columns for clustering. "
            f"Found: {numeric_cols}"
        )

    features = df[numeric_cols].copy()
    features = features.fillna(features.median())

    # Add an ID column
    id_col = next((c for c in ["id","product_id","sku","name","product_name"] if c in df.columns), None)
    if id_col:
        features["_id"] = df[id_col].astype(str).values
    else:
        features["_id"] = [f"Row_{i}" for i in range(len(features))]

    return features, numeric_cols


def name_cluster_generic(profile, feature_cols):
    """Placeholder — actual naming done by rank in run_kmeans_generic"""
    return "Group"


def name_cluster(profile):
    """Auto-name RFM clusters."""
    r = profile["Recency"]
    f = profile["Frequency"]
    m = profile["Monetary"]

    if r <= 60 and f >= 3 and m >= 200:
        return "Premium Loyal Customers"
    elif r <= 90 and m >= 300:
        return "At-Risk High-Value"
    elif r <= 60 and f >= 3:
        return "Frequent Budget Buyers"
    elif r > 180 and f <= 2:
        return "Lost Customers"
    elif r > 90 and f <= 3:
        return "Lapsed Customers"
    elif f >= 3 and m >= 100:
        return "Loyal Mid-Tier"
    elif m >= 200:
        return "High Spenders"
    elif f >= 3:
        return "Frequent Buyers"
    else:
        return "New Customers"


def compute_shap_values(X_scaled, labels, feature_names):
    try:
        global_mean  = X_scaled.mean(axis=0)
        shap_results = {}
        for label in sorted(set(labels)):
            cluster_mean = X_scaled[labels == label].mean(axis=0)
            importance   = cluster_mean - global_mean
            shap_results[int(label)] = [
                {
                    "feature":    name,
                    "importance": round(float(imp), 4),
                    "direction":  "above average" if imp > 0 else "below average",
                }
                for name, imp in zip(feature_names, importance)
            ]
        return shap_results
    except Exception:
        return {}


def run_kmeans_clustering(features_df, k=4, random_state=42):
    """RFM-based KMeans for retail datasets."""
    X        = features_df[["Recency","Frequency","Monetary"]].values
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model    = KMeans(n_clusters=k, random_state=random_state, n_init="auto")
    labels   = model.fit_predict(X_scaled)

    sil_score = float(silhouette_score(X_scaled, labels)) if len(features_df) > k and k >= 2 else None
    db_score  = float(davies_bouldin_score(X_scaled, labels)) if len(features_df) > k and k >= 2 else None

    out = features_df.copy()
    out["cluster"] = labels
    profiles      = []
    cluster_names = {}

    for cluster_id in sorted(out["cluster"].unique()):
        cdata   = out[out["cluster"] == cluster_id]
        profile = {
            "cluster":   int(cluster_id),
            "size":      int(len(cdata)),
            "pct":       round(len(cdata) / len(out) * 100, 1),
            "Recency":   round(float(cdata["Recency"].mean()),   1),
            "Frequency": round(float(cdata["Frequency"].mean()), 1),
            "Monetary":  round(float(cdata["Monetary"].mean()),  1),
        }
        profile["name"] = name_cluster(profile)
        cluster_names[int(cluster_id)] = profile["name"]
        total_revenue = out["Monetary"].sum()
        profile["revenue_pct"] = round(float(cdata["Monetary"].sum()) / total_revenue * 100, 1) if total_revenue > 0 else 0.0
        profiles.append(profile)

    # Apply relative naming — guaranteed unique names
    r_rank = sorted([p["cluster"] for p in profiles], key=lambda i: next(p["Recency"]   for p in profiles if p["cluster"]==i))
    f_rank = sorted([p["cluster"] for p in profiles], key=lambda i: next(p["Frequency"] for p in profiles if p["cluster"]==i), reverse=True)
    m_rank = sorted([p["cluster"] for p in profiles], key=lambda i: next(p["Monetary"]  for p in profiles if p["cluster"]==i), reverse=True)
    scores = {p["cluster"]: r_rank.index(p["cluster"]) + f_rank.index(p["cluster"]) + m_rank.index(p["cluster"]) for p in profiles}
    ranked = sorted([p["cluster"] for p in profiles], key=lambda i: scores[i])
    all_names = ["Premium Loyal Customers", "At-Risk High-Value", "Lapsed Customers", "Lost Customers",
                 "Loyal Mid-Tier", "Frequent Buyers", "New Customers", "High Spenders"]
    for i, cid in enumerate(ranked):
        name = all_names[i] if i < len(all_names) else f"Cluster {i+1}"
        cluster_names[cid] = name
        next(p for p in profiles if p["cluster"]==cid)["name"] = name

    # Add cluster_name to dataframe
    out["cluster_name"] = out["cluster"].map(cluster_names)

    shap_values = compute_shap_values(X_scaled, labels, ["Recency","Frequency","Monetary"])
    for cluster_id, imp_list in shap_values.items():
        for item in imp_list:
            item["cluster_name"] = cluster_names.get(cluster_id, f"Cluster {cluster_id}")

    return {
        "mode": "rfm",
        "k": k,
        "silhouette_score": round(sil_score, 4) if sil_score else None,
        "davies_bouldin":   round(db_score,  4) if db_score  else None,
        "cluster_profiles": profiles,
        "cluster_names":    cluster_names,
        "shap_importance":  shap_values,
        "customer_clusters": out[["CustomerID","Recency","Frequency","Monetary","cluster","cluster_name"]].to_dict(orient="records"),
    }


def run_kmeans_generic(df, k=4, random_state=42):
    """Generic KMeans for non-retail datasets — clusters on numeric columns."""
    features, numeric_cols = build_generic_features(df)

    ids      = features["_id"].values
    X        = features[numeric_cols].values
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model    = KMeans(n_clusters=k, random_state=random_state, n_init="auto")
    labels   = model.fit_predict(X_scaled)

    sil_score = float(silhouette_score(X_scaled, labels)) if len(features) > k and k >= 2 else None
    db_score  = float(davies_bouldin_score(X_scaled, labels)) if len(features) > k and k >= 2 else None

    profiles      = []
    cluster_names = {}
    global_mean   = X_scaled.mean(axis=0)

    for cluster_id in sorted(set(labels)):
        mask         = labels == cluster_id
        cluster_mean = X_scaled[mask].mean(axis=0)
        importance   = cluster_mean - global_mean

        profile = {"cluster": int(cluster_id), "size": int(mask.sum()), "pct": round(mask.sum() / len(labels) * 100, 1)}
        for i, col in enumerate(numeric_cols):
            profile[col] = round(float(features[numeric_cols].values[mask, i].mean()), 2)
        profile["_scaled_importance"] = {col: round(float(importance[i]), 4) for i, col in enumerate(numeric_cols)}
        profile["name"] = name_cluster_generic(profile["_scaled_importance"], numeric_cols)
        cluster_names[int(cluster_id)] = profile["name"]
        profiles.append(profile)

    # Rank-based unique naming — sorted by sum of all numeric values
    name_pool = ["Top Tier Group", "High Value Group", "Standard Group", "Budget Group",
                 "Growth Group", "Emerging Group", "Niche Group", "Baseline Group"]
    for p in profiles:
        p["_score"] = sum(p.get(col, 0) for col in numeric_cols)
    ranked = sorted(profiles, key=lambda p: p["_score"], reverse=True)
    for i, p in enumerate(ranked):
        p["name"] = name_pool[i] if i < len(name_pool) else f"Group {i+1}"
        cluster_names[int(p["cluster"])] = p["name"]
    for p in profiles:
        p.pop("_score", None)

    shap_values = compute_shap_values(X_scaled, labels, numeric_cols)
    for cluster_id, imp_list in shap_values.items():
        for item in imp_list:
            item["cluster_name"] = cluster_names.get(cluster_id, f"Cluster {cluster_id}")

    rows = []
    for i, (label, id_val) in enumerate(zip(labels, ids)):
        row = {"ID": id_val, "cluster": int(label), "cluster_name": cluster_names[int(label)]}
        for j, col in enumerate(numeric_cols):
            row[col] = round(float(X[i, j]), 4)
        rows.append(row)

    return {
        "mode":             "generic",
        "k":                k,
        "features_used":    numeric_cols,
        "silhouette_score": round(sil_score, 4) if sil_score else None,
        "davies_bouldin":   round(db_score,  4) if db_score  else None,
        "cluster_profiles": profiles,
        "cluster_names":    cluster_names,
        "shap_importance":  shap_values,
        "customer_clusters": rows,
    }


def run_kmeans_auto(df, k=4, random_state=42):
    """
    Auto-detect dataset type and run appropriate KMeans.
    Retail → RFM clustering
    Generic → numeric column clustering
    """
    if _is_retail_dataset(df):
        features_df = build_customer_features(df)
        if len(features_df) < k:
            raise ValueError(f"Not enough customers ({len(features_df)}) for k={k}. Reduce k.")
        return run_kmeans_clustering(features_df, k=k, random_state=random_state)
    else:
        return run_kmeans_generic(df, k=k, random_state=random_state)
