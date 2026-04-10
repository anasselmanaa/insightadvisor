import json
import os
from pathlib import Path
from datetime import timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

from backend_core.storage import cleaned_path

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
FREE_MODELS = [
    "openai/gpt-oss-20b:free",
    "openai/gpt-oss-120b:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "arcee-ai/trinity-mini:free",
]
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "RetailIQ")


def _get_response(prompt: str, temperature: float = 0.2) -> str:
    """Call AI API — tries Groq first, then OpenRouter as fallback"""
    import os
    groq_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Try Groq first (fast, reliable, works in China)
    if groq_key:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": groq_model,
                    "messages": [
                        {"role": "system", "content": "You are InsightAdvisor AI, a senior business analytics assistant. Be concise, helpful and specific with data."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": 500,
                },
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    # Fallback to OpenRouter
    if not OPENROUTER_API_KEY:
        raise ValueError("No AI API key available")

    models_to_try = list(dict.fromkeys([OPENROUTER_MODEL] + FREE_MODELS))
    for model in models_to_try:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": OPENROUTER_SITE_URL,
                    "X-Title": OPENROUTER_APP_NAME,
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are InsightAdvisor AI, a senior business analytics assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                },
                timeout=60,
            )
            if response.status_code == 429:
                continue
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            continue

    raise RuntimeError("All AI services are currently unavailable. Please try again later.")


def build_analysis_context(reports_dir: Path, dataset_id: str) -> dict:
    """
    Collect all analysis results for a dataset into one context object.
    Reads from saved JSON reports in data/processed/
    """
    context = {}

    def load_report(suffix: str) -> dict:
        path = reports_dir / f"{dataset_id}__{suffix}.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    cleaning = load_report("cleaning_report")
    arima = load_report("arima_report")
    apriori = load_report("apriori_report")
    regression = load_report("regression_report")
    anomaly = load_report("anomaly_report")
    kmeans = load_report("kmeans_report")
    causal = load_report("causal_report")

    if cleaning:
        context["data_quality"] = {
            "quality_score": cleaning.get("quality_score"),
            "rows_before": cleaning.get("rows_before"),
            "rows_after": cleaning.get("rows_after"),
            "duplicates_removed": cleaning.get("duplicates_removed"),
            "outliers_removed": cleaning.get("outliers_removed"),
            "missing_before": cleaning.get("missing_before"),
        }

    if kmeans and kmeans.get("cluster_profiles"):
        context["customer_segments"] = {
            "k": kmeans.get("k"),
            "silhouette_score": kmeans.get("silhouette_score"),
            "davies_bouldin": kmeans.get("davies_bouldin"),
            "profiles": kmeans.get("cluster_profiles", [])[:6],
        }

    if arima and arima.get("summary"):
        context["sales_forecast"] = {
            "model": arima.get("model"),
            "trend": arima.get("summary", {}).get("trend"),
            "total_forecast_revenue": arima.get("summary", {}).get("total_forecast_revenue"),
            "avg_daily_forecast": arima.get("summary", {}).get("avg_daily_forecast"),
            "rmse": arima.get("metrics", {}).get("rmse"),
            "mape": arima.get("metrics", {}).get("mape"),
            "forecast_days": arima.get("forecast_days"),
        }

    if apriori and apriori.get("top_rules"):
        context["association_rules"] = {
            "total_rules": apriori.get("total_rules_found"),
            "top_3_rules": [
                rule.get("english", "")
                for rule in apriori.get("top_rules", [])[:3]
            ],
            "max_lift": apriori.get("summary", {}).get("max_lift"),
        }

    if regression and regression.get("metrics"):
        context["regression"] = {
            "target": regression.get("target_column"),
            "r2": regression.get("metrics", {}).get("r2"),
            "mae": regression.get("metrics", {}).get("mae"),
            "rmse": regression.get("metrics", {}).get("rmse"),
            "top_features": regression.get("feature_importance", [])[:3],
            "interpretation": regression.get("interpretation"),
        }

    if anomaly:
        top_anomalies = anomaly.get("top_anomalies", [])
        context["anomalies"] = {
            "total_anomalies": anomaly.get("total_anomalies"),
            "anomaly_pct": anomaly.get("anomaly_pct"),
            "top_example": top_anomalies[0].get("explanation", "") if top_anomalies else "",
        }

    if causal:
        context["causal_insights"] = {
            "relationships_found": causal.get("relationships_found"),
            "top_relationships": causal.get("relationships", [])[:3],
        }

    return context


def _clean_json_text(text: str) -> str:
    return text.replace("```json", "").replace("```", "").strip()


def _estimate_revenue_impact(context: dict) -> str:
    forecast = context.get("sales_forecast", {})
    avg_daily = forecast.get("avg_daily_forecast")

    if avg_daily and isinstance(avg_daily, (int, float)):
        estimated = round(avg_daily * 0.08, 2)
        return f"Estimated short-term uplift: about {estimated} extra revenue units per day if executed well"

    return "Estimated short-term uplift: 5% to 10% revenue improvement if executed well"


def _generate_rule_based_recommendations(context: dict) -> dict:
    quality = context.get("data_quality", {}).get("quality_score")
    trend = context.get("sales_forecast", {}).get("trend")
    anomalies = context.get("anomalies", {}).get("total_anomalies", 0)
    rules = context.get("association_rules", {}).get("top_3_rules", [])
    segments = context.get("customer_segments", {}).get("profiles", [])

    if quality is not None and quality < 75:
        priority_1 = {
            "title": "Improve data quality first",
            "action": "Fix missing values, check pricing errors, and review outlier rows today before making business decisions",
            "reason": "Low data quality can make every downstream recommendation less reliable",
            "expected_impact": "Higher confidence in all analytics and fewer wrong decisions",
        }
    elif anomalies and anomalies > 0:
        priority_1 = {
            "title": "Review unusual transactions",
            "action": "Investigate the most abnormal transactions today and confirm whether they are fraud, returns, or data-entry mistakes",
            "reason": "Anomalies often reveal hidden revenue leakage or operational issues",
            "expected_impact": _estimate_revenue_impact(context),
        }
    else:
        priority_1 = {
            "title": "Protect top-performing sales patterns",
            "action": "Review your strongest product and customer patterns today and make sure stock, pricing, and promotions support them",
            "reason": "Fast action on existing strengths usually gives the quickest payoff",
            "expected_impact": _estimate_revenue_impact(context),
        }

    if trend == "decreasing":
        priority_2 = {
            "title": "Respond to declining sales trend",
            "action": "Launch a focused promotion this week for your best-performing products and re-engage recent inactive customers",
            "reason": "The forecast suggests sales may weaken if no action is taken",
            "expected_impact": "Can reduce forecast decline and recover 5% to 12% of expected lost revenue",
        }
    elif rules:
        priority_2 = {
            "title": "Use product bundling opportunities",
            "action": "Create bundle offers this week based on the strongest association rules found in the basket analysis",
            "reason": "Customers already show repeat co-purchase behavior in the data",
            "expected_impact": "Can improve average basket value by 4% to 10%",
        }
    else:
        priority_2 = {
            "title": "Strengthen weekly sales execution",
            "action": "This week, segment customers by behavior and target the highest-value group with more personalized promotions",
            "reason": "Segment-based actions are usually more effective than broad campaigns",
            "expected_impact": "Can improve campaign efficiency and increase conversion rate",
        }

    if segments:
        priority_3 = {
            "title": "Build segment-specific strategy",
            "action": "This month, design separate retention, upsell, and win-back plans for each major customer segment",
            "reason": "Different customer groups need different actions to maximize value",
            "expected_impact": "Can improve retention and long-term customer lifetime value",
        }
    else:
        priority_3 = {
            "title": "Build a monthly optimization cycle",
            "action": "This month, create a repeatable process for tracking top products, top customers, anomalies, and forecast changes",
            "reason": "Consistent monitoring improves decision quality over time",
            "expected_impact": "Better planning, faster intervention, and more stable revenue growth",
        }

    return {
        "priority_1": priority_1,
        "priority_2": priority_2,
        "priority_3": priority_3,
        "overall_health": "Business health is moderate and should improve with targeted action on quality, demand patterns, and customer behavior",
        "biggest_opportunity": "The biggest opportunity is to turn existing analysis into fast, segment-specific actions that lift revenue",
    }


def _generate_rule_based_action_plan(context: dict) -> dict:
    return {
        "today": [
            {
                "action": "Review anomalies and validate unusual transactions",
                "department": "Operations",
                "effort": "Low",
                "impact": "Removes risky records and uncovers urgent operational issues",
                "expected_revenue_impact": "Protect 2% to 5% of revenue from leakage or errors",
            },
            {
                "action": "Check the highest-value customer segment and verify product availability",
                "department": "Sales",
                "effort": "Low",
                "impact": "Prevents missed revenue from stock or fulfillment problems",
                "expected_revenue_impact": "Support immediate revenue capture from top buyers",
            },
        ],
        "this_week": [
            {
                "action": "Launch a promotion or bundle based on the strongest association rule",
                "department": "Marketing",
                "effort": "Medium",
                "impact": "Increases average basket size",
                "expected_revenue_impact": "Potential basket uplift of 4% to 10%",
            },
            {
                "action": "Target at-risk or inactive customers with a recovery campaign",
                "department": "Sales",
                "effort": "Medium",
                "impact": "Improves retention and repeat purchases",
                "expected_revenue_impact": "Recover 3% to 8% of otherwise lost revenue",
            },
        ],
        "this_month": [
            {
                "action": "Create segment-specific retention and upsell strategy",
                "department": "Management",
                "effort": "High",
                "impact": "Turns analytics into a repeatable growth system",
                "expected_revenue_impact": "Long-term customer lifetime value increase",
            },
            {
                "action": "Set up KPI tracking for forecast trend, anomaly rate, and segment performance",
                "department": "Finance",
                "effort": "Medium",
                "impact": "Improves business decision speed and control",
                "expected_revenue_impact": "Supports steadier month-over-month growth",
            },
        ],
        "kpis_to_track": [
            "Daily revenue",
            "Average basket value",
            "Repeat customer rate",
            "Anomaly rate",
            "Segment revenue contribution",
        ],
    }


def generate_recommendations(context: dict) -> dict:
    """
    Send analysis context to OpenRouter and get business recommendations.
    Falls back to local rule-based recommendations if API fails.
    """
    prompt = f"""
You are a senior retail business analyst.
Here is the full analysis context:

{json.dumps(context, indent=2)}

Generate exactly 3 prioritized business recommendations.
Return valid JSON only.

Use this exact format:
{{
  "priority_1": {{
    "title": "Short action title",
    "action": "Specific action to take TODAY",
    "reason": "Why this is urgent based on the data",
    "expected_impact": "Estimated business impact"
  }},
  "priority_2": {{
    "title": "Short action title",
    "action": "Specific action to take THIS WEEK",
    "reason": "Why this matters based on the data",
    "expected_impact": "Estimated business impact"
  }},
  "priority_3": {{
    "title": "Short action title",
    "action": "Specific action to take THIS MONTH",
    "reason": "Why this is important based on the data",
    "expected_impact": "Estimated business impact"
  }},
  "overall_health": "One sentence summary of business health",
  "biggest_opportunity": "Single biggest opportunity identified from the data"
}}
"""

    try:
        text = _get_response(prompt)
        recommendations = json.loads(_clean_json_text(text))
        return {
            "status": "success",
            "source": "openrouter",
            "recommendations": recommendations,
            "context_used": list(context.keys()),
        }
    except Exception as e:
        fallback = _generate_rule_based_recommendations(context)
        return {
            "status": "success",
            "source": "fallback",
            "recommendations": fallback,
            "context_used": list(context.keys()),
            "warning": str(e),
        }


def generate_action_plan(context: dict) -> dict:
    """
    Generate a detailed prescriptive action plan from analysis results.
    Falls back to local rule-based action plan if API fails.
    """
    prompt = f"""
You are a senior retail business consultant.
Based on this analysis context:

{json.dumps(context, indent=2)}

Generate a prescriptive action plan.
Return valid JSON only.

Use this exact format:
{{
  "today": [
    {{
      "action": "Specific action",
      "department": "Marketing/Sales/Operations/Finance",
      "effort": "Low/Medium/High",
      "impact": "Expected result",
      "expected_revenue_impact": "Estimated revenue impact"
    }}
  ],
  "this_week": [
    {{
      "action": "Specific action",
      "department": "Department name",
      "effort": "Low/Medium/High",
      "impact": "Expected result",
      "expected_revenue_impact": "Estimated revenue impact"
    }}
  ],
  "this_month": [
    {{
      "action": "Specific action",
      "department": "Department name",
      "effort": "Low/Medium/High",
      "impact": "Expected result",
      "expected_revenue_impact": "Estimated revenue impact"
    }}
  ],
  "kpis_to_track": ["KPI 1", "KPI 2", "KPI 3"]
}}
"""

    try:
        text = _get_response(prompt)
        action_plan = json.loads(_clean_json_text(text))
        return {
            "status": "success",
            "source": "openrouter",
            "action_plan": action_plan,
        }
    except Exception as e:
        fallback = _generate_rule_based_action_plan(context)
        return {
            "status": "success",
            "source": "fallback",
            "action_plan": fallback,
            "warning": str(e),
        }


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return df


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _prepare_revenue(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    quantity_col = _pick_column(df, ["quantity"])
    price_col = _pick_column(df, ["price", "unitprice", "unit_price"])
    revenue_col = _pick_column(df, ["revenue", "sales", "total_sales"])

    if revenue_col:
        df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce")
        return df

    if quantity_col and price_col:
        df[quantity_col] = pd.to_numeric(df[quantity_col], errors="coerce")
        df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
        df["revenue"] = df[quantity_col] * df[price_col]

    return df


def process_nl_query(dataset_id: str, query: str) -> dict:
    """
    Process a natural language query using local pandas logic.
    Returns summary + table data + chart-ready data.
    """
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        return {
            "status": "error",
            "query": query,
            "error": "Cleaned dataset not found. Upload and clean the dataset first.",
        }

    try:
        df = pd.read_csv(cleaned_file)
        df = _normalize_columns(df)
        df = _prepare_revenue(df)

        date_col = _pick_column(df, ["invoicedate", "invoice_date", "date"])
        customer_col = _pick_column(df, ["customer_id", "customerid"])
        country_col = _pick_column(df, ["country"])
        product_col = _pick_column(df, ["description", "stockcode", "stock_code"])
        revenue_col = _pick_column(df, ["revenue", "sales", "total_sales"])

        query_lower = query.strip().lower()

        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        if "top customers last month" in query_lower:
            if not date_col or not customer_col or not revenue_col:
                return {
                    "status": "error",
                    "query": query,
                    "error": "This query needs date, customer, and revenue columns.",
                }

            max_date = df[date_col].max()
            if pd.isna(max_date):
                return {
                    "status": "error",
                    "query": query,
                    "error": "Date column could not be parsed.",
                }

            start_date = (max_date.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = max_date.replace(day=1) - timedelta(days=1)

            filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()

            result_df = (
                filtered.groupby(customer_col, dropna=False)[revenue_col]
                .sum()
                .reset_index()
                .sort_values(revenue_col, ascending=False)
                .head(10)
            )

            summary = f"Top customers for last month were calculated from {start_date.date()} to {end_date.date()}."

            return {
                "status": "success",
                "query": query,
                "intent": "top_customers_last_month",
                "summary": summary,
                "table": result_df.to_dict(orient="records"),
                "chart": {
                    "type": "bar",
                    "x": result_df[customer_col].astype(str).tolist(),
                    "y": result_df[revenue_col].fillna(0).round(2).tolist(),
                    "x_label": "Customer",
                    "y_label": "Revenue",
                    "title": "Top Customers Last Month",
                },
            }

        if "sales by country" in query_lower or "revenue by country" in query_lower:
            if not country_col or not revenue_col:
                return {
                    "status": "error",
                    "query": query,
                    "error": "This query needs country and revenue columns.",
                }

            result_df = (
                df.groupby(country_col, dropna=False)[revenue_col]
                .sum()
                .reset_index()
                .sort_values(revenue_col, ascending=False)
                .head(10)
            )

            return {
                "status": "success",
                "query": query,
                "intent": "sales_by_country",
                "summary": "Top countries by total revenue were calculated from the cleaned dataset.",
                "table": result_df.to_dict(orient="records"),
                "chart": {
                    "type": "bar",
                    "x": result_df[country_col].astype(str).tolist(),
                    "y": result_df[revenue_col].fillna(0).round(2).tolist(),
                    "x_label": "Country",
                    "y_label": "Revenue",
                    "title": "Sales by Country",
                },
            }

        if "top products" in query_lower or "best products" in query_lower:
            if not product_col:
                return {
                    "status": "error",
                    "query": query,
                    "error": "This query needs a product column such as description or stockcode.",
                }

            if revenue_col:
                result_df = (
                    df.groupby(product_col, dropna=False)[revenue_col]
                    .sum()
                    .reset_index()
                    .sort_values(revenue_col, ascending=False)
                    .head(10)
                )
                y_values = result_df[revenue_col].fillna(0).round(2).tolist()
                y_label = "Revenue"
            else:
                result_df = (
                    df.groupby(product_col, dropna=False)
                    .size()
                    .reset_index(name="count")
                    .sort_values("count", ascending=False)
                    .head(10)
                )
                y_values = result_df["count"].tolist()
                y_label = "Count"

            return {
                "status": "success",
                "query": query,
                "intent": "top_products",
                "summary": "Top products were ranked using the cleaned dataset.",
                "table": result_df.to_dict(orient="records"),
                "chart": {
                    "type": "bar",
                    "x": result_df[product_col].astype(str).tolist(),
                    "y": y_values,
                    "x_label": "Product",
                    "y_label": y_label,
                    "title": "Top Products",
                },
            }

        # Fall back to OpenRouter for any unrecognized query
        try:
            df_summary = df.describe().to_string()
            prompt = f"""You are a retail analytics assistant. The user is analyzing a dataset with these stats:
{df_summary}

User question: {query}

Answer in 2-3 sentences. Be helpful and specific. If you cannot answer from the data, say so briefly."""
            answer = _get_response(prompt)
            return {
                "status": "success",
                "query": query,
                "intent": "ai_response",
                "summary": answer,
                "table": [],
                "chart": {},
            }
        except Exception as ai_err:
            return {
                "status": "success",
                "query": query,
                "intent": "generic_summary",
                "summary": "I could not process that query right now. Try: Show me top products, Show me sales by country, or Show me top customers last month.",
                "table": [],
                "chart": {},
            }

    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "error": str(e),
        }