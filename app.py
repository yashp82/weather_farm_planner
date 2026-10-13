"""
================================================================================
Weather-Based Farm Machinery Planner
S.Y. B.Tech Python Programming Laboratory Capstone Project
Problem Statement: Agricultural Mechanization & Farm Productivity
================================================================================
This application provides data analytics and weather-based planning to help
farmers and farm machinery planners analyze how precipitation impacts farm
equipment operations (ploughing, sowing, spraying, harvesting).
"""

import datetime
import os
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
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
        background-color: rgba(255, 255, 255, 0.2);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        margin-top: 10px;
        color: #f1f5f9;
        font-weight: 500;
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

    /* Recommendation Badges */
    .badge-lower-concern {
        background-color: #d1fae5;
        color: #065f46;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-caution {
        background-color: #fef3c7;
        color: #92400e;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-higher-concern {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
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
        border-left: 3px solid #64748b;
        padding: 8px 12px;
        margin-top: 8px;
        margin-bottom: 24px;
        font-size: 0.88rem;
        color: #334155;
        border-radius: 0 4px 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Supported Locations & Baseline Configurations
# ------------------------------------------------------------------------------
LOCATIONS = {
    "Pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "state": "Maharashtra"},
    "Thane": {"lat": 19.2183, "lon": 72.9781, "state": "Maharashtra"},
}

FARM_OPERATIONS = ["Ploughing", "Sowing", "Spraying", "Harvesting"]

# Operation-specific rainfall sensitivity guidelines (Heuristics)
OPERATION_GUIDELINES = {
    "Spraying": {
        "description": "Chemical spraying (pesticides, fungicides, foliar nutrients) requires dry foliage. Rain within 2-4 hours washes chemicals away.",
        "recommended_max_rain": 1.0,
        "recommended_max_prob": 30.0,
        "machine": "Boom Sprayer / Tractor Mounted Sprayer",
        "guidance": "High rain sensitivity: Avoid operations when precipitation is expected."
    },
    "Harvesting": {
        "description": "Combine harvesters and grain transport equipment require dry crops and stable soil to avoid grain rotting and deep ruts.",
        "recommended_max_rain": 2.0,
        "recommended_max_prob": 35.0,
        "machine": "Combine Harvester / Multi-crop Thresher",
        "guidance": "High soil & crop moisture sensitivity: Standing water halts harvesting."
    },
    "Ploughing": {
        "description": "Tractor ploughing needs manageable soil friability. Extremely wet, saturated clay causes wheel slippage and severe soil compaction.",
        "recommended_max_rain": 10.0,
        "recommended_max_prob": 60.0,
        "machine": "Tractor (45-55 HP) with Disc/Mouldboard Plough",
        "guidance": "Moderate moisture tolerance: Dry ploughing is difficult; waterlogged soil clogs tillage implements."
    },
    "Sowing": {
        "description": "Seed drills require optimum seedbed moisture. Excessive rain leads to seed rotting or soil capping.",
        "recommended_max_rain": 8.0,
        "recommended_max_prob": 50.0,
        "machine": "Tractor with Automated Seed-cum-Fertilizer Drill",
        "guidance": "Optimal moisture window: Light rain post-sowing is beneficial; heavy downpours cause seed crusting."
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
            return None, "Empty or invalid response received from weather service."

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


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_forecast_data(latitude: float, longitude: float):
    """
    Fetch upcoming 7-day weather forecast from the Open-Meteo Forecast API.
    API endpoint: https://api.open-meteo.com/v1/forecast
    Variables: precipitation_sum (mm), precipitation_probability_max (%), temperature_2m_max (°C)
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None, f"Forecast API returned error code {response.status_code}"
        
        data = response.json()
        if "daily" not in data or not data["daily"].get("time"):
            return None, "No forecast records received."

        daily = data["daily"]
        df = pd.DataFrame({
            "date": daily["time"],
            "precipitation_sum": daily.get("precipitation_sum", [0.0]*len(daily["time"])),
            "precipitation_probability_max": daily.get("precipitation_probability_max", [0]*len(daily["time"])),
            "temperature_2m_max": daily.get("temperature_2m_max", [28.0]*len(daily["time"]))
        })
        return df, None

    except Exception as e:
        return None, f"Forecast unavailable: {str(e)}"


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
        # Fallback inline generation if file was missing
        dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
        np.random.seed(42)
        precip = [round(np.random.exponential(12.0) if d.month in [6,7,8,9] and np.random.rand() < 0.6 else 0.0, 1) for d in dates]
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
    - Identifies and reports missing values
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
                    report["notes"].append(f"Found {missing} missing values in '{col}'.")
                
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
                    report["notes"].append(f"Found {missing} missing values in '{col}'.")
        
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
    Computes descriptive statistics for historical weather data.
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


def analyze_weather_delay_relationship(weather_df: pd.DataFrame, machinery_df: pd.DataFrame, rainy_threshold: float = 0.0):
    """
    Merges weather and machinery datasets on matching dates and location,
    and analyzes delay patterns on rainy vs non-rainy operation days.
    """
    if weather_df is None or machinery_df is None or weather_df.empty or machinery_df.empty:
        return None, "Insufficient data for joint analysis."

    # Prepare merge keys
    w = weather_df.copy()
    m = machinery_df.copy()

    w["date_str"] = pd.to_datetime(w["date"]).dt.strftime("%Y-%m-%d")
    m["date_str"] = pd.to_datetime(m["date"]).dt.strftime("%Y-%m-%d")

    # Match on date and, if present in both, location
    merge_keys = ["date_str"]
    if "location" in w.columns and "location" in m.columns:
        # Check if locations overlap
        w_locs = set(w["location"].dropna().unique())
        m_locs = set(m["location"].dropna().unique())
        if len(w_locs.intersection(m_locs)) > 0:
            merge_keys.append("location")

    merged = pd.merge(m, w, on=merge_keys, how="inner", suffixes=("_machinery", "_weather"))

    if len(merged) < 3:
        return None, "Fewer than 3 matched operation dates between weather and machinery records."

    # Define rainy day for machinery operation
    merged["is_rainy"] = merged["precipitation_sum"] > rainy_threshold
    merged["hours_lost"] = (merged["actual_hours"] - merged["planned_hours"]).clip(lower=0.0)

    rainy_ops = merged[merged["is_rainy"]]
    dry_ops = merged[~merged["is_rainy"]]

    rainy_total = len(rainy_ops)
    dry_total = len(dry_ops)

    rainy_delay_rate = (rainy_ops["delayed"] == 1).mean() * 100.0 if rainy_total > 0 else 0.0
    dry_delay_rate = (dry_ops["delayed"] == 1).mean() * 100.0 if dry_total > 0 else 0.0
    rate_diff = rainy_delay_rate - dry_delay_rate

    # Calculate Correlation if sample size and variation are sufficient
    corr_results = {}
    valid_data = merged.dropna(subset=["precipitation_sum", "hours_lost"])
    if len(valid_data) >= 8 and valid_data["precipitation_sum"].std() > 0 and valid_data["hours_lost"].std() > 0:
        pearson_r, pearson_p = stats.pearsonr(valid_data["precipitation_sum"], valid_data["hours_lost"])
        spearman_rho, spearman_p = stats.spearmanr(valid_data["precipitation_sum"], valid_data["hours_lost"])
        corr_results = {
            "sufficient": True,
            "pearson_r": float(pearson_r),
            "pearson_p": float(pearson_p),
            "spearman_rho": float(spearman_rho),
            "spearman_p": float(spearman_p),
            "sample_size": len(valid_data)
        }
    else:
        corr_results = {
            "sufficient": False,
            "reason": f"Sample size ({len(valid_data)}) is too small or rainfall/hours lost has zero variance."
        }

    # Hypothesis Testing (Mann-Whitney U Test comparing hours lost on rainy vs non-rainy days)
    test_results = {}
    rainy_hours = rainy_ops["hours_lost"].dropna()
    dry_hours = dry_ops["hours_lost"].dropna()

    if len(rainy_hours) >= 3 and len(dry_hours) >= 3:
        try:
            stat_val, p_val = stats.mannwhitneyu(rainy_hours, dry_hours, alternative="two-sided")
            test_results = {
                "valid": True,
                "test_name": "Mann-Whitney U Test",
                "statistic": float(stat_val),
                "p_value": float(p_val),
                "null_hypothesis": "The distribution of machinery delay hours is identical on rainy and non-rainy days.",
                "significant": p_val < 0.05
            }
        except Exception as e:
            test_results = {"valid": False, "reason": str(e)}
    else:
        test_results = {
            "valid": False,
            "reason": f"Not enough observations in both groups (Rainy: {len(rainy_hours)}, Dry: {len(dry_hours)})."
        }

    return {
        "merged_df": merged,
        "rainy_total": rainy_total,
        "dry_total": dry_total,
        "rainy_delayed": int((rainy_ops["delayed"] == 1).sum()),
        "dry_delayed": int((dry_ops["delayed"] == 1).sum()),
        "rainy_delay_rate": rainy_delay_rate,
        "dry_delay_rate": dry_delay_rate,
        "rate_difference": rate_diff,
        "correlation": corr_results,
        "hypothesis_test": test_results
    }, None

# ------------------------------------------------------------------------------
# 6. Chart Creation Functions (Matplotlib & Seaborn)
# ------------------------------------------------------------------------------
def create_weather_charts(weather_df: pd.DataFrame, merged_analysis: dict = None, rainy_threshold: float = 0.0):
    """
    Builds clean, labelled agricultural analytics charts using Matplotlib and Seaborn.
    """
    sns.set_theme(style="whitegrid", palette="muted")
    charts = {}

    # Chart 1: Daily Rainfall Over Time
    if weather_df is not None and not weather_df.empty:
        fig1, ax1 = plt.subplots(figsize=(10, 4.2))
        dates = pd.to_datetime(weather_df["date"])
        precip = weather_df["precipitation_sum"]

        ax1.plot(dates, precip, color="#2d6a4f", linewidth=1.5, label="Daily Rainfall")
        ax1.fill_between(dates, precip, color="#74c69d", alpha=0.35)
        ax1.axhline(rainy_threshold, color="#e76f51", linestyle="--", linewidth=1.2,
                    label=f"Rainy Day Threshold ({rainy_threshold} mm)")
        ax1.set_title("Historical Daily Rainfall Over Time", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
        ax1.set_xlabel("Date", fontsize=10, fontweight="bold")
        ax1.set_ylabel("Precipitation (mm)", fontsize=10, fontweight="bold")
        ax1.legend(loc="upper right", frameon=True)
        fig1.tight_layout()
        charts["rainfall_timeline"] = fig1

    # Chart 2: Rainfall Totals by Month
    if weather_df is not None and not weather_df.empty:
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

    # Chart 3: Delay Rate Comparison on Rainy vs Non-Rainy Operation Days
    if merged_analysis and "rainy_delay_rate" in merged_analysis:
        fig3, ax3 = plt.subplots(figsize=(7, 4.2))
        categories = [
            f"Rainy Days\n(>{rainy_threshold} mm, n={merged_analysis['rainy_total']})",
            f"Non-Rainy Days\n(≤{rainy_threshold} mm, n={merged_analysis['dry_total']})"
        ]
        rates = [merged_analysis["rainy_delay_rate"], merged_analysis["dry_delay_rate"]]
        colors = ["#e76f51", "#2a9d8f"]

        bars3 = ax3.bar(categories, rates, color=colors, width=0.45, edgecolor="#264653")
        for bar in bars3:
            h = bar.get_height()
            ax3.annotate(f"{h:.1f}%",
                         xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", va="bottom", fontsize=11, fontweight="bold", color="#1b4332")

        ax3.set_ylim(0, max(rates + [10]) * 1.25)
        ax3.set_title("Machinery Operation Delay Rate: Rainy vs. Non-Rainy Days", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
        ax3.set_ylabel("Recorded Delay Rate (%)", fontsize=10, fontweight="bold")
        fig3.tight_layout()
        charts["delay_comparison"] = fig3

    # Chart 4: Distribution of Daily Rainfall (Histogram)
    if weather_df is not None and not weather_df.empty:
        fig4, ax4 = plt.subplots(figsize=(8, 4.2))
        precip = weather_df["precipitation_sum"].dropna()
        # Filter for readable display of rainy distributions
        sns.histplot(precip, bins=25, color="#40916c", kde=True, ax=ax4, edgecolor="#1b4332")
        ax4.set_title("Distribution of Daily Precipitation", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
        ax4.set_xlabel("Daily Precipitation (mm)", fontsize=10, fontweight="bold")
        ax4.set_ylabel("Frequency (Days)", fontsize=10, fontweight="bold")
        fig4.tight_layout()
        charts["rainfall_dist"] = fig4

    # Chart 5: Scatter Plot: Daily Rainfall vs Hours Lost
    if merged_analysis and "merged_df" in merged_analysis:
        m_df = merged_analysis["merged_df"]
        if len(m_df) >= 5 and "hours_lost" in m_df.columns:
            fig5, ax5 = plt.subplots(figsize=(8, 4.5))
            sns.regplot(data=m_df, x="precipitation_sum", y="hours_lost", ax=ax5,
                        color="#2d6a4f",
                        scatter_kws={"alpha": 0.65, "s": 45, "edgecolor": "#1b4332"},
                        line_kws={"color": "#e76f51", "linewidth": 2, "label": "Trendline"})
            ax5.set_title("Daily Rainfall vs. Recorded Machinery Hours Lost", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
            ax5.set_xlabel("Daily Rainfall on Operation Date (mm)", fontsize=10, fontweight="bold")
            ax5.set_ylabel("Hours Lost (Actual - Planned, hrs)", fontsize=10, fontweight="bold")
            ax5.legend(loc="upper left")
            fig5.tight_layout()
            charts["scatter_rain_delay"] = fig5

    return charts

# ------------------------------------------------------------------------------
# 7. Weather-Based Planning Evaluation
# ------------------------------------------------------------------------------
def evaluate_planning_day(rain_mm: float, prob_pct: float, operation: str, rain_thresh: float, prob_thresh: float):
    """
    Evaluates weather conditions for an upcoming forecast day against operation heuristics.
    Returns: (category, badge_class, explanation)
    """
    guideline = OPERATION_GUIDELINES.get(operation, {})
    
    # Severe rainfall trigger
    if rain_mm > (rain_thresh * 1.8) or prob_pct > (prob_thresh * 1.6):
        category = "Higher rainfall concern"
        badge_html = "<span class='badge-higher-concern'>🔴 Higher rainfall concern</span>"
        explanation = (
            f"Forecast rainfall ({rain_mm:.1f} mm, {prob_pct:.0f}% probability) significantly exceeds the "
            f"{operation} threshold ({rain_thresh:.1f} mm). Heavy moisture and wet soil pose high risk of machinery stuck, "
            f"soil compaction, or chemical wash-off."
        )
    # Cautionary trigger
    elif rain_mm > rain_thresh or prob_pct > prob_thresh:
        category = "Caution"
        badge_html = "<span class='badge-caution'>🟡 Caution</span>"
        explanation = (
            f"Forecast rainfall ({rain_mm:.1f} mm) or precipitation chance ({prob_pct:.0f}%) is elevated relative to "
            f"ideal {operation} conditions. Operations may proceed with caution, subject to ground inspection."
        )
    # Favorable / Lower concern trigger
    else:
        category = "Lower weather concern"
        badge_html = "<span class='badge-lower-concern'>🟢 Lower weather concern</span>"
        explanation = (
            f"Minimal forecast precipitation ({rain_mm:.1f} mm, {prob_pct:.0f}% chance) within acceptable threshold "
            f"for {operation}. Weather appears generally conducive for scheduling equipment."
        )

    return category, badge_html, explanation

# ------------------------------------------------------------------------------
# 8. User Interface Layout & Sidebar Controls
# ------------------------------------------------------------------------------
# Top Header Banner
st.markdown("""
<div class="header-banner">
    <h1>🌾 Weather-Based Farm Machinery Planner</h1>
    <p>Analyze weather patterns, understand machinery delays, and plan farm operations more effectively.</p>
    <div class="badge">S.Y. B.Tech Python Programming Laboratory Capstone Project</div>
</div>
""", unsafe_allow_html=True)

# Sidebar: Controls and Configuration
st.sidebar.header("⚙️ Configuration & Filters")

# Location Selection
selected_location = st.sidebar.selectbox(
    "📍 Select Location",
    options=list(LOCATIONS.keys()),
    index=0,
    help="Select an Indian agricultural district to analyze historical weather and forecasts."
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
    help="Fetch live daily weather from Open-Meteo API or load the bundled sample dataset."
)

# Date Range Selection (Default: full 2024 calendar year)
default_start = datetime.date(2024, 1, 1)
default_end = datetime.date(2024, 12, 31)

date_range = st.sidebar.date_input(
    "📅 Historical Date Range",
    value=(default_start, default_end),
    min_value=datetime.date(2020, 1, 1),
    max_value=datetime.date.today(),
    help="Select the period for historical weather and machinery analysis."
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date_str = date_range[0].strftime("%Y-%m-%d")
    end_date_str = date_range[1].strftime("%Y-%m-%d")
else:
    start_date_str = default_start.strftime("%Y-%m-%d")
    end_date_str = default_end.strftime("%Y-%m-%d")

# Farming Operation Filter
st.sidebar.markdown("---")
st.sidebar.subheader("🚜 Machinery Operations")

selected_op = st.sidebar.selectbox(
    "Planned Farming Operation",
    options=FARM_OPERATIONS,
    index=0,
    help="Select an operation to examine tailored planning thresholds and operation delays."
)

filter_machinery_by_op = st.sidebar.checkbox(
    f"Filter analysis strictly to '{selected_op}'",
    value=False,
    help="If checked, machinery metrics reflect only the chosen operation instead of all operations."
)

# Rainy Day Threshold
st.sidebar.markdown("---")
st.sidebar.subheader("🌧️ Analytical Parameters")
rainy_threshold = st.sidebar.number_input(
    "Rainy Day Definition Threshold (mm)",
    min_value=0.0,
    max_value=20.0,
    value=0.0,
    step=0.5,
    help="Precipitation greater than this value is defined as a 'Rainy Day' in the analysis."
)
st.sidebar.caption(f"Days with precipitation > {rainy_threshold} mm are classified as Rainy Days.")

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
    Built for S.Y. B.Tech Python Programming Laboratory. Synthetic demo datasets are explicitly marked as synthetic and do not claim to represent specific physical farm surveys.
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 9. Data Loading & Cleaning Execution
# ------------------------------------------------------------------------------
raw_weather_df = None
weather_fetch_error = None
is_sample_weather = False

if weather_source_option == "Live Open-Meteo API":
    with st.spinner(f"Fetching weather records for {selected_location} via Open-Meteo API..."):
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
# 10. Compute Analytics & Statistics
# ------------------------------------------------------------------------------
weather_stats = calculate_weather_statistics(clean_weather_df, rainy_threshold=rainy_threshold)
machinery_stats = calculate_delay_statistics(active_machinery_df)
merged_analysis, merged_error = analyze_weather_delay_relationship(clean_weather_df, active_machinery_df, rainy_threshold=rainy_threshold)

# ------------------------------------------------------------------------------
# 11. Main Application Tabs
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
            f"were recorded with cumulative rainfall reaching **{weather_stats['total_rain']:.1f} mm**. "
            f"Rainfall was detected on **{weather_stats['rainy_days_count']} days ({weather_stats['rainy_days_pct']:.1f}%)**, "
            f"yielding a daily mean of **{weather_stats['mean_rain']:.1f} mm** and a peak daily event of **{weather_stats['max_rain']:.1f} mm**."
        )
    else:
        summary_parts.append("Weather records are currently not available for this period.")

    if machinery_stats:
        op_scope = f"specifically for {selected_op}" if filter_machinery_by_op else "across all logged operations"
        summary_parts.append(
            f"From the machinery operation dataset ({op_scope}), **{machinery_stats['total_operations']} operations** were logged. "
            f"The historical delay rate was **{machinery_stats['delay_rate']:.1f}%** ({machinery_stats['delayed_operations']} delayed), "
            f"representing a cumulative **{machinery_stats['total_hours_lost']:.1f} operating hours lost** compared to planned schedules."
        )
    else:
        summary_parts.append("Machinery operational records are not available to determine delay statistics.")

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
    with st.expander("🔍 View Cleaned Raw Data Tables", expanded=False):
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**Cleaned Weather Data (Top 10 Rows)**")
            if clean_weather_df is not None and not clean_weather_df.empty:
                st.dataframe(clean_weather_df.head(10), use_container_width=True)
            else:
                st.write("No weather data available.")
        with t2:
            st.markdown("**Cleaned Machinery Operations Data (Top 10 Rows)**")
            if active_machinery_df is not None and not active_machinery_df.empty:
                st.dataframe(active_machinery_df.head(10), use_container_width=True)
            else:
                st.write("No machinery data available.")

# ==============================================================================
# TAB 2: HISTORICAL DATA ANALYSIS
# ==============================================================================
with tab2:
    st.subheader("Statistical Analysis & Data Visualizations")

    # Section A: Descriptive Statistics
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

    # Section C: Weather and Machinery Delays (Merged Analysis)
    st.markdown("### C. Relationship Between Rainfall and Machinery Delays")
    if merged_analysis:
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Rainy Days Delay Rate", f"{merged_analysis['rainy_delay_rate']:.1f}%",
                      f"{merged_analysis['rainy_delayed']} of {merged_analysis['rainy_total']} ops")
        with r2:
            st.metric("Non-Rainy Days Delay Rate", f"{merged_analysis['dry_delay_rate']:.1f}%",
                      f"{merged_analysis['dry_delayed']} of {merged_analysis['dry_total']} ops")
        with r3:
            diff_color = "normal" if merged_analysis['rate_difference'] <= 0 else "inverse"
            st.metric("Delay Rate Difference", f"{merged_analysis['rate_difference']:+.1f}% pts")

        # Correlation Analysis
        st.markdown("#### 🔗 Correlation Analysis")
        corr = merged_analysis["correlation"]
        if corr.get("sufficient"):
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown(f"**Pearson Correlation ($r$):** `{corr['pearson_r']:.3f}` (p-value: `{corr['pearson_p']:.4f}`)")
                st.caption("Measures linear association between rainfall (mm) and hours lost.")
            with c_b:
                st.markdown(f"**Spearman Rank Correlation ($\\rho$):** `{corr['spearman_rho']:.3f}` (p-value: `{corr['spearman_p']:.4f}`)")
                st.caption("Measures monotonic association, robust against skewness and outliers.")
        else:
            st.warning(f"⚠️ Correlation Warning: {corr.get('reason')}")

        # Scientific Caution Notice (Correlation != Causation)
        st.markdown("""
        <div class="disclaimer-callout">
            <b>⚠️ Academic & Analytical Disclaimer:</b> Correlation does not imply causation. 
            While operations conducted on rainy days exhibit a higher recorded delay rate in this dataset, 
            delays may also arise from mechanical breakdowns, operator shortage, soil texture variations, 
            or supply chain issues. Weather is a contributing risk factor, not the sole cause.
        </div>
        """, unsafe_allow_html=True)

        # Section D: Basic Statistical Hypothesis Test (SciPy)
        st.markdown("### D. Statistical Hypothesis Test (SciPy)")
        ht = merged_analysis["hypothesis_test"]
        if ht.get("valid"):
            st.write(f"**Test Conducted:** {ht['test_name']}")
            st.markdown(f"- **Null Hypothesis ($H_0$):** {ht['null_hypothesis']}")
            st.markdown(f"- **Alternative Hypothesis ($H_1$):** Machinery operations on rainy days incur significantly higher delay hours than on non-rainy days.")
            st.markdown(f"- **Test Statistic (U):** `{ht['statistic']:.2f}`")
            st.markdown(f"- **p-value:** `{ht['p_value']:.4f}`")
            
            if ht["significant"]:
                st.success(f"✅ **Statistical Result:** The p-value ({ht['p_value']:.4f}) is less than the standard significance threshold ($\\alpha = 0.05$). "
                           "We reject the null hypothesis: in this dataset, machinery delay hours are significantly different between rainy and non-rainy days.")
            else:
                st.info(f"ℹ️ **Statistical Result:** The p-value ({ht['p_value']:.4f}) is greater than or equal to $\\alpha = 0.05$. "
                        "There is insufficient statistical evidence to reject the null hypothesis at the 5% significance level.")
        else:
            st.info(f"Hypothesis test skipped: {ht.get('reason')}")

    else:
        st.warning(f"Merged analysis could not be calculated: {merged_error}")

    st.markdown("---")

    # Section E: Visualizations
    st.markdown("### E. Data Visualizations (Matplotlib & Seaborn)")
    charts = create_weather_charts(clean_weather_df, merged_analysis, rainy_threshold=rainy_threshold)

    # 1. Line chart: Daily rainfall over time
    if "rainfall_timeline" in charts:
        st.pyplot(charts["rainfall_timeline"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 1 Insight:</b> Displays the historical chronology of daily precipitation. 
            Notice the concentrated spike during the monsoon season (June to September), contrasting with the prolonged dry winter and summer months.
        </div>
        """, unsafe_allow_html=True)

    # 2. Bar chart: Monthly rainfall totals
    if "monthly_rainfall" in charts:
        st.pyplot(charts["monthly_rainfall"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 2 Insight:</b> Aggregates cumulative precipitation per calendar month. 
            Agricultural operations such as Kharif sowing and spraying coincide with peak rainfall months, elevating operational machinery scheduling risks.
        </div>
        """, unsafe_allow_html=True)

    # 3. Bar chart: Delay rates on rainy vs non-rainy days
    if "delay_comparison" in charts:
        st.pyplot(charts["delay_comparison"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 3 Insight:</b> Direct comparison of the proportion of delayed machinery operations on rainy vs non-rainy days. 
            Demonstrates how wet conditions correlate with increased likelihood of operational rescheduling or field stoppage.
        </div>
        """, unsafe_allow_html=True)

    # 4. Histogram: Distribution of daily rainfall
    if "rainfall_dist" in charts:
        st.pyplot(charts["rainfall_dist"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 4 Insight:</b> Frequency distribution of daily precipitation values. 
            The distribution is typically right-skewed, with most days recording zero or light rainfall and a few high-intensity rainfall events.
        </div>
        """, unsafe_allow_html=True)

    # 5. Scatter plot: Daily rainfall vs hours lost
    if "scatter_rain_delay" in charts:
        st.pyplot(charts["scatter_rain_delay"])
        st.markdown("""
        <div class="chart-insight-box">
            <b>Chart 5 Insight:</b> Scatter distribution with regression trendline plotting daily rainfall against recorded lost operating hours. 
            Points higher on the vertical axis reflect greater schedule disruption on wet field days.
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# TAB 3: WEATHER-BASED PLANNING SECTION
# ==============================================================================
with tab3:
    st.subheader(f"Upcoming Weather-Based Planning Aid — {selected_location}")
    st.markdown("""
    This section evaluates upcoming daily forecasts against operational thresholds to provide an initial 
    scheduling guideline for farm machinery.
    """)

    # Operation Guidelines Display
    op_guide = OPERATION_GUIDELINES.get(selected_op, {})
    st.markdown(f"""
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;">
        <h4 style="margin: 0 0 6px 0; color: #1b4332;">🚜 Selected Operation: {selected_op}</h4>
        <p style="margin: 0 0 6px 0; font-size: 0.95rem; color: #334155;">{op_guide.get('description', '')}</p>
        <span style="font-size: 0.85rem; color: #475569;"><b>Typical Machine:</b> {op_guide.get('machine', '')} | <b>Sensitivity:</b> {op_guide.get('guidance', '')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Configurable Planning Sensitivity Thresholds
    with st.expander("⚙️ Customize Planning Heuristic Thresholds", expanded=False):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            cfg_rain_thresh = st.slider(
                f"Rainfall Concern Threshold for {selected_op} (mm)",
                min_value=0.2,
                max_value=25.0,
                value=float(op_guide.get("recommended_max_rain", 5.0)),
                step=0.5,
                help="Forecast daily rainfall exceeding this threshold triggers a cautionary or higher concern indicator."
            )
        with p_col2:
            cfg_prob_thresh = st.slider(
                f"Precipitation Probability Concern Threshold (%)",
                min_value=10.0,
                max_value=90.0,
                value=float(op_guide.get("recommended_max_prob", 40.0)),
                step=5.0,
                help="Forecast precipitation probability exceeding this percentage triggers caution."
            )
        st.caption("Note: These thresholds are demonstration heuristics for student scheduling simulation, not agronomic safety standards.")

    # Fetch 7-Day Live Forecast from Open-Meteo
    with st.spinner("Fetching 7-day live weather forecast..."):
        forecast_df, forecast_err = fetch_forecast_data(latitude=loc_info["lat"], longitude=loc_info["lon"])

    if forecast_df is None:
        st.warning(f"⚠️ Live forecast could not be retrieved ({forecast_err}). Generating demo forecast schedule.")
        # Fallback 7-day demonstration forecast
        f_dates = pd.date_range(datetime.date.today(), periods=7, freq="D")
        forecast_df = pd.DataFrame({
            "date": f_dates.strftime("%Y-%m-%d"),
            "precipitation_sum": [0.0, 0.4, 3.2, 14.5, 0.0, 0.0, 1.2],
            "precipitation_probability_max": [10, 25, 60, 85, 15, 20, 40],
            "temperature_2m_max": [29.5, 30.1, 28.0, 26.5, 29.0, 31.0, 30.5]
        })

    # Evaluate Each Forecast Day
    evaluated_records = []
    for _, row in forecast_df.iterrows():
        d_val = row["date"]
        r_val = float(row.get("precipitation_sum", 0.0))
        p_val = float(row.get("precipitation_probability_max", 0.0))
        t_val = float(row.get("temperature_2m_max", 28.0))

        cat, badge, expl = evaluate_planning_day(
            rain_mm=r_val,
            prob_pct=p_val,
            operation=selected_op,
            rain_thresh=cfg_rain_thresh,
            prob_thresh=cfg_prob_thresh
        )
        evaluated_records.append({
            "date": d_val,
            "rain_mm": r_val,
            "prob_pct": p_val,
            "temp_max": t_val,
            "category": cat,
            "badge_html": badge,
            "explanation": expl
        })

    eval_df = pd.DataFrame(evaluated_records)

    # Display Daily Forecast Cards
    st.markdown("#### 📅 Upcoming 7-Day Operation Schedule Assessment")

    f_cols = st.columns(len(eval_df))
    for i, col in enumerate(f_cols):
        day_row = eval_df.iloc[i]
        d_obj = pd.to_datetime(day_row["date"])
        day_name = d_obj.strftime("%a, %b %d")

        with col:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 10px; text-align: center; height: 230px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; font-size: 0.9rem; color: #1b4332;">{day_name}</div>
                <div style="font-size: 1.2rem; font-weight: 700; margin: 8px 0 4px 0; color: #2d6a4f;">{day_row['rain_mm']:.1f} mm</div>
                <div style="font-size: 0.8rem; color: #64748b;">Chance: {day_row['prob_pct']:.0f}%</div>
                <div style="font-size: 0.8rem; color: #64748b;">Max: {day_row['temp_max']:.1f}°C</div>
                <div style="margin-top: 10px;">{day_row['badge_html']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Detailed Schedule Table with Reasoning
    st.markdown("#### 📋 Detailed Day-by-Day Advisory")
    for _, item in eval_df.iterrows():
        d_formatted = pd.to_datetime(item["date"]).strftime("%A, %d %B %Y")
        st.markdown(f"""
        - **{d_formatted}** — Forecast: **{item['rain_mm']:.1f} mm** rainfall ({item['prob_pct']:.0f}% probability) | Max Temp: **{item['temp_max']:.1f}°C**  
          {item['badge_html']}  
          <span style="font-size: 0.9rem; color: #334155;">{item['explanation']}</span>
        """, unsafe_allow_html=True)

    # Suggested Planning Window Summary
    favorable_days = eval_df[eval_df["category"] == "Lower weather concern"]
    st.markdown("#### 💡 Planning Recommendation Window")
    if not favorable_days.empty:
        fav_dates = [pd.to_datetime(d).strftime("%b %d (%a)") for d in favorable_days["date"]]
        st.success(
            f"**Consider reviewing these comparatively dry dates for {selected_op}:** {', '.join(fav_dates)}. "
            "These dates have minimal forecast precipitation, reducing the risk of machinery slippage or chemical wash-off."
        )
    else:
        st.warning(
            f"All upcoming forecast dates exceed or approach the concern thresholds for **{selected_op}**. "
            "Consider rescheduling intensive field operations or verifying drainage capabilities before deployment."
        )

    # Mandatory Academic & Agronomic Disclaimers
    st.markdown("""
    <div class="disclaimer-callout">
        <b>⚠️ Agronomic Limitations & Field Trafficability Disclaimer:</b><br>
        1. <b>Heuristic Threshold:</b> The configured thresholds are simple planning heuristics, not guaranteed agronomic safety limits.<br>
        2. <b>Direct Soil Moisture:</b> Precipitation forecasts alone do not measure actual root-zone soil saturation, clay plasticity, or machine tire load-bearing capacity.<br>
        3. <b>Check Field Conditions:</b> Always check actual physical soil trafficability and local field conditions before deploying tractors or heavy farm machinery.<br>
        4. <b>Weather Model Uncertainty:</b> Public weather forecast models are subject to meteorological uncertainties and local microclimate variations.
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 12. Application Footer & Data Source Limitations
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="font-size: 0.85rem; color: #64748b; line-height: 1.5;">
    <b>Weather-Based Farm Machinery Planner</b> | S.Y. B.Tech Python Programming Laboratory Capstone Project<br>
    <b>Weather Data Provider:</b> Open-Meteo Historical & Forecast APIs (Non-commercial open-access).<br>
    <b>Machinery Operations:</b> Demonstration dataset with explicitly synthetic records for student laboratory analysis.<br>
    <b>Statistical Stack:</b> Pandas, NumPy, Matplotlib, Seaborn, SciPy.
</div>
""", unsafe_allow_html=True)
