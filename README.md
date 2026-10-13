# 🌾 Weather-Based Farm Machinery Planner

> **S.Y. B.Tech — Python Programming Laboratory Capstone Project**  
> **Phase 1 — Intermediate Submission (50–60% Completion)**  
> *Domain:* Agricultural Mechanization & Farm Productivity  
> *Target Framework:* Streamlit & Scientific Python Stack  
> *Team Size:* 3 Members

---

## 1. Project Overview & Problem Statement
Agricultural mechanization is a core driver of modern farm productivity across India. However, the operational scheduling and efficiency of critical farm equipment—including tractors, seed drills, boom sprayers, and combine harvesters—are heavily vulnerable to adverse weather, particularly unseasonal and heavy precipitation. 

Rainfall creates saturated field soils, leading to excessive tire slippage, machinery immobilization, soil compaction, and chemical run-off. 

The **Weather-Based Farm Machinery Planner** is a beginner-friendly Python data analytics dashboard designed to help agricultural supervisors, custom hiring centers, and farmers analyze historical weather patterns, track machinery operational delays, and lay the foundation for predictive weather-based machinery scheduling.

This **Phase 1 intermediate submission** represents a **50–60% completion milestone**, delivering a functional, robust foundation for data ingestion, cleaning, descriptive statistical analytics, and agricultural visualizations, while mapping the architectural blueprint for advanced inferential modeling and forecast planning in Phase 2.

---

## 2. Team Code Division & Viva Preparation (3 Members)

To ensure each team member can independently present and defend their individual contribution during evaluation, the codebase is cleanly modularized into 3 distinct parts:

```text
d:\weather_farm_planner\
├── data_pipeline.py     <-- PART 1: Member 1 (Data Ingestion & Cleaning)
├── analytics.py         <-- PART 2: Member 2 (Statistical Analytics & Visualization)
├── app.py               <-- PART 3: Member 3 (Streamlit UI & System Integration)
├── requirements.txt
├── README.md
└── data/
    ├── machinery_operations.csv
    └── sample_weather.csv
```

---

### 👨‍💻 Member 1: Data Ingestion & Data Cleaning Pipeline
- **Primary Source File:** [`data_pipeline.py`](file:///d:/weather_farm_planner/data_pipeline.py)
- **Key Functions Owned:**
  - `fetch_weather_data(latitude, longitude, start_date, end_date)`: Connects to the Open-Meteo Historical Archive API using `requests`, handles HTTP errors and network timeouts, and caches responses with `@st.cache_data`.
  - `load_sample_weather_data(location_name)`: Provides offline demonstration fallback from [`data/sample_weather.csv`](file:///d:/weather_farm_planner/data/sample_weather.csv) so the app never crashes during offline evaluation.
  - `load_machinery_data(uploaded_file)`: Ingests [`data/machinery_operations.csv`](file:///d:/weather_farm_planner/data/machinery_operations.csv) or handles user-uploaded custom CSVs with column validation.
  - `clean_data(df, dataset_type)`: Performs datetime standardization (`pd.to_datetime`), numeric type coercion (`pd.to_numeric`), duplicate removal (`drop_duplicates`), negative value clipping/checks, binary normalization of the `delayed` column (`{0, 1}`), and generates a structured Data Quality Report dictionary.

#### 💡 Member 1 Viva Questions & Answers:
* **Q: How does `fetch_weather_data` handle internet failures?**  
  *Ans:* It wraps the REST call in a `try-except` catching `requests.exceptions.Timeout` and `ConnectionError`. If an error occurs, it returns `(None, error_message)` instead of crashing, allowing Member 3's UI to offer the offline sample dataset fallback.
* **Q: Why don't you fill missing rainfall values with zero in `clean_data`?**  
  *Ans:* Silently replacing missing values with zero distorts meteorological reality; zero rainfall means a dry day, whereas a missing value means an unrecorded observation. We identify and report missing entries explicitly.
* **Q: What data validation checks do you perform on machinery records?**  
  *Ans:* We verify that working hours are non-negative, drop duplicate entries, ensure date parsing succeeds, and ensure the `delayed` indicator is strictly binary (`0` or `1`).

---

### 👨‍💻 Member 2: Statistical Analytics & Data Visualization Engine
- **Primary Source File:** [`analytics.py`](file:///d:/weather_farm_planner/analytics.py)
- **Key Functions Owned:**
  - `calculate_weather_statistics(weather_df, rainy_threshold=0.0)`: Computes mean, median, maximum, standard deviation ($\sigma$), cumulative rainfall, and rainy days count & percentage.
  - `calculate_delay_statistics(machinery_df)`: Computes total operations, delayed operations, delay rate percentage, average planned hours, average actual hours, and total recorded hours lost ($\sum \max(0, \text{actual} - \text{planned})$).
  - `create_basic_weather_charts(weather_df, rainy_threshold=0.0)`: Generates 3 Matplotlib & Seaborn figures with titles, labeled axes, units, and insight notes:
    - *Chart 1:* Daily Rainfall Timeline (Line Chart with threshold).
    - *Chart 2:* Monthly Total Precipitation (Bar Chart with seasonal totals).
    - *Chart 3:* Distribution of Daily Precipitation (Histogram with Seaborn KDE).

#### 💡 Member 2 Viva Questions & Answers:
* **Q: How is the machinery delay rate calculated, and can it be calculated from weather data alone?**  
  *Ans:* No, the delay rate must be calculated strictly from machinery logs using $R_{\text{delay}} = \frac{\text{delayed operations}}{\text{total operations}} \times 100\%$. Weather alone cannot determine whether a machine was delayed.
* **Q: What formula did you use for "Hours Lost"?**  
  *Ans:* $H_{\text{lost}} = \sum \max(0, \text{actual\_hours} - \text{planned\_hours})$. We take only positive differences where the actual duration exceeded the planned schedule.
* **Q: What insight does the histogram with KDE reveal in Chart 3?**  
  *Ans:* Daily precipitation is heavily right-skewed; most days record zero or light rainfall, while a few intense monsoon cloudbursts make up the long positive tail.

---

### 👨‍💻 Member 3: Streamlit UI, System Integration & Planning Blueprint
- **Primary Source File:** [`app.py`](file:///d:/weather_farm_planner/app.py)
- **Key Functions & Sections Owned:**
  - `st.set_page_config` and agricultural green/white/grey CSS design system.
  - Sidebar layout: district selector (**Pune**, **Nashik**, **Thane**), date picker, operation filter, data source toggle, and custom CSV uploader.
  - Orchestrating Member 1's `data_pipeline.py` and Member 2's `analytics.py`.
  - **Tab 1: Dashboard Overview:** 4 summary metric cards, automated dynamic narrative summary, and Member 1's Data Quality Report expander.
  - **Tab 2: Historical Analysis UI:** Layout of Member 2's descriptive stats and rendering of the 3 Matplotlib/Seaborn charts.
  - **Tab 3: Weather-Based Planning UI (Phase 2 Preview):** Architectural blueprint of the upcoming 7-day forecast decision engine, operation guidelines profile, decision indicators matrix, and agronomic disclaimers.

#### 💡 Member 3 Viva Questions & Answers:
* **Q: Why was Streamlit selected over Django, Flask, or React?**  
  *Ans:* Streamlit allows rapid prototyping of pure Python data science apps. It natively binds to Pandas DataFrames and Matplotlib figures without needing a separate JavaScript frontend, database, or API layer.
* **Q: Why are correlation and live forecast planning shown as Phase 2 previews in Tab 2 and Tab 3?**  
  *Ans:* In this Phase 1 (50–60%) milestone, our goal was to build a clean, validated baseline with descriptive statistics and data cleaning. Rather than fabricating fake forecasts or fake p-values, we preserved the 3-tab layout and provided an architectural roadmap for Phase 2.
* **Q: What agronomic limitations are built into the planning system?**  
  *Ans:* Rainfall forecasts are planning heuristics, not direct soil safety measurements. Rainfall alone does not measure soil cone index (bearing strength) or root-zone saturation; operators must still physically inspect field trafficability.

---

## 3. Technology Stack & Dependencies

```text
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.8.0
seaborn>=0.13.0
requests>=2.31.0
```

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
- **Hours Lost ($H_{\text{lost}}$):**
  $$H_{\text{lost}} = \sum \max(0, \text{actual\_hours} - \text{planned\_hours})$$

---

## 6. Installation & Execution Guide

### Step-by-Step Instructions (Windows PowerShell)

```powershell
# 1. Navigate to the project root directory
cd d:\weather_farm_planner

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit application
streamlit run app.py
```

The application will launch in your browser at:  
`http://localhost:8501`

---

## 7. 🗺️ Phase 2 Roadmap (Deferred Advanced Features)

| Feature / Module | Purpose in Phase 2 | Planned Implementation |
| :--- | :--- | :--- |
| **Merged Weather-Delay Cross Analysis** | Quantify delay rates on rainy vs. non-rainy operation days | Pandas merged cross-tabulation |
| **Statistical Correlation Modeling** | Measure linear and monotonic associations between rainfall and hours lost | SciPy `stats.pearsonr` and `stats.spearmanr` |
| **Inferential Hypothesis Testing** | Test whether weather significantly impacts machinery delay distributions | SciPy `stats.mannwhitneyu` ($p$-value evaluation) |
| **Delay Scatter & Trendline Plot** | Visualize relationship between rainfall intensity and lost operating hours | Seaborn regression scatter plot |
| **7-Day Live Weather Forecast** | Ingest numerical precipitation forecasts and probabilities | Open-Meteo Forecast API client |
| **Dynamic Operational Planning Matrix** | Evaluate operation-specific rainfall tolerance heuristics | Interactive heuristic risk evaluation engine |

---

## 8. 🤝 GitHub Collaboration Workflow (For Team Members)

### Step 1: Clone the Repository to Your Local Machine
Each teammate runs:
```bash
git clone https://github.com/yashp82/weather_farm_planner.git
cd weather_farm_planner
```

### Step 2: Set Up Environment & Install Dependencies
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Edit Your Assigned File
- **Member 1:** Edit `data_pipeline.py` (API data ingestion, cleaning rules).
- **Member 2:** Edit `analytics.py` (Descriptive statistics formulas, Matplotlib/Seaborn charts).
- **Member 3:** Edit `app.py` (Streamlit dashboard UI, layouts, tabs).

### Step 4: Push Changes Back to GitHub
```bash
git pull origin main
git add .
git commit -m "Updated <your module name> feature"
git push origin main
```

