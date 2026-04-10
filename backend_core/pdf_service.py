import json
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from backend_core.storage import export_pdf_path

# ── Color Palette ─────────────────────────────────────
C_DARK      = colors.HexColor("#0f172a")
C_PRIMARY   = colors.HexColor("#4f46e5")
C_SECONDARY = colors.HexColor("#06b6d4")
C_SUCCESS   = colors.HexColor("#059669")
C_WARNING   = colors.HexColor("#d97706")
C_DANGER    = colors.HexColor("#dc2626")
C_WHITE     = colors.white
C_LIGHT     = colors.HexColor("#f8fafc")
C_GRAY      = colors.HexColor("#e2e8f0")
C_MUTED     = colors.HexColor("#64748b")
C_TEXT      = colors.HexColor("#1e293b")
C_ACCENT_BG = colors.HexColor("#eef2ff")

PAGE_W = A4[0]
CONTENT_W = PAGE_W - 3 * cm

def _load(path: Path) -> dict:
    if path and path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _styles():
    return {
        "cover_title": ParagraphStyle("cover_title",
            fontName="Helvetica-Bold", fontSize=32,
            textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=8, leading=38),
        "cover_sub": ParagraphStyle("cover_sub",
            fontName="Helvetica", fontSize=14,
            textColor=colors.HexColor("#c7d2fe"), alignment=TA_CENTER, spaceAfter=6),
        "cover_meta": ParagraphStyle("cover_meta",
            fontName="Helvetica", fontSize=10,
            textColor=colors.HexColor("#818cf8"), alignment=TA_CENTER),
        "section_num": ParagraphStyle("section_num",
            fontName="Helvetica-Bold", fontSize=11,
            textColor=C_PRIMARY, spaceBefore=20, spaceAfter=2),
        "h1": ParagraphStyle("h1",
            fontName="Helvetica-Bold", fontSize=18,
            textColor=C_DARK, spaceBefore=4, spaceAfter=4),
        "h2": ParagraphStyle("h2",
            fontName="Helvetica-Bold", fontSize=12,
            textColor=C_PRIMARY, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=10,
            textColor=C_TEXT, leading=16, spaceAfter=4),
        "muted": ParagraphStyle("muted",
            fontName="Helvetica-Oblique", fontSize=9,
            textColor=C_MUTED, leading=14, spaceAfter=4),
        "metric_label": ParagraphStyle("metric_label",
            fontName="Helvetica", fontSize=8,
            textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=2),
        "metric_value": ParagraphStyle("metric_value",
            fontName="Helvetica-Bold", fontSize=18,
            textColor=C_PRIMARY, alignment=TA_CENTER),
        "metric_value_sm": ParagraphStyle("metric_value_sm",
            fontName="Helvetica-Bold", fontSize=13,
            textColor=C_PRIMARY, alignment=TA_CENTER),
        "tag": ParagraphStyle("tag",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=C_WHITE, alignment=TA_CENTER),
        "rule_text": ParagraphStyle("rule_text",
            fontName="Helvetica", fontSize=10,
            textColor=C_TEXT, leading=15, spaceAfter=6,
            leftIndent=12, borderPad=0),
    }

def _divider(color=C_PRIMARY, thick=2):
    return HRFlowable(width="100%", thickness=thick,
        color=color, spaceAfter=8, spaceBefore=2)

def _thin_divider():
    return HRFlowable(width="100%", thickness=0.5,
        color=C_GRAY, spaceAfter=6, spaceBefore=6)

def _section_header(num, title, styles):
    return KeepTogether([
        Paragraph(f"SECTION {num}", styles["section_num"]),
        Paragraph(title, styles["h1"]),
        _divider(),
    ])

def _metric_cards(metrics, styles):
    n = len(metrics)
    col_w = CONTENT_W / n
    labels = [Paragraph(m[0], styles["metric_label"]) for m in metrics]
    values = []
    for m in metrics:
        val = str(m[1])
        st = styles["metric_value"] if len(val) <= 8 else styles["metric_value_sm"]
        values.append(Paragraph(val, st))
    t = Table([labels, values],
        colWidths=[col_w] * n,
        rowHeights=[20, 36])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_ACCENT_BG),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.3, C_GRAY),
        ("LINEAFTER",     (0, 0), (-2, -1), 0.3, C_GRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("BOX",           (0, 0), (-1, -1), 1, C_PRIMARY),
    ]))
    return t

def _data_table(headers, rows, col_widths=None):
    if not rows:
        return Spacer(1, 0.1*cm)
    data = [[Paragraph(str(h), ParagraphStyle("th",
        fontName="Helvetica-Bold", fontSize=9,
        textColor=C_WHITE, alignment=TA_CENTER)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), ParagraphStyle("td",
            fontName="Helvetica", fontSize=9,
            textColor=C_TEXT)) for c in row])
    n = len(headers)
    if col_widths is None:
        col_widths = [CONTENT_W / n] * n
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  C_PRIMARY),
        ("BACKGROUND",    (0, 1), (-1, -1), C_WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_GRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("BOX",           (0, 0), (-1, -1), 1, C_PRIMARY),
    ]))
    return t

def _tag(text, color=C_PRIMARY):
    data = [[Paragraph(text, ParagraphStyle("tg",
        fontName="Helvetica-Bold", fontSize=8,
        textColor=C_WHITE, alignment=TA_CENTER))]]
    t = Table(data, colWidths=[2.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
    ]))
    return t

def _quality_color(score):
    if score is None: return C_MUTED
    if score >= 80: return C_SUCCESS
    if score >= 60: return C_WARNING
    return C_DANGER

# ── Cover Page ────────────────────────────────────────
def _cover(dataset_id, styles):
    now = datetime.now().strftime("%B %d, %Y")
    elements = []

    # Full-width dark header
    cover = Table([[
        Paragraph("InsightAdvisor", styles["cover_title"]),
    ]], colWidths=[PAGE_W - 2*cm])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_DARK),
        ("TOPPADDING",    (0,0),(-1,-1), 50),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
    ]))
    elements.append(cover)

    sub = Table([[Paragraph("AI-Powered Business Analytics Report", styles["cover_sub"])
    ]], colWidths=[PAGE_W - 2*cm])
    sub.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_DARK),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
    ]))
    elements.append(sub)

    # Accent bar
    accent_bar = Table([[Paragraph("", styles["cover_meta"])
    ]], colWidths=[PAGE_W - 2*cm], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), C_PRIMARY),
    ]))
    elements.append(accent_bar)

    meta = Table([[
        Paragraph(f"Dataset: {dataset_id[:16]}...  |  Generated: {now}  |  insightadvisor.co",
            styles["cover_meta"])
    ]], colWidths=[PAGE_W - 2*cm])
    meta.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_DARK),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 50),
    ]))
    elements.append(meta)
    elements.append(Spacer(1, 0.8*cm))

    # TOC-style summary box
    toc_items = [
        ["01", "Data Quality & Cleaning"],
        ["02", "Exploratory Data Analysis"],
        ["03", "Customer Segmentation"],
        ["04", "Sales Forecasting"],
        ["05", "Regression Analysis"],
        ["06", "Association Rules"],
        ["07", "Anomaly Detection"],
        ["08", "AI Recommendations"],
    ]
    toc_data = []
    for num, title in toc_items:
        toc_data.append([
            Paragraph(num, ParagraphStyle("tn", fontName="Helvetica-Bold",
                fontSize=11, textColor=C_PRIMARY, alignment=TA_CENTER)),
            Paragraph(title, ParagraphStyle("tt", fontName="Helvetica",
                fontSize=11, textColor=C_TEXT)),
        ])
    toc = Table(toc_data, colWidths=[1.5*cm, CONTENT_W - 1.5*cm])
    toc.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [C_LIGHT, C_WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("BOX",           (0,0),(-1,-1), 1, C_GRAY),
        ("LINEAFTER",     (0,0),(0,-1),  0.5, C_GRAY),
        ("LINEBEFORE",    (1,0),(1,-1),  0.5, C_GRAY),
    ]))
    elements.append(Paragraph("Table of Contents", styles["h2"]))
    elements.append(toc)
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 1: Data Quality ───────────────────────────
def _section_data_quality(report, styles):
    if not report:
        return []
    elements = [_section_header("01", "Data Quality & Cleaning", styles)]

    score = report.get("quality_score")
    score_color = _quality_color(score)

    # Fix outliers_removed if it's a dict
    outliers = report.get("outliers_removed", 0)
    if isinstance(outliers, dict):
        outliers = sum(outliers.values())

    metrics = [
        ("Quality Score", f"{score}/100" if score else "N/A"),
        ("Rows Before",   f"{report.get('rows_before', 'N/A'):,}" if isinstance(report.get('rows_before'), int) else report.get('rows_before', 'N/A')),
        ("Rows After",    f"{report.get('rows_after', 'N/A'):,}" if isinstance(report.get('rows_after'), int) else report.get('rows_after', 'N/A')),
        ("Duplicates",    report.get("duplicates_removed", 0)),
        ("Outliers",      outliers),
    ]
    elements.append(_metric_cards(metrics, styles))
    elements.append(Spacer(1, 0.4*cm))

    missing = report.get("missing_before", {})
    if missing:
        elements.append(Paragraph("Missing Values by Column", styles["h2"]))
        rows = [[col, str(count)] for col, count in list(missing.items())[:10]]
        elements.append(_data_table(["Column", "Missing Count"], rows,
            [CONTENT_W * 0.6, CONTENT_W * 0.4]))
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 2: EDA ────────────────────────────────────
def _section_eda(report, styles):
    if not report:
        return []
    elements = [_section_header("02", "Exploratory Data Analysis", styles)]

    stats = report.get("summary_statistics", {}) or report.get("numeric_summary", {})
    if stats:
        elements.append(Paragraph("Summary Statistics", styles["h2"]))
        rows = []
        for col, s in list(stats.items())[:8]:
            rows.append([col,
                str(round(s.get("mean", 0), 2)),
                str(round(s.get("std",  0), 2)),
                str(round(s.get("min",  0), 2)),
                str(round(s.get("max",  0), 2)),
            ])
        if rows:
            elements.append(_data_table(["Column","Mean","Std","Min","Max"], rows))
        elements.append(Spacer(1, 0.3*cm))

    top_cats = report.get("top_categories", {})
    if top_cats:
        elements.append(Paragraph("Top Categories", styles["h2"]))
        for col, items in list(top_cats.items())[:3]:
            elements.append(Paragraph(f"Top values — <b>{col}</b>:", styles["body"]))
            if isinstance(items, dict):
                values = items.get("values", [])
                counts = items.get("counts", [])
                rows = [[str(v), str(c)] for v, c in zip(values[:5], counts[:5])]
            elif isinstance(items, list):
                rows = [[str(i.get("value","")), str(i.get("count",""))] for i in items[:5]]
            else:
                rows = []
            if rows:
                elements.append(_data_table(["Value","Count"], rows,
                    [CONTENT_W * 0.7, CONTENT_W * 0.3]))
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 3: Clustering ─────────────────────────────
def _section_clustering(report, styles):
    if not report:
        return []
    elements = [_section_header("03", "Customer Segmentation (KMeans + RFM)", styles)]

    total = sum(p.get("size",0) for p in report.get("cluster_profiles",[]))
    metrics = [
        ("Clusters (k)",     report.get("k", "N/A")),
        ("Silhouette Score", round(report.get("silhouette_score", 0), 4)),
        ("Davies-Bouldin",   round(report.get("davies_bouldin",   0), 4)),
        ("Total Customers",  f"{total:,}"),
    ]
    elements.append(_metric_cards(metrics, styles))
    elements.append(Spacer(1, 0.4*cm))

    profiles = report.get("cluster_profiles", [])
    if profiles:
        elements.append(Paragraph("Cluster Profiles", styles["h2"]))
        rows = []
        for p in profiles:
            rows.append([
                p.get("name", f"Cluster {p.get('cluster')}"),
                f"{p.get('size', 0):,}",
                str(round(p.get("Recency",   p.get("avg_recency",   0)), 1)),
                str(round(p.get("Frequency", p.get("avg_frequency", 0)), 1)),
                str(round(p.get("Monetary",  p.get("avg_monetary",  0)), 2)),
                f"{p.get('pct', p.get('revenue_pct', 0))}%",
            ])
        elements.append(_data_table(
            ["Segment","Size","Recency","Frequency","Monetary","Revenue %"], rows))
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 4: Forecasting ────────────────────────────
def _section_forecasting(report, styles):
    if not report:
        return []
    elements = [_section_header("04", "Sales Forecasting (ARIMA)", styles)]

    m = report.get("metrics", {})
    s = report.get("summary", {})
    trend = s.get("trend", "N/A")
    trend_color = C_SUCCESS if trend == "increasing" else C_DANGER if trend == "decreasing" else C_WARNING

    metrics = [
        ("Model",         report.get("model", "ARIMA")),
        ("RMSE",          round(m.get("rmse", 0), 2)),
        ("MAPE",          f"{round(m.get('mape', 0), 2)}%"),
        ("Total Forecast",f"{round(s.get('total_forecast_revenue', 0), 0):,.0f}"),
        ("Trend",         trend.upper()),
    ]
    elements.append(_metric_cards(metrics, styles))
    elements.append(Spacer(1, 0.4*cm))

    forecast = report.get("forecast", [])
    if forecast:
        elements.append(Paragraph("Forecast — First 7 Days", styles["h2"]))
        rows = [[
            str(f.get("date",""))[:10],
            str(round(f.get("forecast",    0), 2)),
            str(round(f.get("lower_bound", 0), 2)),
            str(round(f.get("upper_bound", 0), 2)),
        ] for f in forecast[:7]]
        elements.append(_data_table(["Date","Forecast","Lower (95%)","Upper (95%)"], rows))
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 5: Regression ─────────────────────────────
def _section_regression(report, styles):
    if not report:
        return []
    elements = [_section_header("05", "Linear Regression Analysis", styles)]

    m = report.get("metrics", {})
    metrics = [
        ("Target Column", report.get("target_column", "N/A")),
        ("R² Score",      round(m.get("r2",   0), 4)),
        ("MAE",           round(m.get("mae",  0), 2)),
        ("RMSE",          round(m.get("rmse", 0), 2)),
        ("Train Size",    f"{report.get('train_size', 'N/A'):,}" if isinstance(report.get('train_size'), int) else "N/A"),
    ]
    elements.append(_metric_cards(metrics, styles))
    elements.append(Spacer(1, 0.4*cm))

    features = report.get("feature_importance", [])
    if features:
        elements.append(Paragraph("Feature Importance (Coefficients)", styles["h2"]))
        rows = [[f.get("feature",""), str(round(f.get("coefficient",0), 4))]
                for f in features[:8]]
        elements.append(_data_table(["Feature","Coefficient"], rows,
            [CONTENT_W * 0.6, CONTENT_W * 0.4]))

    interp = report.get("interpretation")
    if interp:
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(f"Interpretation: {interp}", styles["muted"]))
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 6: Apriori ────────────────────────────────
def _section_apriori(report, styles):
    if not report:
        return []
    elements = [_section_header("06", "Association Rules (Apriori)", styles)]

    s = report.get("summary", {})
    rules = report.get("top_rules", [])
    max_conf = s.get("max_confidence") or (rules[0].get("confidence") if rules else 0)
    max_lift = s.get("max_lift") or (rules[0].get("lift") if rules else 0)
    max_sup  = s.get("max_support") or (rules[0].get("support") if rules else 0)

    metrics = [
        ("Total Rules",    report.get("total_rules_found", len(rules))),
        ("Max Confidence", f"{round((max_conf or 0)*100,1)}%"),
        ("Max Lift",       round(max_lift or 0, 2)),
        ("Max Support",    f"{round((max_sup or 0)*100, 2)}%"),
    ]
    elements.append(_metric_cards(metrics, styles))
    elements.append(Spacer(1, 0.4*cm))

    if rules:
        elements.append(Paragraph("Top Rules in Plain English", styles["h2"]))
        for i, rule in enumerate(rules[:5], 1):
            eng = rule.get("english","")
            if eng:
                elements.append(Paragraph(f"{i}.  {eng}", styles["rule_text"]))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("Rules Table", styles["h2"]))
        rows = [[
            str(rule.get("antecedents",""))[:30],
            str(rule.get("consequents",""))[:30],
            f"{round(rule.get('confidence',0)*100,1)}%",
            str(round(rule.get("lift",0),2)),
        ] for rule in rules[:8]]
        elements.append(_data_table(
            ["If Bought","Then Bought","Confidence","Lift"], rows,
            [CONTENT_W*0.35, CONTENT_W*0.35, CONTENT_W*0.15, CONTENT_W*0.15]))
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 7: Anomaly ────────────────────────────────
def _section_anomaly(report, styles):
    if not report:
        return []
    elements = [_section_header("07", "Anomaly Detection (Isolation Forest)", styles)]

    summ = report.get("summary", {})
    metrics = [
        ("Total Rows",      f"{report.get('total_rows', 0):,}"),
        ("Anomalies Found", f"{report.get('total_anomalies', 0):,}"),
        ("Anomaly %",       f"{report.get('anomaly_pct', 0)}%"),
        ("High Severity",   summ.get("high_severity",   0)),
        ("Med Severity",    summ.get("medium_severity", 0)),
    ]
    elements.append(_metric_cards(metrics, styles))
    elements.append(Spacer(1, 0.4*cm))

    top = report.get("top_anomalies", [])
    if top:
        elements.append(Paragraph("Top Anomalies Detected", styles["h2"]))
        for i, a in enumerate(top[:6], 1):
            sev = a.get("severity","")
            sev_color = C_DANGER if sev=="High" else C_WARNING if sev=="Medium" else C_MUTED
            elements.append(Paragraph(
                f"<b>#{i} — Row {a.get(chr(39)+'row_index'+chr(39),'N/A')} [{sev}]</b>",
                styles["body"]))
            elements.append(Paragraph(a.get("explanation",""), styles["muted"]))
            elements.append(_thin_divider())
    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Section 8: AI Recommendations ────────────────────
def _section_ai(report, styles):
    if not report:
        return []
    elements = [_section_header("08", "AI-Powered Recommendations", styles)]

    recs = report.get("recommendations", {})
    if not recs:
        return elements

    overall = recs.get("overall_health","")
    if overall:
        box = Table([[Paragraph(overall, ParagraphStyle("ob",
            fontName="Helvetica", fontSize=10, textColor=C_TEXT, leading=16))]],
            colWidths=[CONTENT_W])
        box.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_ACCENT_BG),
            ("BOX",           (0,0),(-1,-1), 1, C_PRIMARY),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ]))
        elements.append(box)
        elements.append(Spacer(1, 0.3*cm))

    priority_colors = {
        "priority_1": C_DANGER,
        "priority_2": C_WARNING,
        "priority_3": C_SUCCESS,
    }
    priority_labels = {
        "priority_1": "TODAY",
        "priority_2": "THIS WEEK",
        "priority_3": "THIS MONTH",
    }

    for key in ["priority_1","priority_2","priority_3"]:
        p = recs.get(key, {})
        if not p:
            continue
        color = priority_colors[key]
        label = priority_labels[key]
        pbox = Table([
            [Paragraph(label, ParagraphStyle("pl",
                fontName="Helvetica-Bold", fontSize=9,
                textColor=C_WHITE, alignment=TA_LEFT)),
             Paragraph(p.get("title",""), ParagraphStyle("pt",
                fontName="Helvetica-Bold", fontSize=9,
                textColor=C_WHITE, alignment=TA_RIGHT))],
            [Paragraph(p.get("action",""), ParagraphStyle("pa",
                fontName="Helvetica", fontSize=10,
                textColor=C_TEXT, leading=15, colSpan=2)), Paragraph("","body")],
            [Paragraph(f"Expected Impact: {p.get('expected_impact','')}", ParagraphStyle("pi",
                fontName="Helvetica-Oblique", fontSize=9,
                textColor=C_MUTED, colSpan=2)), Paragraph("","body")],
        ], colWidths=[CONTENT_W*0.3, CONTENT_W*0.7])
        pbox.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  color),
            ("BACKGROUND",    (0,1),(-1,-1), C_LIGHT),
            ("BOX",           (0,0),(-1,-1), 1, color),
            ("SPAN",          (0,1),(-1,1)),
            ("SPAN",          (0,2),(-1,2)),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ]))
        elements.append(pbox)
        elements.append(Spacer(1, 0.25*cm))

    biggest = recs.get("biggest_opportunity","")
    if biggest:
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph("Biggest Opportunity", styles["h2"]))
        elements.append(Paragraph(biggest, styles["body"]))

    elements.append(Spacer(1, 0.5*cm))
    return elements

# ── Main Entry Point ──────────────────────────────────
def generate_pdf(dataset_id: str) -> Path:
    out_path = export_pdf_path(dataset_id)
    base = out_path.parent.parent / "processed"

    def load(name):
        return _load(base / f"{dataset_id}__{name}.json")

    cleaning   = load("cleaning_report")
    eda        = load("eda_report")
    kmeans     = load("kmeans_report")
    arima      = load("arima_report")
    regression = load("regression_report")
    apriori    = load("apriori_report")
    anomaly    = load("anomaly_report")
    ai         = load("ai_report")

    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm,  bottomMargin=1.5*cm,
    )

    styles   = _styles()
    elements = []
    elements += _cover(dataset_id, styles)
    elements += _section_data_quality(cleaning,   styles)
    elements += _section_eda(eda,                 styles)
    elements += _section_clustering(kmeans,        styles)
    elements += _section_forecasting(arima,        styles)
    elements += _section_regression(regression,    styles)
    elements += _section_apriori(apriori,          styles)
    elements += _section_anomaly(anomaly,          styles)
    elements += _section_ai(ai,                    styles)

    doc.build(elements)
    return out_path
