# 🌾 Weather-Based Farm Machinery Planner

> **S.Y. B.Tech — Python Programming Laboratory Capstone Project**  
> *Domain:* Agricultural Mechanization & Farm Productivity  
> *Target Framework:* Streamlit & Scientific Python Stack

---

## 1. Problem Statement & Project Overview
Farm mechanization plays a pivotal role in agricultural productivity across India. However, the deployment and operational scheduling of heavy farm equipment—such as tractors for ploughing, seed-cum-fertilizer drills, chemical sprayers, and combine harvesters—is acutely vulnerable to adverse meteorological conditions, primarily unseasonal or heavy precipitation. 

Rainfall creates saturated, waterlogged soil that leads to excessive tire slippage, severe subsoil compaction, machinery immobility, and washed-off chemical applications. 

The **Weather-Based Farm Machinery Planner** is a lightweight, beginner-friendly Python data analytics dashboard designed to:
1. Examine historical weather patterns alongside machinery operation logs.
2. Determine statistical delay rates and evaluate associations between daily precipitation and machinery scheduling disruptions.
3. Offer an accessible, heuristic-driven weather planning aid for upcoming 7-day farm operations.

---

## 2. Project Objectives
- **Data Engineering:** Retrieve daily meteorological data from the open-access Open-Meteo API (historical archive & upcoming forecast) and handle CSV-based operational logs.
- **Data Cleaning (`clean_data()`):** Robustly detect missing observations, eliminate duplicates, enforce valid non-negative ranges, and normalize binary classification indicators.
- **Statistical Analytics:** Compute descriptive statistics (mean, median, standard deviation, cumulative precipitation), calculate operational delay percentages and hours lost, quantify correlation (Pearson $r$ and Spearman $\rho$), and conduct non-parametric hypothesis testing (Mann-Whitney $U$ test).
- **Data Visualization:** Present publication-grade, agricultural-themed visual charts using Matplotlib and Seaborn.
- **Decision-Support Planning:** Implement operation-tailored heuristic thresholds to categorize upcoming days into *Lower weather concern*, *Caution*, and *Higher rainfall concern*.

---

## 3. Real-World Relevance
In semi-arid and monsoon-dependent farming regions of India (such as Maharashtra's Pune, Nashik, and Thane districts), custom hiring centers (CHCs) and smallholder farmer collectives must allocate costly machinery across tight temporal windows. An unpredicted 15 mm downpour can stall harvesting or ruin freshly applied foliar pesticides, inflicting substantial financial losses. This planner provides an intuitive, data-backed interface for farm supervisors and agricultural extension officers.

---

## 4. Software Architecture & Technology Stack

| Library | Version | Purpose in Project |
| :--- | :--- | :--- |
| **Streamlit** | $\ge 1.30.0$ | Interactive web dashboard, sidebar controls, metric cards, tabs, and layout. |
| **Pandas** | $\ge 2.0.0$ | Data ingestion, tabular cleaning, date parsing, aggregation, and table merging. |
| **NumPy** | $\ge 1.24.0$ | Vectorized numeric operations, hours lost calculation, and clipping. |
| **Matplotlib** | $\ge 3.8.0$ | Primary canvas and figure layouts for timeline, bar, and categorical plots. |
| **Seaborn** | $\ge 0.13.0$ | Statistical distributions, histogram KDE estimation, and regression scatter plots. |
| **SciPy (`scipy.stats`)** | $\ge 1.11.0$ | Statistical correlation coefficients and Mann-Whitney $U$ hypothesis testing. |
| **Requests** | $\ge 2.31.0$ | HTTP client for Open-Meteo REST APIs (Archive and Forecast endpoints). |

---

## 5. Dataset Descriptions & Data Transparency

### A. Meteorological Data (Open-Meteo API & `sample_weather.csv`)
- **Live Source:** [Open-Meteo Historical Archive API](https://archive-api.open-meteo.com/v1/archive) and [Forecast API](https://api.open-meteo.com/v1/forecast).
- **Variables Retrieved:** `date`, `precipitation_sum` (mm), `temperature_2m_max` (°C), `relative_humidity_2m_mean` (%), and `precipitation_probability_max` (%).
- **Fallback Sample Data (`data/sample_weather.csv`):** A bundled dataset of 1,098 daily records spanning 2024 for Pune, Nashik, and Thane.  
  *Explicit Academic Label:* **Synthetic Demonstration Data**. It reproduces realistic monsoon distributions (June–September) for offline demonstration and testing.

### B. Machinery Operations Log (`data/machinery_operations.csv`)
- **File Structure:** 298 records across Kharif and Rabi operational periods.
- **Columns:**
  - `date`: Operation date (`YYYY-MM-DD`).
  - `location`: District (`Pune`, `Nashik`, `Thane`).
  - `operation`: Farming task (`Ploughing`, `Sowing`, `Spraying`, `Harvesting`).
  - `machine_type`: Specific implement (`Tractor`, `Power Tiller`, `Seed Drill`, `Boom Sprayer`, `Combine Harvester`).
  - `planned_hours`: Scheduled shift duration in hours (e.g., $4.0 - 8.0$ hrs).
  - `actual_hours`: Actual logged duration in hours.
  - `delayed`: Binary indicator ($1 = \text{Delayed}, 0 = \text{On-Time}$).
  - `delay_reason`: Categorical root cause (`rain`, `wet soil`, `machine maintenance`, `labour shortage`, `other`, `none`).
- *Explicit Academic Label:* **Synthetic Demonstration Data**. This dataset is modeled for student academic inquiry and does not represent a survey of physical private farms.
- **Custom CSV Upload:** Users can upload custom machinery logs directly in the sidebar.

---

## 6. Statistical Methods & Formulas

### 1. Descriptive Weather Metrics
- **Mean Daily Precipitation ($\bar{x}$):**
  $$\bar{x} = \frac{1}{N}\sum_{i=1}^N x_i$$
- **Sample Standard Deviation ($s$):**
  $$s = \sqrt{\frac{1}{N-1}\sum_{i=1}^N (x_i - \bar{x})^2}$$
- **Rainy Day Definition:** Any day where $\text{precipitation\_sum} > \text{threshold}$ (default: $> 0.0\text{ mm}$, adjustable via UI).

### 2. Machinery Operational Delay Metrics
- **Delay Rate ($R_{\text{delay}}$):**
  $$R_{\text{delay}} = \left( \frac{\sum \text{delayed operations}}{\text{total logged operations}} \right) \times 100\%$$
  *(Note: Delay rate is computed strictly from machinery records, not estimated from weather records alone).*
- **Hours Lost ($H_{\text{lost}}$):**
  $$H_{\text{lost}} = \sum \max(0, \text{actual\_hours} - \text{planned\_hours})$$

### 3. Merged Association Analysis
- **Delay Rate on Rainy Days ($R_{\text{rainy}}$) vs. Non-Rainy Days ($R_{\text{dry}}$):**
  $$\Delta R = R_{\text{rainy}} - R_{\text{dry}}$$
- **Pearson Product-Moment Correlation ($r$):**
  $$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
- **Spearman Rank Correlation ($\rho$):**
  Monotonic association between ranked precipitation and ranked delay hours lost:
  $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$

### 4. Non-Parametric Hypothesis Testing (Mann-Whitney $U$ Test)
- **Null Hypothesis ($H_0$):** The distribution of lost machinery hours is identical across rainy and non-rainy operation days.
- **Alternative Hypothesis ($H_1$):** Machinery operations scheduled on rainy days incur significantly higher delay hours.
- **Decision Rule:** Reject $H_0$ if $p\text{-value} < \alpha = 0.05$.

---

## 7. Data Visualizations Included
1. **Daily Rainfall Timeline (Line Chart):** Tracks chronology of precipitation with threshold markers and fill areas.
2. **Monthly Precipitation Totals (Bar Chart):** Quantifies monsoon seasonality and peak precipitation months.
3. **Delay Rates Comparison (Bar Chart):** Visualizes the percentage disparity in delayed operations between rainy and dry days.
4. **Precipitation Distribution (Histogram with KDE):** Illustrates the positive skewness of daily rainfall events.
5. **Rainfall vs. Hours Lost (Regression Scatter Plot):** Plots operation-day rainfall against excess hours spent.

---

## 8. Weather-Based Planning Heuristics
The planning tab evaluates upcoming 7-day weather forecasts using operation-specific rules:

| Farming Operation | Recommended Max Rain | Rain Sensitivity Rationale |
| :--- | :---: | :--- |
| **Spraying** | $\le 1.0\text{ mm}$ | Chemical wash-off risk; requires dry foliage for $\ge 4\text{ hours}$. |
| **Harvesting** | $\le 2.0\text{ mm}$ | Standing water and wet straw clog combine harvesters; mold risk. |
| **Sowing** | $\le 8.0\text{ mm}$ | Seedbed crusting and seed rot from heavy downpours. |
| **Ploughing** | $\le 10.0\text{ mm}$ | Severe wheel slippage and hardpan compaction in waterlogged clay soils. |

### Classification Badges:
- 🟢 **Lower weather concern:** Forecast precipitation and probability within safe tolerance.
- 🟡 **Caution:** Forecast values near or slightly above thresholds; proceed with ground check.
- 🔴 **Higher rainfall concern:** Elevated precipitation predicted; high likelihood of machine immobilization.

---

## 9. Installation & Execution Guide

### Prerequisites
- Python 3.10+ installed on your computer.
- Windows PowerShell, Command Prompt, or terminal.

### Step-by-Step Instructions (Windows PowerShell)

```powershell
# 1. Navigate to the project root directory
cd d:\weather_farm_planner

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 4. Install the required dependencies
pip install -r requirements.txt

# 5. Launch the Streamlit application
streamlit run app.py
```

The application will launch automatically in your web browser at:
`http://localhost:8501`

---

## 10. Academic Disclaimers & System Limitations
1. **Correlation vs. Causation:**  
   Statistical correlation between rainy days and machinery delays **does not prove causation**. Farm machinery operations are also impacted by equipment breakdown, lack of spare parts, operator absenteeism, and varying soil clay percentages.
2. **Public Weather Model Limitations:**  
   Forecasts are sourced from numerical weather prediction (NWP) models (Open-Meteo). Microclimate conditions and sudden localized convective storms may deviate from regional model forecasts.
3. **No Direct Soil Physical Sensing:**  
   This prototype uses precipitation as a planning proxy. It does not measure direct soil cone index (bearing capacity), volumetric soil water content, or clay plasticity. Field operators must physically verify field trafficability before operating heavy tractors.

---

## 11. Viva Voce Preparation Guide (For S.Y. B.Tech Students)

**Q1: Why was Streamlit chosen instead of Flask/Django or React?**  
*Ans:* Streamlit allows rapid prototyping of pure Python data science dashboards without complex multi-tier JavaScript frameworks. It natively integrates with Pandas DataFrames and Matplotlib figures.

**Q2: Why is the Mann-Whitney $U$ test used instead of an independent Student's $t$-test?**  
*Ans:* Daily precipitation and machinery delay hours are strongly right-skewed (non-normally distributed with many zeros). The Mann-Whitney $U$ test is a non-parametric test that evaluates rank sums rather than assuming normality.

**Q3: Where does the delay rate in the Dashboard Overview come from?**  
*Ans:* The delay rate is computed strictly from the machinery operations records ($\frac{\text{delayed operations}}{\text{total operations}} \times 100\%$). It is never fabricated or computed solely from weather data.

**Q4: How does the application handle offline situations or API errors?**  
*Ans:* The `fetch_weather_data()` function includes `try-except` blocks for network timeouts and connection errors. If the API is unreachable, the app provides a button to fall back to the bundled synthetic sample dataset (`data/sample_weather.csv`), ensuring zero app crashes.

---

## 12. Future Enhancements
- Integration of IoT soil moisture sensor probes via LoRaWAN/MQTT.
- Multi-district geospatial mapping using Folium/Streamlit-Folium.
- Inclusion of wind speed thresholds specifically for aerial and boom spraying drift risk.
