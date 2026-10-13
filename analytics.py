"""
================================================================================
PART 2: STATISTICAL ANALYTICS & DATA VISUALIZATION ENGINE
================================================================================
Team Member 2 Responsibility:
- Descriptive weather statistics computation (mean, median, max, std dev, total)
- Rainy day classification logic (daily precipitation > 0.0 mm)
- Machinery operational metrics (delay rate %, planned vs actual hours)
- Schedule variance analysis (hours lost = max(0, actual - planned))
- Publication-quality visualizations using Matplotlib and Seaborn:
    1. Daily Precipitation Timeline (Line Chart)
    2. Monthly Total Precipitation (Bar Chart)
    3. Daily Precipitation Distribution (Histogram with KDE)
================================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------------------------------------------------------
# 1. Weather Descriptive Statistics Computation
# ------------------------------------------------------------------------------
def calculate_weather_statistics(weather_df: pd.DataFrame, rainy_threshold: float = 0.0):
    """
    [Member 2] Computes descriptive meteorological statistics using Pandas and NumPy.
    
    Formulas:
        - Mean: x̄ = (1/N) * Σ(x_i)
        - Median: 50th percentile of precipitation observations
        - Maximum: max(x_i)
        - Standard Deviation: s = sqrt( (1 / (N - 1)) * Σ(x_i - x̄)^2 )
        - Rainy Day: Any observation with precipitation > rainy_threshold (default > 0.0 mm)
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


# ------------------------------------------------------------------------------
# 2. Machinery Delay Analytics Computation
# ------------------------------------------------------------------------------
def calculate_delay_statistics(machinery_df: pd.DataFrame):
    """
    [Member 2] Computes operational machinery delay metrics from valid records.
    
    Rules:
        - Delay rate is computed strictly from machinery logs:
            R_delay = (delayed_operations / total_operations) * 100%
        - Hours lost represents the positive difference between actual and planned hours:
            H_lost = Σ max(0, actual_hours - planned_hours)
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

    # Total recorded hours lost: sum of positive differences
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
# 3. Statistical Data Visualizations (Matplotlib & Seaborn)
# ------------------------------------------------------------------------------
def create_basic_weather_charts(weather_df: pd.DataFrame, rainy_threshold: float = 0.0):
    """
    [Member 2] Generates labelled agricultural analytics figures using Matplotlib & Seaborn:
        Chart 1: Daily Precipitation Timeline (Line Chart with rainy day threshold)
        Chart 2: Monthly Total Precipitation (Bar Chart with seasonal totals)
        Chart 3: Distribution of Daily Precipitation (Histogram with KDE)
    """
    sns.set_theme(style="whitegrid", palette="muted")
    charts = {}

    if weather_df is None or weather_df.empty:
        return charts

    # Chart 1: Daily Rainfall Timeline (Line Chart)
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

    # Chart 2: Monthly Total Precipitation (Bar Chart)
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

    # Chart 3: Distribution of Daily Precipitation (Histogram with KDE)
    fig3, ax3 = plt.subplots(figsize=(8, 4.2))
    precip_clean = weather_df["precipitation_sum"].dropna()
    sns.histplot(precip_clean, bins=25, color="#40916c", kde=True, ax=ax3, edgecolor="#1b4332")
    ax3.set_title("Distribution of Daily Precipitation", fontsize=13, fontweight="bold", pad=12, color="#1b4332")
    ax3.set_xlabel("Daily Precipitation (mm)", fontsize=10, fontweight="bold")
    ax3.set_ylabel("Frequency (Number of Days)", fontsize=10, fontweight="bold")
    fig3.tight_layout()
    charts["rainfall_dist"] = fig3

    return charts
