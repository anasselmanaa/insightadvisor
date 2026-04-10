<div align="center">

# InsightAdvisor
### AI-Powered Business Analytics Platform for SMEs

*From raw CSV to board-ready presentation in under 5 minutes*

[![Live Demo](https://img.shields.io/badge/Live_Demo-insightadvisor.vercel.app-6366f1?style=for-the-badge)](https://insightadvisor.vercel.app)
[![API Docs](https://img.shields.io/badge/API_Docs-onrender.com/docs-22d3ee?style=for-the-badge)](https://insightadvisor-api.onrender.com/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python_3.10-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

> **InsightAdvisor** is an autonomous, end-to-end business intelligence platform combining explainable ML, causal AI, LLM-powered recommendations, and automated reporting — designed for SMEs who cannot afford Tableau or Power BI.

</div>

---

## Why InsightAdvisor?

| Problem | Solution |
|---------|----------|
| Tableau costs $70,000/year | Completely free and open-source |
| Requires data science expertise | Upload CSV and get insights in 5 minutes |
| Separate tools for each analysis | 6 ML models + AI in one platform |
| Technical jargon in results | Plain English explanations everywhere |
| No actionable next steps | AI generates prioritized action plan |
| Manual report creation | One-click PDF + PowerPoint + Excel export |

---

## Live Demo

| Service | URL |
|---------|-----|
| Frontend | https://insightadvisor.vercel.app |
| Backend API | https://insightadvisor-api.onrender.com |
| API Documentation | https://insightadvisor-api.onrender.com/docs |

> The backend runs on Render free tier and may take 30-60 seconds to wake up after inactivity.

---

## Key Features

### 6 Machine Learning Models

| Model | Purpose | Metrics |
|-------|---------|---------|
| KMeans + RFM | Customer segmentation | Silhouette, Davies-Bouldin |
| ARIMA | Sales forecasting | RMSE, MAPE, Confidence Intervals |
| Linear Regression | Revenue prediction | R2, MAE, RMSE |
| Apriori | Market basket analysis | Support, Confidence, Lift |
| Isolation Forest | Anomaly detection | Anomaly Score, Severity |
| SHAP | Model explainability | Feature Importance per Cluster |

### AI Layer
- **AI Copilot** powered by Groq (Llama 3.3 70B) with OpenRouter fallback
- **Prescriptive Analytics** — Today / This Week / This Month action plans
- **Natural Language Queries** — Ask anything about your data in plain English
- **Causal AI** — DoWhy causal inference between business variables
- **Revenue Impact** — Expected dollar impact per recommendation

### Smart Features
- Auto-detect dataset type (retail, stock, or generic)
- Context-aware UI — disables incompatible features automatically
- Data Quality Score — 0 to 100 with detailed cleaning report
- Multi-language support — English, French, Chinese

---

## Model Performance

Evaluated on the UCI Online Retail Dataset (200,000 rows):

| Model | Metric | Value | Interpretation |
|-------|--------|-------|----------------|
| Data Cleaning | Quality Score | 96/100 | Excellent |
| KMeans | Silhouette Score | 0.6201 | Good separation |
| KMeans | Davies-Bouldin | 0.3836 | Excellent |
| ARIMA | RMSE | 386.43 | Acceptable |
| ARIMA | MAPE | 34.17% | Acceptable |
| Linear Regression | R2 Score | 0.6472 | Good |
| Linear Regression | MAE | 4.29 | Avg error $4.29 |
| Apriori | Max Lift | 16.00x | Excellent |
| Isolation Forest | Detection Rate | 5% | 2,073 anomalies |

---

## Tech Stack

**Backend:** FastAPI, Python 3.10, SQLite, SQLAlchemy, uvicorn

**ML Models:** scikit-learn, statsmodels, mlxtend, SHAP, DoWhy

**AI:** Groq API (Llama 3.3 70B), OpenRouter, yfinance

**Frontend:** React 18, Vite, TailwindCSS, Recharts, Framer Motion

**Export:** ReportLab (PDF), python-pptx, openpyxl

**Auth:** JWT, python-jose, passlib, bcrypt

**Deploy:** Vercel (frontend) + Render (backend)

---

## Quick Start

**Prerequisites:** Python 3.10+, Node.js 18+

**1. Clone and setup backend:**

    git clone https://github.com/anasselmanaa/insightadvisor.git
    cd insightadvisor
    pip install -r requirements.txt
    cp .env.example .env
    uvicorn backend_core.api:app --reload

**2. Setup frontend:**

    cd frontend
    npm install
    npm run dev

**3. Environment variables (.env):**

    GROQ_API_KEY=your_groq_api_key
    OPENROUTER_API_KEY=your_openrouter_api_key
    GEMINI_API_KEY=your_gemini_api_key
    SECRET_KEY=your_jwt_secret_key
    GROQ_MODEL=llama-3.3-70b-versatile

Get free API keys at [console.groq.com](https://console.groq.com) and [openrouter.ai](https://openrouter.ai)

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login and get JWT token |
| POST | /upload | Upload CSV or Excel file |
| GET | /eda/{id} | Exploratory data analysis |
| GET | /kmeans/{id}?k=4 | Customer clustering |
| GET | /arima/{id}?forecast_days=30 | Sales forecasting |
| GET | /regression/{id}?target=revenue | Linear regression |
| GET | /apriori/{id}?min_support=0.01 | Association rules |
| GET | /anomaly/{id}?contamination=0.05 | Anomaly detection |
| GET | /stock/{ticker} | Live stock market analysis |
| GET | /ai/recommendations/{id} | AI recommendations |
| GET | /ai/action-plan/{id} | Prioritized action plan |
| POST | /ai/query/{id} | Natural language query |
| GET | /export/pdf/{id} | Download PDF report |
| GET | /export/pptx/{id} | Download PowerPoint |
| GET | /export/cleaned/{id} | Download cleaned Excel |

---

## Project Structure

| File | Description |
|------|-------------|
| backend_core/api.py | FastAPI app + CORS + routers |
| backend_core/kmeans_service.py | KMeans + RFM + SHAP + auto-naming |
| backend_core/arima_service.py | ARIMA + confidence intervals + MAPE |
| backend_core/regression_service.py | Linear Regression + R2 + feature importance |
| backend_core/apriori_service.py | Apriori + English rule translation |
| backend_core/anomaly_service.py | Isolation Forest + plain English explanations |
| backend_core/stock_service.py | yfinance + ARIMA on stock data |
| backend_core/ai_service.py | Groq/OpenRouter LLM + action plans |
| backend_core/pdf_service.py | ReportLab PDF generation |
| backend_core/auth_service.py | JWT + bcrypt authentication |
| frontend/src/pages/Landing.jsx | Marketing landing page |
| frontend/src/pages/Upload.jsx | File upload + quality score |
| frontend/src/pages/Dashboard.jsx | EDA charts + summary stats |
| frontend/src/pages/Clustering.jsx | KMeans + radar charts + SHAP |
| frontend/src/pages/Forecasting.jsx | ARIMA + confidence bands |
| frontend/src/pages/AICopilot.jsx | LLM chat + action plan |

---

## Academic Context

| | |
|--|--|
| **University** | Sichuan University |
| **Degree** | Bachelor of Engineering - Software Engineering |
| **Author** | Anass Elmanaa |
| **Supervisor** | Prof. Li Xinsheng |
| **Year** | 2026 |
| **Thesis Title** | An End-to-End Analytics System for Business and Finance |
| **Dataset** | UCI Online Retail Dataset (1,067,372 transactions) |

---

## License

MIT License - see LICENSE file for details.

---

<div align="center">

Built with love by Anass Elmanaa

Sichuan University - Software Engineering - Class of 2026

anasselmanaa7@gmail.com

Star this repo if you find it useful!

</div>
