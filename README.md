# 🌾 Weather-Based Farm Machinery Planner

> **S.Y. B.Tech — Python Programming Laboratory Capstone Project**  
> **Phase 1 — Intermediate Submission (50–60% Completion)**  
> *Domain:* Agricultural Mechanization & Farm Productivity  
> *Target Framework:* Streamlit & Scientific Python Stack

---

## 1. Project Overview & Problem Statement
Agricultural mechanization is a core driver of modern farm productivity across India. However, the operational scheduling and efficiency of critical farm equipment—including tractors, seed drills, boom sprayers, and combine harvesters—are heavily vulnerable to adverse weather, particularly unseasonal and heavy precipitation. 

Rainfall creates saturated field soils, leading to excessive tire slippage, machinery immobilization, soil compaction, and chemical run-off. 

The **Weather-Based Farm Machinery Planner** is a beginner-friendly Python data analytics dashboard designed to help agricultural supervisors, custom hiring centers, and farmers analyze historical weather patterns, track machinery operational delays, and lay the foundation for predictive weather-based machinery scheduling.

This **Phase 1 intermediate submission** represents a **50–60% completion milestone**, delivering a functional, robust foundation for data ingestion, cleaning, descriptive statistical analytics, and agricultural visualizations, while mapping the architectural blueprint for advanced inferential modeling and forecast planning in Phase 2.

---

## 2. Phase 1 Implemented Features (Current Version)

### A. Interactive Streamlit Dashboard
- **Agricultural Theme:** Styled with an agricultural green, white, and soft-grey visual design.
- **District Selection:** Supports Maharashtra agricultural hubs (**Pune**, **Nashik**, and **Thane**) with latitude and longitude coordinates.
- **Date Range Selector:** Configurable historical date range (defaulting to the complete 2024 calendar year).
- **Farming Operation Filter:** Supports major mechanized operations (**Ploughing**, **Sowing**, **Spraying**, **Harvesting**).
- **Four Core Summary Metric Cards:**
  1. *Total Weather Records* (days loaded in observation window).
  2. *Average Daily Rainfall* (mm).
  3. *Number of Rainy Days* (days with precipitation $> 0.0\text{ mm}$, including percentage).
  4. *Machinery Operation Delay Rate* (calculated **strictly** from machinery operation records, displaying "Not available" if logs are absent).
- **Automated Narrative Summary:** Dynamically generates text describing rainfall patterns and recorded machinery delays.

### B. Automated Historical Weather Data Ingestion
- **Live Open-Meteo Archive API:** Fetches daily date, precipitation sum (mm), maximum temperature (°C), and mean relative humidity (%).
- **Resilient Error Handling:** Gracefully catches connection timeouts, API errors, and invalid date responses.
- **Offline Demonstration Fallback:** One-click fallback button loads bundled demonstration weather records when offline or during connectivity disruptions.
- **Cached Requests:** Employs Streamlit `@st.cache_data` caching to prevent redundant API queries.

### C. Data Cleaning & Validation Pipeline (`clean_data()`)
- **Datetime Parsing:** Automatically standardizes date strings using `pd.to_datetime()`.
- **Numeric Coercion:** Coerces numeric attributes via `pd.to_numeric()`.
- **Missing Value Detection:** Accurately identifies missing observations without silently filling values with zero.
- **Duplicate Removal:** Identifies and drops exact duplicate records.
- **Range & Value Validation:** Verifies non-negative rainfall and working hours, and normalizes delay indicators strictly to binary values (`0` and `1`).
- **Data Quality Report:** Displays a structured expander in the UI summarizing initial rows, final rows, missing values, duplicates removed, and anomalies handled.

### D. Descriptive Statistical Analysis (Pandas & NumPy)
- **Weather Statistics:** Mean daily rainfall, median daily rainfall, maximum daily rainfall, standard deviation of rainfall ($\sigma$), cumulative rainfall, and rainy days count & percentage.
- **Machinery Statistics:** Total recorded operations, delayed operations count, delay rate percentage, average planned hours, average actual hours, and total recorded hours lost.

### E. Statistical Data Visualizations (Matplotlib & Seaborn)
1. **Daily Rainfall Timeline (Line Chart):** Chronological rainfall distribution with rainy day threshold line.
2. **Monthly Precipitation Totals (Bar Chart):** Seasonal rainfall totals across calendar months.
3. **Daily Rainfall Distribution (Histogram with KDE):** Visualizes skewness and frequency of rainfall events.
*(Each chart includes descriptive titles, labeled axes, appropriate units, and explanatory insight notes).*

### F. Machinery Operations Dataset & Custom Upload
- Ingests `data/machinery_operations.csv` across operations, machine types, and locations.
- Supports custom user CSV uploads via `st.file_uploader` with automated column validation.

---

## 3. Technology Stack & Dependencies (Phase 1)

| Library | Version | Role in Phase 1 |
| :--- | :--- | :--- |
| **Streamlit** | $\ge 1.30.0$ | Interactive dashboard interface, sidebar controls, metric cards, and layout. |
| **Pandas** | $\ge 2.0.0$ | Data ingestion, tabular cleaning, date parsing, aggregations, and filtering. |
| **NumPy** | $\ge 1.24.0$ | Vectorized numeric operations, hours lost calculation, and clipping. |
| **Matplotlib** | $\ge 3.8.0$ | Primary canvas, figure layouts, and bar/line charts. |
| **Seaborn** | $\ge 0.13.0$ | Statistical distributions and histogram KDE estimation. |
| **Requests** | $\ge 2.31.0$ | HTTP REST client for Open-Meteo Historical Archive API. |

---

## 4. Dataset Transparency & Data Sources

### A. Meteorological Data
- **Live Provider:** [Open-Meteo Historical Weather Archive API](https://archive-api.open-meteo.com/v1/archive) (Non-commercial open-access).
- **Fallback Demonstration Dataset (`data/sample_weather.csv`):**  
  *Explicit Academic Label:* **Synthetic Demonstration Data** (1,098 rows spanning 2024 for Pune, Nashik, and Thane). Sourced to model typical Maharashtra monsoon distributions for reliable offline academic demonstration.

### B. Machinery Operations Records (`data/machinery_operations.csv`)
- **Structure:** 298 records across Kharif and Rabi operational periods.
- **Columns:** `date`, `location`, `operation`, `machine_type`, `planned_hours`, `actual_hours`, `delayed`, `delay_reason`.
- *Explicit Academic Label:* **Synthetic Demonstration Data**. Generated to simulate realistic custom hiring center operations; it does not represent real-world private farm surveys.

---

## 5. Statistical Methods & Formulas (Implemented in Phase 1)

### 1. Weather Descriptive Statistics
- **Mean Daily Rainfall ($\bar{x}$):**
  $$\bar{x} = \frac{1}{N}\sum_{i=1}^N x_i$$
- **Sample Standard Deviation ($s$):**
  $$s = \sqrt{\frac{1}{N-1}\sum_{i=1}^N (x_i - \bar{x})^2}$$
- **Rainy Day Definition:** Any day with daily precipitation $> 0.0\text{ mm}$:
  $$\text{Rainy Days} = \sum_{i=1}^N \mathbb{I}(x_i > 0.0)$$

### 2. Machinery Delay Metrics
- **Delay Rate ($R_{\text{delay}}$):**
  $$R_{\text{delay}} = \left( \frac{\sum \text{delayed operations}}{\text{total logged operations}} \right) \times 100\%$$
  *(Note: Computed strictly from machinery operation records).*
- **Hours Lost ($H_{\text{lost}}$):**
  $$H_{\text{lost}} = \sum \max(0, \text{actual\_hours} - \text{planned\_hours})$$

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10+ installed on your computer.
- Windows PowerShell or Command Prompt.

### Step-by-Step Instructions (Windows PowerShell)

```powershell
# 1. Navigate to the project root directory
cd d:\weather_farm_planner

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install Phase 1 dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit application
streamlit run app.py
```

The application will launch in your browser at:  
`http://localhost:8501`

---

## 7. Current System Limitations (Phase 1)
1. **Descriptive Scope Only:** Phase 1 focuses strictly on baseline descriptive statistics and data cleaning. It does not perform inferential hypothesis testing or multi-variable regression.
2. **Historical Focus:** Phase 1 analyzes historical weather archives; upcoming 7-day numerical forecast ingestion is scheduled for Phase 2.
3. **No Direct Soil Sensing:** Rainfall serves as an observational proxy. The system does not measure direct soil cone bearing capacity or volumetric soil water content.

---

## 8. 🗺️ Phase 2 Roadmap (Deferred Advanced Features)

The following advanced capabilities are scheduled for the **Phase 2 final submission**:

| Feature / Module | Purpose in Phase 2 | Planned Implementation |
| :--- | :--- | :--- |
| **Merged Weather-Delay Cross Analysis** | Quantify delay rates on rainy vs. non-rainy operation days | Pandas merged cross-tabulation |
| **Statistical Correlation Modeling** | Measure linear and monotonic associations between rainfall and hours lost | SciPy `stats.pearsonr` and `stats.spearmanr` |
| **Inferential Hypothesis Testing** | Test whether weather significantly impacts machinery delay distributions | SciPy `stats.mannwhitneyu` ($p$-value evaluation) |
| **Delay Scatter & Trendline Plot** | Visualize relationship between rainfall intensity and lost operating hours | Seaborn regression scatter plot |
| **7-Day Live Weather Forecast** | Ingest numerical precipitation forecasts and probabilities | Open-Meteo Forecast API client |
| **Dynamic Operational Planning Matrix** | Evaluate operation-specific rainfall tolerance heuristics | Interactive heuristic risk evaluation engine |

---

## 9. Viva Voce Key Questions (Phase 1 Evaluation)

**Q1: What is the primary milestone achieved in Phase 1?**  
*Ans:* Phase 1 establishes the end-to-end data pipeline: automated API weather retrieval, robust cleaning via `clean_data()`, calculation of descriptive weather and machinery delay statistics, and generation of statistical charts using Matplotlib and Seaborn.

**Q2: How does the application handle missing data or offline environments?**  
*Ans:* The `clean_data()` function identifies missing values without silently zero-filling them. For offline environments or API failures, a fallback toggle loads the bundled synthetic dataset (`data/sample_weather.csv`), ensuring zero application crashes.

**Q3: How is the machinery delay rate calculated?**  
*Ans:* The delay rate is calculated strictly from valid machinery operation logs ($\frac{\text{delayed operations}}{\text{total operations}} \times 100\%$). It is never fabricated or computed solely from weather records.

**Q4: Why are correlation and hypothesis testing deferred to Phase 2?**  
*Ans:* To maintain software engineering best practices. Phase 1 focuses on data integrity, descriptive baselines, and data validation. Inferential modeling and predictive planning are introduced in Phase 2 once the foundation is proven sound.
