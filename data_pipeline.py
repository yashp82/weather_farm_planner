"""
================================================================================
PART 1: DATA INGESTION & DATA CLEANING PIPELINE
================================================================================
Team Member 1 Responsibility:
- Weather data retrieval from Open-Meteo Historical Archive API (REST API & requests)
- Network exception handling (timeouts, connection errors, invalid responses)
- Streamlit caching (@st.cache_data) for performance optimization
- Local CSV data ingestion (sample weather & machinery logs, custom file upload)
- Robust data cleaning function (clean_data) using Pandas
- Data quality report generation (missing values, duplicates, range checks)
================================================================================
"""

import datetime
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
    
    Returns:
        (pd.DataFrame, None) on success
        (None, error_message_str) on failure
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
        # Fallback inline generation if file was moved or missing
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
# 3. Data Cleaning and Validation Pipeline
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
                
                # Check for invalid negative values (e.g. negative precipitation)
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
