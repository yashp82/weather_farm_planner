"""
================================================================================
PART 1: DATA INGESTION, DATA CLEANING & DASHBOARD OVERVIEW (TAB 1)
================================================================================
Author / Owner: Team Member 1
Responsibilities:
1. Open-Meteo Historical Archive API data fetching with timeout/error handling
2. Offline demonstration data loading (sample weather & machinery logs)
3. Automated data cleaning pipeline (clean_data) with quality report
4. Rendering Tab 1: Dashboard Overview (4 Metric cards, Narrative summary,
   Data quality report expander, and Cleaned raw data preview tables)
================================================================================
"""

import os
import requests
import pandas as pd
import streamlit as st


# ------------------------------------------------------------------------------
# 1. API Weather Data Ingestion (Open-Meteo Archive API)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_weather_data(latitude: float, longitude: float, start_date: str, end_date: str):
    """
    [Member 1] Fetches daily historical weather information from the Open-Meteo Historical Weather API.
    Endpoint: https://archive-api.open-meteo.com/v1/archive
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
            return None, f"Open-Meteo API returned error status {response.status_code}: {response.text[:120]}"
        
        data = response.json()
        if "daily" not in data or not data["daily"].get("time"):
            return None, "Empty or invalid response structure received from weather API."

        daily = data["daily"]
        df = pd.DataFrame({
            "date": daily["time"],
            "precipitation_sum": daily.get("precipitation_sum", []),
            "temperature_2m_max": daily.get("temperature_2m_max", []),
            "relative_humidity_2m_mean": daily.get("relative_humidity_2m_mean", [])
        })
        return df, None

    except requests.exceptions.Timeout:
        return None, "Connection timed out while reaching Open-Meteo API. Please use offline sample dataset."
    except requests.exceptions.ConnectionError:
        return None, "Network connection error. Open-Meteo API is unreachable. Please switch to offline sample dataset."
    except Exception as e:
        return None, f"An unexpected error occurred during weather retrieval: {str(e)}"


# ------------------------------------------------------------------------------
# 2. Local CSV Data Ingestion & Demonstration Fallback
# ------------------------------------------------------------------------------
def load_sample_weather_data(location_name: str = "Pune"):
    """
    [Member 1] Loads bundled sample weather CSV data (synthetic demo records).
    Enables the application to operate 100% offline during college laboratory evaluation.
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
        dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
        return pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "location": location_name,
            "precipitation_sum": [0.0] * len(dates),
            "temperature_2m_max": [30.0] * len(dates),
            "relative_humidity_2m_mean": [60.0] * len(dates)
        })


def load_machinery_data(uploaded_file=None):
    """
    [Member 1] Ingests machinery operational records either from an uploaded CSV file
    or from the bundled demonstration file (data/machinery_operations.csv).
    Validates that required columns exist.
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
# 3. Data Cleaning Pipeline
# ------------------------------------------------------------------------------
def clean_data(df: pd.DataFrame, dataset_type: str = "weather"):
    """
    [Member 1] Cleans, standardizes, and validates dataset observations:
    - Parses date strings to valid datetime format
    - Converts numeric columns into appropriate numeric data types
    - Identifies missing values without silently replacing them with zero
    - Identifies and drops exact duplicate rows
    - Checks for negative rainfall and invalid working hours
    - Validates binary delay indicators (must be 0 or 1)
    - Returns cleaned DataFrame along with a detailed data quality report dictionary
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

    # 3. Weather dataset cleaning
    if dataset_type == "weather":
        num_cols = ["precipitation_sum", "temperature_2m_max", "relative_humidity_2m_mean"]
        for col in num_cols:
            if col in clean_df.columns:
                clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")
                missing = clean_df[col].isna().sum()
                if missing > 0:
                    report["missing_values_found"] += int(missing)
                    report["notes"].append(f"Identified {missing} missing values in '{col}'.")
                
                # Check for invalid negative values
                if col == "precipitation_sum":
                    neg_mask = clean_df[col] < 0
                    neg_count = neg_mask.sum()
                    if neg_count > 0:
                        clean_df.loc[neg_mask, col] = 0.0
                        report["anomalies_handled"] += int(neg_count)
                        report["notes"].append(f"Adjusted {neg_count} negative rainfall values to 0.0 mm.")

    # 4. Machinery operations dataset cleaning
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
        
        # Strip text whitespace
        text_cols = ["location", "operation", "machine_type", "delay_reason"]
        for col in text_cols:
            if col in clean_df.columns:
                clean_df[col] = clean_df[col].astype(str).str.strip()

    report["final_rows"] = len(clean_df)
    return clean_df, report


# ------------------------------------------------------------------------------
# 4. Render Tab 1: Dashboard Overview (UI Component owned by Member 1)
# ------------------------------------------------------------------------------
def render_tab1_overview(
    clean_weather_df,
    active_machinery_df,
    weather_clean_report,
    machinery_clean_report,
    weather_stats,
    machinery_stats,
    selected_location,
    is_sample_weather,
    start_date_str,
    end_date_str,
    selected_op,
    filter_machinery_by_op,
    rainy_threshold=0.0
):
    """
    [Member 1] Assembles and renders Tab 1: Dashboard Overview.
    Displays 4 metric cards, automated narrative summary, data quality report,
    and data preview tables.
    """
    st.subheader(f"Overview for {selected_location}")
    if is_sample_weather:
        st.caption("ℹ️ Showing synthetic sample demonstration weather records.")
    else:
        st.caption(f"🌐 Sourced from Open-Meteo Historical Archive API ({start_date_str} to {end_date_str}).")

    # 4 Summary Metric Cards
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    # Metric 1: Total weather records
    with m_col1:
        val1 = f"{weather_stats['total_records']}" if weather_stats else "Not available"
        desc1 = "Days in observation period" if weather_stats else "Missing weather data"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Weather Records</div>
            <div class="metric-value">{val1}</div>
            <div class="metric-desc">{desc1}</div>
        </div>
        """, unsafe_allow_html=True)

    # Metric 2: Average daily rainfall
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

    # Metric 3: Number of rainy days
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

    # Metric 4: Historical machinery delay rate (from machinery records only)
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

    # Data Quality & Cleaning Summary Expander
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
