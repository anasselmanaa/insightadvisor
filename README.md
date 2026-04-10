<div align="center">

<img src="https://img.shields.io/badge/InsightAdvisor-AI%20Analytics-6366f1?style=for-the-badge&logoColor=white" alt="InsightAdvisor"/>

# InsightAdvisor
### The Open-Source Business Intelligence Platform for SMEs

*From raw CSV to board-ready presentation in under 5 minutes*

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-insightadvisor.vercel.app-6366f1?style=for-the-badge)](https://insightadvisor.vercel.app)
[![API Docs](https://img.shields.io/badge/📖%20API%20Docs-onrender.com-22d3ee?style=for-the-badge)](https://insightadvisor-api.onrender.com/docs)

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python_3.10-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

<br/>

> **InsightAdvisor** is an autonomous, end-to-end business intelligence platform that combines explainable machine learning, causal AI, LLM-powered prescriptive recommendations, and automated report generation — in a single open-source system designed specifically for small and medium enterprises who cannot afford Tableau or Power BI.

<br/>

</div>

---

## 📌 Table of Contents

- [Why InsightAdvisor?](#-why-insightadvisor)
- [Live Demo](#-live-demo)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Model Performance](#-model-performance)
- [System Architecture](#-system-architecture)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Academic Context](#-academic-context)
- [License](#-license)

---

## 💡 Why InsightAdvisor?

| Problem | InsightAdvisor Solution |
|---------|------------------------|
| Tableau costs $70,000/year | Completely free and open-source |
| Requires data science expertise | Upload CSV → get insights in 5 minutes |
| Separate tools for each analysis | 6 ML models + AI in one platform |
| Technical jargon in results | Plain English explanations everywhere |
| No actionable next steps | AI generates prioritized action plan |
| Manual report creation | One-click PDF + PowerPoint + Excel export |

---

## 🌐 Live Demo

| Service | URL | Status |
|---------|-----|--------|
| Frontend | https://insightadvisor.vercel.app | ✅ Live |
| Backend API | https://insightadvisor-api.onrender.com | ✅ Live |
| API Documentation | https://insightadvisor-api.onrender.com/docs | ✅ Live |

> **Note:** The backend runs on Render's free tier and may take 30-60 seconds to wake up after inactivity. Visit the backend URL once before using the app.

---

## ✨ Key Features

### 🤖 6 Machine Learning Models
| Model | Purpose | Key Metrics |
|-------|---------|-------------|
| KMeans + RFM | Customer segmentation | Silhouette, Davies-Bouldin |
| ARIMA | Sales forecasting | RMSE, MAPE, Confidence Intervals |
| Linear Regression | Revenue prediction | R², MAE, RMSE |
| Apriori | Market basket analysis | Support, Confidence, Lift |
| Isolation Forest | Anomaly detection | Anomaly Score, Severity |
| SHAP | Model explainability | Feature Importance per Cluster |

### 🧠 AI Layer
- **AI Copilot** — Powered by Groq (Llama 3.3 70B) with OpenRouter fallback
- **Prescriptive Analytics** — Prioritized action plans: Today / This Week / This Month
- **Natural Language Queries** — Ask anything about your data in plain English
- **Causal AI** — DoWhy causal inference between business variables
- **Revenue Impact Estimation** — Expected $ impact for each recommendation

### 📊 Smart Analytics
- **Auto-detect dataset type** — Retail, stock, or generic data
- **Context-aware UI** — Automatically enables/disables features based on data
- **Data Quality Score** — 0-100 quality assessment with detailed report
- **Smart Fill Strategy** — Mean vs median based on skewness detection
- **IQR Outlier Detection** — Automatic outlier removal with report

### 📄 Export & Reporting
- **Professional PDF** — 8-section report with all analyses and AI recommendations
- **PowerPoint Slides** — 8 slides ready for board presentation
- **Excel Export** — Cleaned dataset + clustering results
- **Multi-language** — English, French, Chinese (ZH)

### 🔒 Security
- JWT authentication with encrypted passwords
- bcrypt password hashing
- Protected API endpoints
- Secure token management

---

## 🛠️ Tech Stack
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  React 18 + Vite + TailwindCSS + Recharts + Framer Motion  │
├─────────────────────────────────────────────────────────────┤
│                         BACKEND                             │
│           FastAPI + Python 3.10 + SQLAlchemy               │
├──────────────────┬──────────────────┬───────────────────────┤
│    ML MODELS     │     AI LAYER     │      EXPORT           │
│  scikit-learn    │  Groq API        │  ReportLab (PDF)      │
│  statsmodels     │  OpenRouter      │  python-pptx          │
│  mlxtend         │  DoWhy           │  openpyxl             │
│  SHAP            │  yfinance        │  SMTP Email           │
├──────────────────┴──────────────────┴───────────────────────┤
│                        DATABASE                             │
│                  SQLite + SQLAlchemy ORM                    │
├─────────────────────────────────────────────────────────────┤
│                      DEPLOYMENT                             │
│           Vercel (Frontend) + Render (Backend)              │
└─────────────────────────────────────────────────────────────┘
---

## 📈 Model Performance

Evaluated on the **UCI Online Retail Dataset** (200,000 rows sample from 1,067,372 transactions):

| Model | Metric | Value | Interpretation |
|-------|--------|-------|----------------|
| Data Cleaning | Quality Score | **96/100** | Excellent data quality |
| KMeans | Silhouette Score | **0.6201** | Good cluster separation |
| KMeans | Davies-Bouldin Index | **0.3836** | Excellent (lower = better) |
| ARIMA | RMSE | **386.43** | Acceptable for retail |
| ARIMA | MAPE | **34.17%** | Acceptable for volatile retail |
| Linear Regression | R² Score | **0.6472** | Good for retail data |
| Linear Regression | MAE | **4.29** | Average error of $4.29 |
| Apriori | Max Lift | **16.00x** | Excellent association strength |
| Isolation Forest | Detection Rate | **5%** | 2,073 anomalies detected |

---

## 🏗️ System Architecture
[User Browser]
│
▼
[React Frontend - Vercel]
│ HTTPS API calls
▼
[FastAPI Backend - Render]
│
├──► [Upload & Cleaning Module]
│         └── Quality Score + IQR Outlier Detection
│
├──► [EDA Module]
│         └── Correlation + Distributions + Top Categories
│
├──► [ML Models Layer]
│         ├── KMeans + RFM + SHAP
│         ├── ARIMA + Confidence Intervals
│         ├── Linear Regression + Feature Importance
│         ├── Apriori + English Rules
│         └── Isolation Forest + Explanations
│
├──► [AI Layer]
│         ├── Groq LLM (Primary)
│         ├── OpenRouter (Fallback)
│         └── DoWhy Causal Inference
│
├──► [Export Layer]
│         ├── ReportLab PDF
│         ├── python-pptx PowerPoint
│         └── openpyxl Excel
│
└──► [SQLite Database]
└── Users + Datasets + Analysis Results
---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/anasselmanaa/insightadvisor.git
cd insightadvisor
```

### 2. Backend setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your API keys

# Start the backend
uvicorn backend_core.api:app --reload
# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

### 4. Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_jwt_secret_key_here
GROQ_MODEL=llama-3.3-70b-versatile
OPENROUTER_MODEL=openai/gpt-oss-20b:free
```

> Get free API keys: [Groq](https://console.groq.com) | [OpenRouter](https://openrouter.ai)

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |

### Data Pipeline
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload CSV or Excel file |
| GET | `/eda/{dataset_id}` | Run exploratory analysis |

### ML Models
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/kmeans/{dataset_id}?k=4` | Customer clustering |
| GET | `/arima/{dataset_id}?forecast_days=30` | Sales forecasting |
| GET | `/regression/{dataset_id}?target=revenue` | Linear regression |
| GET | `/apriori/{dataset_id}?min_support=0.01` | Association rules |
| GET | `/anomaly/{dataset_id}?contamination=0.05` | Anomaly detection |
| GET | `/stock/{ticker}` | Live stock analysis |

### AI & Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ai/recommendations/{dataset_id}` | AI recommendations |
| GET | `/ai/action-plan/{dataset_id}` | Prioritized action plan |
| POST | `/ai/query/{dataset_id}` | Natural language query |
| GET | `/export/pdf/{dataset_id}` | Download PDF report |
| GET | `/export/pptx/{dataset_id}` | Download PowerPoint |
| GET | `/export/cleaned/{dataset_id}` | Download cleaned Excel |

---

## 📁 Project Structure
insightadvisor/
│
├── backend_core/
│   ├── api.py                    # FastAPI app + CORS + router registration
│   ├── cleaning.py               # Data cleaning + quality score
│   ├── eda.py                    # EDA + correlation + distributions
│   ├── storage.py                # File path management
│   ├── database.py               # SQLite + SQLAlchemy connection
│   ├── models.py                 # Database table definitions
│   │
│   ├── kmeans_service.py         # KMeans + RFM + SHAP + auto-naming
│   ├── arima_service.py          # ARIMA + confidence intervals + MAPE
│   ├── regression_service.py     # Linear Regression + R² + feature importance
│   ├── apriori_service.py        # Apriori + English rule translation
│   ├── anomaly_service.py        # Isolation Forest + plain English explanations
│   ├── stock_service.py          # yfinance + ARIMA on stock data
│   ├── causal_service.py         # DoWhy causal inference
│   ├── ai_service.py             # Groq/OpenRouter LLM + action plans
│   ├── pdf_service.py            # ReportLab PDF generation
│   ├── pptx_service.py           # python-pptx PowerPoint generation
│   └── auth_service.py           # JWT + bcrypt authentication
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Landing.jsx       # Marketing landing page
│       │   ├── Login.jsx         # Authentication
│       │   ├── Upload.jsx        # File upload + quality score
│       │   ├── Dashboard.jsx     # EDA charts + summary
│       │   ├── Clustering.jsx    # KMeans + radar charts + SHAP
│       │   ├── Forecasting.jsx   # ARIMA + confidence bands
│       │   ├── Regression.jsx    # Scatter plot + coefficients
│       │   ├── Apriori.jsx       # Association rules in English
│       │   ├── Anomaly.jsx       # Anomaly detection + severity
│       │   ├── Stock.jsx         # Live stock + forecast
│       │   ├── AICopilot.jsx     # LLM chat + action plan
│       │   └── Reports.jsx       # PDF/PPTX/Excel download
│       └── components/
│           └── Layout.jsx        # Sidebar + navigation
│
├── .python-version               # Python 3.10.18
├── requirements.txt              # Python dependencies
└── README.md                     # This file

---

## 🎓 Academic Context

This project was developed as a **graduation thesis** at Sichuan University (2026).

| | |
|--|--|
| **University** | Sichuan University (四川大学) |
| **Degree** | Bachelor of Engineering — Software Engineering |
| **Author** | Anass Elmanaa |
| **Supervisor** | Prof. Li Xinsheng |
| **Year** | 2026 |
| **Thesis Title** | "An End-to-End Analytics System for Business and Finance: Data Pipelines, Interactive Visualization, Predictive Modeling and Reporting" |
| **Dataset** | UCI Online Retail Dataset (1,067,372 transactions) |

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome. Feel free to check the [issues page](https://github.com/anasselmanaa/insightadvisor/issues).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Anass Elmanaa](https://github.com/anasselmanaa)**

*Sichuan University · Software Engineering · Class of 2026*

📧 anasselmanaa7@gmail.com

⭐ Star this repo if you find it useful!

</div>
