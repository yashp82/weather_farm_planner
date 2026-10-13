"""
================================================================================
Weather-Based Farm Machinery Planner (Phase 1 — Intermediate Submission)
S.Y. B.Tech Python Programming Laboratory Capstone Project
Problem Statement: Agricultural Mechanization & Farm Productivity
================================================================================
Phase 1 Scope (50–60% Milestone):
- Automated meteorological data retrieval (Open-Meteo Historical Archive API)
- Fallback demonstration weather dataset (offline capability)
- Robust data cleaning and validation (clean_data)
- Descriptive weather analytics (mean, median, max, std dev, rainy days)
- Machinery operational delay tracking (delay rate, hours lost, reasons)
- Core statistical visualizations (Timeline, Monthly Totals, Histogram)
- Phase 2 Architectural Blueprint for Inferential Modeling & Weather Planning
================================================================================
"""

import datetime
import os
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ------------------------------------------------------------------------------
# 1. Page Configuration & Custom Theme Styling
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Weather-Based Farm Machinery Planner",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Agricultural Styling: Green, White, and Soft Grey Theme
st.markdown("""
<style>
    /* Main container background and typography */
    .main {
        background-color: #f8faf8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Title and Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 60%, #40916c 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.15);
    }
    .header-banner h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .header-banner p {
        margin: 8px 0 0 0;
        font-size: 1.05rem;
        color: #d8f3dc;
        font-weight: 400;
    }
    .header-banner .badge {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.22);
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        margin-top: 10px;
        color: #f1f5f9;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        border-left: 5px solid #2d6a4f;
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1b4332;
        margin: 4px 0;
    }
    .metric-desc {
        font-size: 0.8rem;
        color: #64748b;
    }

    /* Notice callout boxes */
    .academic-callout {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #16a34a;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 0.92rem;
        color: #166534;
    }
    .phase2-callout {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #3b82f6;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        color: #1e293b;
    }
    .disclaimer-callout {
        background-color: #fffbeb;
        border: 1px solid #fde68a;
        border-left: 4px solid #d97706;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 0.92rem;
        color: #92400e;
    }
    .chart-insight-box {
        background-color: #f8fafc;
        border-left: 3px solid #2d6a4f;
        padding: 10px 14px;
        margin-top: 8px;
        margin-bottom: 24px;
        font-size: 0.88rem;
        color: #334155;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Supported Locations & Farming Operations
# ------------------------------------------------------------------------------
LOCATIONS = {
    "Pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "state": "Maharashtra"},
    "Thane": {"lat": 19.2183, "lon": 72.9781, "state": "Maharashtra"},
}

FARM_OPERATIONS = ["Ploughing", "Sowing", "Spraying", "Harvesting"]

# Operation Specifications (Heuristics & Phase 2 Blueprint)
OPERATION_GUIDELINES = {
    "Ploughing": {
        "description": "Primary and secondary tillage to prepare seedbed friability. Waterlogged soil causes wheel slippage and severe subsoil compaction.",
        "recommended_max_rain": 10.0,
        "machine": "Tractor (45–55 HP) with Disc or Mouldboard Plough",
        "guidance": "Moderate moisture tolerance. Unworkable under standing water."
    },
    "Sowing": {
        "description": "Seed placement via automated seed drills. Excessive rainfall washes out seed beds or causes surface soil crusting.",
        "recommended_max_rain": 8.0,
        "machine": "Tractor with Automated Seed-cum-Fertilizer Drill",
        "guidance": "Requires optimal seedbed moisture; vulnerable to heavy downpours."
    },
    "Spraying": {
        "description": "Application of crop protection chemicals and foliar nutrients. Foliage must stay dry for several hours to prevent chemical wash-off.",
        "recommended_max_rain": 1.0,
        "machine": "Tractor-Mounted Boom Sprayer",
        "guidance": "High rain sensitivity. Best performed during dry spells."
    },
    "Harvesting": {
        "description": "Mechanized grain and crop cutting. Saturated soil mires heavy combine harvesters, causing lodging and grain spoilage.",
        "recommended_max_rain": 2.0,
        "machine": "Self-Propelled Combine Harvester",
        "guidance": "High moisture sensitivity. Requires firm, dry field conditions."
    }
}

# ------------------------------------------------------------------------------
# 3. Data Fetching and Loading Functions
# ------------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_weather_data(latitude: float, longitude: float, start_date: str, end_date: str):
    """
    Fetch daily historical weather information from the Open-Meteo Historical Weather API.
    API endpoint: https://archive-api.open-meteo.com/v1/archive
    Variables: precipitation_sum (mm), temperature_2m_max (°C), relative_humidity_2m_mean (%)
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "precipitation_sum,temperature_2m_max,relative_humidity_2m_mean",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None, f"API returned status code {response.status_code}: {response.text[:120]}"
        
        data = response.json()
        if "daily" not in data or not data["daily"].get("time"):
            return None, "Empty or invalid response received from Open-Meteo API."

        daily = data["daily"]
        df = pd.DataFrame({
            "date": daily["time"],
            "precipitation_sum": daily.get("precipitation_sum", []),
            "temperature_2m_max": daily.get("temperature_2m_max", []),
            "relative_humidity_2m_mean": daily.get("relative_humidity_2m_mean", [])
        })
        return df, None

    except requests.exceptions.Timeout:
        return None, "Connection timed out while reaching Open-Meteo API. Please verify your internet connection or use offline sample data."
    except requests.exceptions.ConnectionError:
        return None, "Network connection error. Open-Meteo API is currently unreachable. You can continue with offline sample data."
    except Exception as e:
        return None, f"An unexpected error occurred while fetching weather data: {str(e)}"


def load_sample_weather_data(location_name: str = "Pune"):
    """
    Load the bundled sample weather CSV data (synthetic demonstration dataset).
    """
    file_path = os.path.join("data", "sample_weather.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if "location" in df.columns:
            filtered = df[df["location"].str.lower() == location_name.lower()].copy()
            if not filtered.empty:
                return filtered
        return df
    else:
        # Fallback inline generation if file is missing
        dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
        np.random.seed(42)
        precip = [round(np.random.exponential(12.0) if d.month in [6, 7, 8, 9] and np.random.rand() < 0.6 else 0.0, 1) for d in dates]
        temps = [round(np.random.uniform(25.0, 34.0), 1) for _ in dates]
        humidity = [round(np.random.uniform(55.0, 85.0), 1) for _ in dates]
        return pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "location": location_name,
            "precipitation_sum": precip,
            "temperature_2m_max": temps,
            "relative_humidity_2m_mean": humidity
        })


def load_machinery_data(uploaded_file=None):
    """
    Load machinery operations records either from an uploaded CSV file
    or from the bundled demonstration file (data/machinery_operations.csv).
    """
    required_cols = [
        "date", "location", "operation", "machine_type",
        "planned_hours", "actual_hours", "delayed", "delay_reason"
    ]
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                return None, f"Uploaded CSV is missing required columns: {', '.join(missing)}"
            return df, None
        except Exception as e:
            return None, f"Failed to parse uploaded CSV: {str(e)}"

    file_path = os.path.join("data", "machinery_operations.csv")
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            return df, None
        except Exception as e:
            return None, f"Failed to read data/machinery_operations.csv: {str(e)}"
    
    return None, "Default machinery operations dataset not found in data/ folder."

# ------------------------------------------------------------------------------
# 4. Data Cleaning and Manipulation
# ------------------------------------------------------------------------------
def clean_data(df: pd.DataFrame, dataset_type: str = "weather"):
    """
    Cleans and standardizes the dataset:
    - Parses date strings to datetime objects
    - Converts numerical features to numeric datatypes
    - Identifies missing values without silently replacing them with zero
    - Identifies and drops exact duplicate rows
    - Checks for negative values in rainfall or working hours
    - Validates binary delay indicator (0 and 1)
    """
    report = {
        "initial_rows": len(df),
        "final_rows": 0,
        "missing_values_found": 0,
        "duplicates_removed": 0,
        "anomalies_handled": 0,
        "notes": []
    }
    
    if df is None or df.empty:
        report["notes"].append("Dataset is empty.")
        return pd.DataFrame(), report

    clean_df = df.copy()

    # 1. Identify and remove exact duplicate records
    dup_count = clean_df.duplicated().sum()
    if dup_count > 0:
        clean_df = clean_df.drop_duplicates().reset_index(drop=True)
        report["duplicates_removed"] = int(dup_count)
        report["notes"].append(f"Removed {dup_count} duplicate record(s).")

    # 2. Convert and validate date column
    if "date" in clean_df.columns:
        clean_df["date"] = pd.to_datetime(clean_df["date"], errors="coerce")
        invalid_dates = clean_df["date"].isna().sum()
        if invalid_dates > 0:
            clean_df = clean_df.dropna(subset=["date"]).reset_index(drop=True)
            report["anomalies_handled"] += int(invalid_dates)
            report["notes"].append(f"Dropped {invalid_dates} row(s) with unparseable dates.")

    # 3. Clean dataset-specific columns
    if dataset_type == "weather":
        num_cols = ["precipitation_sum", "temperature_2m_max", "relative_humidity_2m_mean"]
        for col in num_cols:
            if col in clean_df.columns:
                clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")
                missing = clean_df[col].isna().sum()
                if missing > 0:
                    report["missing_values_found"] += int(missing)
                    report["notes"].append(f"Identified {missing} missing values in '{col}'.")
                
                # Check for invalid negative values (e.g. negative precipitation)
                if col == "precipitation_sum":
                    neg_mask = clean_df[col] < 0
                    neg_count = neg_mask.sum()
                    if neg_count > 0:
                        clean_df.loc[neg_mask, col] = 0.0
                        report["anomalies_handled"] += int(neg_count)
                        report["notes"].append(f"Adjusted {neg_count} negative rainfall values to 0.0 mm.")

    elif dataset_type == "machinery":
        num_cols = ["planned_hours", "actual_hours", "delayed"]
        for col in num_cols:
            if col in clean_df.columns:
                clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")
                missing = clean_df[col].isna().sum()
                if missing > 0:
                    report["missing_values_found"] += int(missing)
                    report["notes"].append(f"Identified {missing} missing values in '{col}'.")
        
        # Check negative working hours
        for col in ["planned_hours", "actual_hours"]:
            if col in clean_df.columns:
                neg_hours = (clean_df[col] < 0).sum()
                if neg_hours > 0:
                    clean_df = clean_df[clean_df[col] >= 0].reset_index(drop=True)
                    report["anomalies_handled"] += int(neg_hours)
                    report["notes"].append(f"Dropped {neg_hours} row(s) with invalid negative hours in '{col}'.")
        
        # Validate binary delay column (must be 0 or 1)
        if "delayed" in clean_df.columns:
            invalid_delay = (~clean_df["delayed"].isin([0, 1])).sum()
            if invalid_delay > 0:
                clean_df["delayed"] = clean_df["delayed"].apply(lambda v: 1 if v == 1 else 0)
                report["anomalies_handled"] += int(invalid_delay)
                report["notes"].append(f"Normalized {invalid_delay} non-binary values in 'delayed' to 0 or 1.")
        
        # Clean text columns
        text_cols = ["location", "operation", "machine_type", "delay_reason"]
        for col in text_cols:
            if col in clean_df.columns:
                clean_df[col] = clean_df[col].astype(str).str.strip()

    report["final_rows"] = len(clean_df)
    return clean_df, report

# ------------------------------------------------------------------------------
# 5. Statistical Calculations
# ------------------------------------------------------------------------------
def calculate_weather_statistics(weather_df: pd.DataFrame, rainy_threshold: float = 0.0):
    """
    Computes descriptive statistics for historical weather data using Pandas and NumPy.
    Rainy day is defined as precipitation > rainy_threshold (default > 0.0 mm).
    """
    if weather_df is None or weather_df.empty or "precipitation_sum" not in weather_df.columns:
        return None

    precip = weather_df["precipitation_sum"].dropna()
    total_days = len(precip)
    if total_days == 0:
        return None

    rainy_days_mask = precip > rainy_threshold
    rainy_days_count = int(rainy_days_mask.sum())
    rainy_days_pct = (rainy_days_count / total_days) * 100.0

    return {
        "total_records": total_days,
        "mean_rain": float(precip.mean()),
        "median_rain": float(precip.median()),
        "max_rain": float(precip.max()),
        "std_rain": float(precip.std()) if total_days > 1 else 0.0,
        "total_rain": float(precip.sum()),
        "rainy_days_count": rainy_days_count,
        "rainy_days_pct": rainy_days_pct,
        "dry_days_count": total_days - rainy_days_count,
        "rainy_threshold": rainy_threshold
    }


def calculate_delay_statistics(machinery_df: pd.DataFrame):
    """
    Computes descriptive metrics from valid machinery operation records.
    Delay rate is strictly calculated only from machinery operation records.
    """
    if machinery_df is None or machinery_df.empty or "delayed" not in machinery_df.columns:
        return None

    total_ops = len(machinery_df)
    if total_ops == 0:
        return None

    delayed_mask = machinery_df["delayed"] == 1
    delayed_ops = int(delayed_mask.sum())
    delay_rate = (delayed_ops / total_ops) * 100.0

    planned = machinery_df["planned_hours"].dropna()
    actual = machinery_df["actual_hours"].dropna()

    avg_planned = float(planned.mean()) if not planned.empty else 0.0
    avg_actual = float(actual.mean()) if not actual.empty else 0.0

    # Total recorded hours lost: sum of positive differences between actual and planned hours
    if "planned_hours" in machinery_df.columns and "actual_hours" in machinery_df.columns:
        hours_diff = machinery_df["actual_hours"] - machinery_df["planned_hours"]
        hours_lost = hours_diff.apply(lambda x: max(0.0, float(x)))
        total_hours_lost = float(hours_lost.sum())
    else:
        total_hours_lost = 0.0

    return {
        "total_operations": total_ops,
        "delayed_operations": delayed_ops,
        "on_time_operations": total_ops - delayed_ops,
        "delay_rate": delay_rate,
        "avg_planned_hours": avg_planned,
        "avg_actual_hours": avg_actual,
        "total_hours_lost": total_hours_lost
    }

# ------------------------------------------------------------------------------
# 6. Basic Chart Creation Functions (Matplotlib & Seaborn)
# ------------------------------------------------------------------------------
def create_basic_weather_charts(weather_df: pd.DataFrame, rainy_threshold: float = 0.0):
    """
    Builds clean, labelled agricultural analytics charts using Matplotlib and Seaborn:
    1. Daily rainfall timeline (Line Chart)
    2. Monthly rainfall totals (Bar Chart)
    3. Daily rainfall distribution (Histogram)
    """
    sns.set_theme(style="whitegrid", palette="muted")
    charts = {}

    if weather_df is None or weather_df.empty:
        return charts

    # Chart 1: Daily Rainfall Over Time
    fig1, ax1 = plt.subplots(figsize=(10, 4.2))
    dates = pd.to_datetime(weather_df["date"])
    precip = weather_df["precipitation_sum"]

    ax1.plot(dates, precip, color="#2d6a4f", linewidth=1.5, label="Daily Rainfall (mm)")
    ax1.fill_between(dates, precip, color="#74c69d", alpha=0.35)
    ax1.axhline(rainy_threshold, color="#e76f51", linestyle="--", linewidth=1.2,
                label=f"Rainy Day Threshold ({rainy_threshold} mm)")
    ax1.set_title("Historical Daily Precipitation Over Time", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
    ax1.set_xlabel("Date", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Precipitation (mm)", fontsize=10, fontweight="bold")
    ax1.legend(loc="upper right", frameon=True)
    fig1.tight_layout()
    charts["rainfall_timeline"] = fig1

    # Chart 2: Rainfall Totals by Month
    fig2, ax2 = plt.subplots(figsize=(9, 4.2))
    w_copy = weather_df.copy()
    w_copy["month_dt"] = pd.to_datetime(w_copy["date"])
    w_copy["month_name"] = w_copy["month_dt"].dt.strftime("%b")
    w_copy["month_num"] = w_copy["month_dt"].dt.month
    monthly = w_copy.groupby(["month_num", "month_name"])["precipitation_sum"].sum().reset_index()
    monthly = monthly.sort_values("month_num")

    bars = ax2.bar(monthly["month_name"], monthly["precipitation_sum"], color="#52b788", edgecolor="#2d6a4f")
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.annotate(f"{height:.1f}",
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points",
                         ha="center", va="bottom", fontsize=8, color="#1b4332")

    ax2.set_title("Monthly Total Precipitation (mm)", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
    ax2.set_xlabel("Month", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Total Rainfall (mm)", fontsize=10, fontweight="bold")
    fig2.tight_layout()
    charts["monthly_rainfall"] = fig2

    # Chart 3: Distribution of Daily Rainfall (Histogram)
    fig3, ax3 = plt.subplots(figsize=(8, 4.2))
    precip_clean = weather_df["precipitation_sum"].dropna()
    sns.histplot(precip_clean, bins=25, color="#40916c", kde=True, ax=ax3, edgecolor="#1b4332")
    ax3.set_title("Distribution of Daily Precipitation", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
    ax3.set_xlabel("Daily Precipitation (mm)", fontsize=10, fontweight="bold")
    ax3.set_ylabel("Frequency (Number of Days)", fontsize=10, fontweight="bold")
    fig3.tight_layout()
    charts["rainfall_dist"] = fig3

    return charts

# ------------------------------------------------------------------------------
# 7. User Interface Layout & Sidebar Controls
# ------------------------------------------------------------------------------
# Top Header Banner
st.markdown("""
<div class="header-banner">
    <h1>🌾 Weather-Based Farm Machinery Planner</h1>
    <p>Analyze weather patterns, understand machinery delays, and plan farm operations more effectively.</p>
    <div class="badge">S.Y. B.Tech Python Programming Laboratory Capstone Project | Phase 1 (50–60% Milestone)</div>
</div>
""", unsafe_allow_html=True)

# Sidebar: Controls and Configuration
st.sidebar.header("⚙️ Configuration & Filters")

# Location Selection (Pune, Nashik, Thane)
selected_location = st.sidebar.selectbox(
    "📍 Select Location",
    options=list(LOCATIONS.keys()),
    index=0,
    help="Select an Indian agricultural district to analyze historical weather patterns."
)
loc_info = LOCATIONS[selected_location]
st.sidebar.caption(f"Coordinates: {loc_info['lat']}° N, {loc_info['lon']}° E ({loc_info['state']})")

st.sidebar.markdown("---")

# Data Source Selection
st.sidebar.subheader("📡 Data Sources")
weather_source_option = st.sidebar.radio(
    "Weather Data Source",
    options=["Live Open-Meteo API", "Sample Dataset (Offline Demo)"],
    index=0,
    help="Fetch live daily weather from Open-Meteo Historical API or load the bundled sample dataset."
)

# Date Range Selection (Default: complete 2024 calendar year)
default_start = datetime.date(2024, 1, 1)
default_end = datetime.date(2024, 12, 31)

date_range = st.sidebar.date_input(
    "📅 Historical Date Range",
    value=(default_start, default_end),
    min_value=datetime.date(2020, 1, 1),
    max_value=datetime.date.today(),
    help="Select the period for historical weather observations."
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date_str = date_range[0].strftime("%Y-%m-%d")
    end_date_str = date_range[1].strftime("%Y-%m-%d")
else:
    start_date_str = default_start.strftime("%Y-%m-%d")
    end_date_str = default_end.strftime("%Y-%m-%d")

# Farming Operation Selection
st.sidebar.markdown("---")
st.sidebar.subheader("🚜 Farming Operations")

selected_op = st.sidebar.selectbox(
    "Planned Farming Operation",
    options=FARM_OPERATIONS,
    index=0,
    help="Select an operation to review baseline requirements and historical delay logs."
)

filter_machinery_by_op = st.sidebar.checkbox(
    f"Filter machinery metrics strictly to '{selected_op}'",
    value=False,
    help="If checked, machinery statistics reflect only the chosen operation instead of all operations."
)

# Rainy Day Threshold Definition
st.sidebar.markdown("---")
st.sidebar.subheader("🌧️ Analytical Parameters")
rainy_threshold = 0.0
st.sidebar.caption(f"Rainy Day Definition: Days with precipitation > {rainy_threshold} mm are classified as Rainy Days.")

# Optional File Uploader for Custom Machinery CSV
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Custom Data Upload")
custom_machinery_file = st.sidebar.file_uploader(
    "Upload Machinery Operations CSV",
    type=["csv"],
    help="Upload your own machinery log CSV with required columns (see README)."
)

# Academic Demonstration Label
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background-color: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 0.8rem; color: #475569;'>
    <b>Academic Project Note:</b><br>
    Intermediate submission (Phase 1: 50–60% Completion). Synthetic sample datasets are explicitly marked as demonstration records.
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 8. Data Loading & Cleaning Execution
# ------------------------------------------------------------------------------
raw_weather_df = None
weather_fetch_error = None
is_sample_weather = False

if weather_source_option == "Live Open-Meteo API":
    with st.spinner(f"Fetching historical weather records for {selected_location} via Open-Meteo API..."):
        raw_weather_df, weather_fetch_error = fetch_weather_data(
            latitude=loc_info["lat"],
            longitude=loc_info["lon"],
            start_date=start_date_str,
            end_date=end_date_str
        )
    if raw_weather_df is None:
        st.warning(f"⚠️ {weather_fetch_error}")
        load_sample_btn = st.button("🔄 Fall back to Sample Weather Dataset (Demo Mode)")
        if load_sample_btn or raw_weather_df is None:
            raw_weather_df = load_sample_weather_data(selected_location)
            is_sample_weather = True
            st.info("Loaded bundled sample weather data for demonstration.")
else:
    raw_weather_df = load_sample_weather_data(selected_location)
    is_sample_weather = True

# Load Machinery Operations Dataset
raw_machinery_df, machinery_load_error = load_machinery_data(uploaded_file=custom_machinery_file)
if machinery_load_error:
    st.error(f"❌ Machinery Dataset Error: {machinery_load_error}")

# Execute Data Cleaning
clean_weather_df, weather_clean_report = clean_data(raw_weather_df, dataset_type="weather") if raw_weather_df is not None else (pd.DataFrame(), {})
clean_machinery_df, machinery_clean_report = clean_data(raw_machinery_df, dataset_type="machinery") if raw_machinery_df is not None else (pd.DataFrame(), {})

# Filter machinery by location if applicable
if not clean_machinery_df.empty and "location" in clean_machinery_df.columns:
    loc_match = clean_machinery_df[clean_machinery_df["location"].str.lower() == selected_location.lower()]
    if not loc_match.empty:
        active_machinery_df = loc_match.copy()
    else:
        active_machinery_df = clean_machinery_df.copy()
else:
    active_machinery_df = clean_machinery_df.copy()

# Filter by selected operation if user selected the checkbox
if filter_machinery_by_op and not active_machinery_df.empty and "operation" in active_machinery_df.columns:
    active_machinery_df = active_machinery_df[active_machinery_df["operation"].str.lower() == selected_op.lower()]

# ------------------------------------------------------------------------------
# 9. Compute Baseline Statistics
# ------------------------------------------------------------------------------
weather_stats = calculate_weather_statistics(clean_weather_df, rainy_threshold=rainy_threshold)
machinery_stats = calculate_delay_statistics(active_machinery_df)

# ------------------------------------------------------------------------------
# 10. Main Application Tabs
# ------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Dashboard Overview",
    "📈 Historical Data Analysis",
    "🗓️ Weather-Based Planning"
])

# ==============================================================================
# TAB 1: DASHBOARD OVERVIEW
# ==============================================================================
with tab1:
    st.subheader(f"Overview for {selected_location}")
    if is_sample_weather:
        st.caption("ℹ️ Showing synthetic sample demonstration weather records.")
    else:
        st.caption(f"🌐 Sourced from Open-Meteo Historical Archive API ({start_date_str} to {end_date_str}).")

    # Four Summary Metric Cards
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    # 1. Total weather records
    with m_col1:
        val1 = f"{weather_stats['total_records']}" if weather_stats else "Not available"
        desc1 = f"Days in period" if weather_stats else "Missing weather data"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Weather Records</div>
            <div class="metric-value">{val1}</div>
            <div class="metric-desc">{desc1}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Average daily rainfall (mm)
    with m_col2:
        val2 = f"{weather_stats['mean_rain']:.1f} mm" if weather_stats else "Not available"
        desc2 = f"Median: {weather_stats['median_rain']:.1f} mm" if weather_stats else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Daily Rainfall</div>
            <div class="metric-value">{val2}</div>
            <div class="metric-desc">{desc2}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Number of rainy days
    with m_col3:
        if weather_stats:
            val3 = f"{weather_stats['rainy_days_count']}"
            desc3 = f"{weather_stats['rainy_days_pct']:.1f}% of days (>{rainy_threshold} mm)"
        else:
            val3 = "Not available"
            desc3 = "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Rainy Days</div>
            <div class="metric-value">{val3}</div>
            <div class="metric-desc">{desc3}</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Historical machinery operation delay rate
    # Calculated strictly from machinery operation records only!
    with m_col4:
        if machinery_stats:
            val4 = f"{machinery_stats['delay_rate']:.1f}%"
            desc4 = f"{machinery_stats['delayed_operations']} of {machinery_stats['total_operations']} operations delayed"
        else:
            val4 = "Not available"
            desc4 = "No valid machinery logs"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Machinery Delay Rate</div>
            <div class="metric-value">{val4}</div>
            <div class="metric-desc">{desc4}</div>
        </div>
        """, unsafe_allow_html=True)

    # Automated Summary Narrative
    st.markdown("#### 📝 Executive Summary")
    summary_parts = []
    if weather_stats:
        summary_parts.append(
            f"Over the selected interval in **{selected_location}**, a total of **{weather_stats['total_records']} daily weather observations** "
            f"were loaded with cumulative rainfall reaching **{weather_stats['total_rain']:.1f} mm**. "
            f"Rainfall (> {rainy_threshold} mm) was recorded on **{weather_stats['rainy_days_count']} days ({weather_stats['rainy_days_pct']:.1f}%)**, "
            f"yielding a daily mean of **{weather_stats['mean_rain']:.1f} mm** and a peak daily event of **{weather_stats['max_rain']:.1f} mm**."
        )
    else:
        summary_parts.append("Weather records are currently not available for this period.")

    if machinery_stats:
        op_scope = f"specifically for {selected_op}" if filter_machinery_by_op else "across all logged operations"
        summary_parts.append(
            f"From the machinery operation dataset ({op_scope}), **{machinery_stats['total_operations']} operations** were logged. "
            f"The recorded delay rate was **{machinery_stats['delay_rate']:.1f}%** ({machinery_stats['delayed_operations']} delayed operations), "
            f"representing a cumulative **{machinery_stats['total_hours_lost']:.1f} operating hours lost** compared to planned schedules."
        )
    else:
        summary_parts.append("Machinery operational records are not available to calculate delay statistics.")

    st.markdown(f"""
    <div class="academic-callout">
        {' '.join(summary_parts)}
    </div>
    """, unsafe_allow_html=True)

    # Data Quality and Cleaning Report
    with st.expander("🛠️ Data Quality & Cleaning Summary (clean_data() Report)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Weather Dataset Cleaning**")
            st.write(f"- Initial rows: {weather_clean_report.get('initial_rows', 0)}")
            st.write(f"- Final cleaned rows: {weather_clean_report.get('final_rows', 0)}")
            st.write(f"- Missing values identified: {weather_clean_report.get('missing_values_found', 0)}")
            st.write(f"- Duplicates removed: {weather_clean_report.get('duplicates_removed', 0)}")
            st.write(f"- Anomalies handled: {weather_clean_report.get('anomalies_handled', 0)}")
            if weather_clean_report.get("notes"):
                for note in weather_clean_report["notes"]:
                    st.caption(f"• {note}")

        with c2:
            st.markdown("**Machinery Operations Dataset Cleaning**")
            st.write(f"- Initial rows: {machinery_clean_report.get('initial_rows', 0)}")
            st.write(f"- Final cleaned rows: {machinery_clean_report.get('final_rows', 0)}")
            st.write(f"- Missing values identified: {machinery_clean_report.get('missing_values_found', 0)}")
            st.write(f"- Duplicates removed: {machinery_clean_report.get('duplicates_removed', 0)}")
            st.write(f"- Anomalies handled: {machinery_clean_report.get('anomalies_handled', 0)}")
            if machinery_clean_report.get("notes"):
                for note in machinery_clean_report["notes"]:
                    st.caption(f"• {note}")

    # Data Preview Tables
    with st.expander("🔍 View Cleaned Weather & Machinery Tables", expanded=False):
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**Cleaned Weather Data (First 10 Rows)**")
            if clean_weather_df is not None and not clean_weather_df.empty:
                st.dataframe(clean_weather_df.head(10), use_container_width=True)
            else:
                st.write("No weather data available.")
        with t2:
            st.markdown("**Cleaned Machinery Operations Data (First 10 Rows)**")
            if active_machinery_df is not None and not active_machinery_df.empty:
                st.dataframe(active_machinery_df.head(10), use_container_width=True)
            else:
                st.write("No machinery data available.")

# ==============================================================================
# TAB 2: HISTORICAL DATA ANALYSIS
# ==============================================================================
with tab2:
    st.subheader("Historical Weather & Machinery Analysis (Phase 1)")

    # Section A: Descriptive Weather Statistics
    st.markdown("### A. Descriptive Weather Statistics")
    if weather_stats:
        d_col1, d_col2, d_col3 = st.columns(3)
        with d_col1:
            st.markdown(f"**Mean Daily Rainfall:** `{weather_stats['mean_rain']:.2f} mm`")
            st.markdown(f"**Median Daily Rainfall:** `{weather_stats['median_rain']:.2f} mm`")
        with d_col2:
            st.markdown(f"**Maximum Daily Rainfall:** `{weather_stats['max_rain']:.2f} mm`")
            st.markdown(f"**Standard Deviation ($\\sigma$):** `{weather_stats['std_rain']:.2f} mm`")
        with d_col3:
            st.markdown(f"**Total Cumulative Rainfall:** `{weather_stats['total_rain']:.1f} mm`")
            st.markdown(f"**Rainy Days ($>{rainy_threshold}$ mm):** `{weather_stats['rainy_days_count']} ({weather_stats['rainy_days_pct']:.1f}%)`")
        st.caption(f"*Rainy day definition: Daily precipitation > {rainy_threshold} mm.*")
    else:
        st.warning("Weather statistics are unavailable because valid weather data has not been loaded.")

    st.markdown("---")

    # Section B: Machinery Delay Analysis
    st.markdown("### B. Machinery Operation Delay Analysis")
    if machinery_stats:
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"**Total Operations Logged:** `{machinery_stats['total_operations']}`")
            st.markdown(f"**Delayed Operations:** `{machinery_stats['delayed_operations']}`")
            st.markdown(f"**Overall Delay Rate:** `{machinery_stats['delay_rate']:.1f}%`")
        with m_col2:
            st.markdown(f"**Avg Planned Duration:** `{machinery_stats['avg_planned_hours']:.1f} hours`")
            st.markdown(f"**Avg Actual Duration:** `{machinery_stats['avg_actual_hours']:.1f} hours`")
            st.markdown(f"**Total Recorded Hours Lost:** `{machinery_stats['total_hours_lost']:.1f} hours`")
        with m_col3:
            st.markdown("**Delay Reasons Breakdown:**")
            if "delay_reason" in active_machinery_df.columns:
                reasons = active_machinery_df["delay_reason"].value_counts()
                for r_name, r_cnt in reasons.items():
                    st.write(f"- *{r_name.capitalize()}*: {r_cnt}")
    else:
        st.info("No machinery operational records loaded.")

    st.markdown("---")

    # Section C: Basic Visualizations (Matplotlib & Seaborn)
    st.markdown("### C. Statistical Data Visualizations")
    charts = create_basic_weather_charts(clean_weather_df, rainy_threshold=rainy_threshold)

    # 1. Line chart: Daily rainfall over time
    if "rainfall_timeline" in charts:
        st.pyplot(charts["rainfall_timeline"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 1 Insight:</b> Historical chronology of daily precipitation. 
            Highlights high-intensity precipitation peaks during monsoon months, contrasting with prolonged dry periods.
        </div>
        """, unsafe_allow_html=True)

    # 2. Bar chart: Monthly rainfall totals
    if "monthly_rainfall" in charts:
        st.pyplot(charts["monthly_rainfall"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 2 Insight:</b> Monthly cumulative precipitation totals. 
            Peak rainfall months coincide with critical Kharif tillage and sowing operations, driving potential machinery delays.
        </div>
        """, unsafe_allow_html=True)

    # 3. Histogram: Distribution of daily rainfall
    if "rainfall_dist" in charts:
        st.pyplot(charts["rainfall_dist"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 3 Insight:</b> Frequency distribution of daily precipitation values. 
            Shows strong positive skewness, with the majority of days recording dry or light precipitation and a smaller tail of extreme downpours.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Section D: Phase 2 Roadmap & Deferred Features Preview
    st.markdown("""
    <div class="phase2-callout">
        <h4 style="margin: 0 0 8px 0; color: #1e3a8a;">🔬 Advanced Delay Modeling & Inferential Statistics (Phase 2 Preview)</h4>
        <p style="margin: 0 0 10px 0; font-size: 0.93rem; color: #334155;">
            In accordance with the <b>Phase 1 milestone (50–60% Completion)</b>, baseline data ingestion, data cleaning, 
            and descriptive statistics have been fully validated. The following advanced inferential and predictive analyses 
            are scheduled for implementation in <b>Phase 2</b>:
        </p>
        <ul style="margin: 0 0 10px 20px; font-size: 0.9rem; color: #475569; line-height: 1.6;">
            <li><b>Merged Weather-Delay Cross Analysis:</b> Direct comparison of operational delay rates between rainy and non-rainy operation days.</li>
            <li><b>Correlation Analysis:</b> Calculation of Pearson ($r$) and Spearman ($\rho$) correlation coefficients between daily rainfall and hours lost.</li>
            <li><b>Hypothesis Testing:</b> Non-parametric SciPy statistical testing (Mann-Whitney $U$ test) with null hypothesis and $p$-value interpretation.</li>
            <li><b>Rainfall-versus-Delay Scatter Modeling:</b> Regression scatter plots mapping daily precipitation against lost operational hours.</li>
        </ul>
        <span style="font-size: 0.85rem; color: #64748b; font-style: italic;">
            Note: Advanced statistical tests are intentionally scheduled for Phase 2 to ensure thorough data validation and baseline descriptive analysis first.
        </span>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# TAB 3: WEATHER-BASED PLANNING SECTION (PHASE 2 PREVIEW)
# ==============================================================================
with tab3:
    st.subheader(f"Weather-Based Operational Planning (Phase 2 Preview) — {selected_location}")

    # Professional Phase 2 Planning Notice
    st.markdown("""
    <div class="phase2-callout">
        <h4 style="margin: 0 0 6px 0; color: #1e3a8a;">🗓️ Operational Decision-Support System Roadmap</h4>
        <p style="margin: 0 0 8px 0; font-size: 0.95rem; color: #1e293b;">
            <b>Advanced weather-based planning and delay analysis will be implemented in Phase 2.</b>
        </p>
        <p style="margin: 0; font-size: 0.9rem; color: #475569;">
            Phase 1 provides the foundational descriptive benchmarks and data pipelines. Phase 2 will introduce live numerical forecast integration 
            and operational risk matrices to generate forward-looking machinery schedules.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Architectural Blueprint for Selected Operation
    op_guide = OPERATION_GUIDELINES.get(selected_op, {})
    st.markdown(f"#### 🚜 Target Operation Profile: {selected_op}")

    p_col1, p_col2 = st.columns([3, 2])
    with p_col1:
        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
            <h5 style="margin: 0 0 8px 0; color: #1b4332;">Agronomic & Machinery Specifications</h5>
            <p style="margin: 0 0 10px 0; font-size: 0.92rem; color: #334155;">{op_guide.get('description', '')}</p>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #475569; line-height: 1.6;">
                <li><b>Typical Equipment:</b> {op_guide.get('machine', '')}</li>
                <li><b>Operational Sensitivity:</b> {op_guide.get('guidance', '')}</li>
                <li><b>Planned Maximum Rainfall Tolerance:</b> <code>≤ {op_guide.get('recommended_max_rain', 5.0)} mm</code></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with p_col2:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
            <h5 style="margin: 0 0 8px 0; color: #1b4332;">Planned Decision Indicators</h5>
            <div style="margin-bottom: 8px;">
                <span style="background-color: #d1fae5; color: #065f46; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">🟢 Lower weather concern</span>
                <span style="font-size: 0.8rem; color: #475569;"> — Conducive field conditions</span>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="background-color: #fef3c7; color: #92400e; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">🟡 Caution</span>
                <span style="font-size: 0.8rem; color: #475569;"> — Marginal moisture / ground check required</span>
            </div>
            <div>
                <span style="background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">🔴 Higher rainfall concern</span>
                <span style="font-size: 0.8rem; color: #475569;"> — Wet soil / high immobilization risk</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Phase 2 Implementation Framework Table
    st.markdown("#### 📋 Phase 2 Implementation Framework")
    framework_data = pd.DataFrame([
        {
            "Module": "Live Forecast Ingestion",
            "Target Feature": "Open-Meteo 7-day numerical weather forecast integration",
            "Status": "Scheduled for Phase 2"
        },
        {
            "Module": "Dynamic Heuristics Engine",
            "Target Feature": "Operation-specific precipitation and probability threshold evaluation",
            "Status": "Scheduled for Phase 2"
        },
        {
            "Module": "Automated Advisory Matrix",
            "Target Feature": "Day-by-day scheduling recommendations and dry window detection",
            "Status": "Scheduled for Phase 2"
        },
        {
            "Module": "Soil Trafficability Integration",
            "Target Feature": "Field inspection guidelines and drainage check advisories",
            "Status": "Scheduled for Phase 2"
        }
    ])
    st.table(framework_data)

    # Disclaimers
    st.markdown("""
    <div class="disclaimer-callout">
        <b>⚠️ Agronomic Limitations & Field Trafficability Notice:</b><br>
        Precipitation forecasts and threshold heuristics represent planning aids, not guaranteed agronomic safety limits. 
        Rainfall alone does not directly measure root-zone soil saturation or load-bearing trafficability. 
        Physical on-site inspection must always precede heavy machinery deployment.
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 11. Application Footer & Data Source Transparency
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="font-size: 0.85rem; color: #64748b; line-height: 1.5;">
    <b>Weather-Based Farm Machinery Planner</b> | S.Y. B.Tech Python Programming Laboratory Capstone Project (Phase 1: 50–60% Completion)<br>
    <b>Weather Data Provider:</b> Open-Meteo Historical Archive API (Non-commercial open-access).<br>
    <b>Machinery Operations:</b> Demonstration dataset with explicitly synthetic records for student laboratory analysis.<br>
    <b>Phase 1 Technology Stack:</b> Streamlit, Pandas, NumPy, Matplotlib, Seaborn, Requests.
</div>
""", unsafe_allow_html=True)
