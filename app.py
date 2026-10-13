"""
================================================================================
PART 3: STREAMLIT DASHBOARD & APPLICATION INTEGRATION
================================================================================
Team Member 3 Responsibility:
- Streamlit dashboard layout, responsive multi-tab architecture, custom CSS
- User control panel in sidebar (district selection, date picker, operations)
- Team member contribution tracking & viva documentation display
- Integration with Member 1's Data Pipeline (data_pipeline.py)
- Integration with Member 2's Analytics Engine (analytics.py)
- Tab 1: Dashboard Overview (4 summary cards, narrative summary, clean_data report)
- Tab 2: Historical Data Analysis UI (descriptive metrics, chart display, roadmap)
- Tab 3: Weather-Based Planning UI (Phase 2 preview, operation profiles, blueprint)
================================================================================
"""

import datetime
import os
import pandas as pd
import streamlit as st

# ------------------------------------------------------------------------------
# Import Modular Components from Member 1 and Member 2
# ------------------------------------------------------------------------------
from data_pipeline import (
    fetch_weather_data,
    load_sample_weather_data,
    load_machinery_data,
    clean_data
)

from analytics import (
    calculate_weather_statistics,
    calculate_delay_statistics,
    create_basic_weather_charts
)

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

    /* Team Contribution Box */
    .team-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 20px;
        font-size: 0.88rem;
    }

    /* Callout & Preview Containers */
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
# 2. Supported Locations & Baseline Configurations
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
# 3. Header Banner & Team Contribution Overview
# ------------------------------------------------------------------------------
st.markdown("""
<div class="header-banner">
    <h1>🌾 Weather-Based Farm Machinery Planner</h1>
    <p>Analyze weather patterns, understand machinery delays, and plan farm operations more effectively.</p>
    <div class="badge">S.Y. B.Tech Python Programming Laboratory Capstone Project | Phase 1 (50–60% Milestone)</div>
</div>
""", unsafe_allow_html=True)

# Team Contribution Card (For College Evaluator / Viva)
with st.expander("👥 Team Members & Code Division (For Evaluation)", expanded=False):
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown("""
        **Member 1: Data Pipeline Lead**  
        *Source File:* `data_pipeline.py`  
        - Open-Meteo REST API data retrieval  
        - Offline demonstration CSV loading  
        - Data cleaning pipeline (`clean_data`)  
        - Missing/duplicate/anomaly reporting
        """)
    with c_m2:
        st.markdown("""
        **Member 2: Analytics & Visuals Lead**  
        *Source File:* `analytics.py`  
        - Weather descriptive statistics (mean, median, std)  
        - Machinery delay analytics & hours lost  
        - Matplotlib & Seaborn charting engine  
        - Mathematical formulas & statistical logic
        """)
    with c_m3:
        st.markdown("""
        **Member 3: UI & System Integration Lead**  
        *Source File:* `app.py`  
        - Streamlit dashboard architecture & CSS  
        - Sidebar filters & district coordination  
        - Dashboard integration (Tabs 1, 2, and 3)  
        - Phase 2 Planning Framework Blueprint
        """)

# ------------------------------------------------------------------------------
# 4. Sidebar Controls & Configuration
# ------------------------------------------------------------------------------
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

# Date Range Selection (Default: full 2024 calendar year)
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

# Rainy Day Threshold
st.sidebar.markdown("---")
st.sidebar.subheader("🌧️ Analytical Parameters")
rainy_threshold = 0.0
st.sidebar.caption(f"Rainy Day Definition: Days with precipitation > {rainy_threshold} mm are classified as Rainy Days.")

# Custom CSV File Uploader
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Custom Data Upload")
custom_machinery_file = st.sidebar.file_uploader(
    "Upload Machinery Operations CSV",
    type=["csv"],
    help="Upload your own machinery log CSV with required columns (see README)."
)

# Academic Attribution & Division Notice
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background-color: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 0.8rem; color: #475569;'>
    <b>Team Division:</b><br>
    • <b>Member 1:</b> <code>data_pipeline.py</code><br>
    • <b>Member 2:</b> <code>analytics.py</code><br>
    • <b>Member 3:</b> <code>app.py</code>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. Data Pipeline Execution (Invoking Member 1's Functions)
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

# Execute Data Cleaning (clean_data from Member 1)
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

# Filter by selected operation if requested
if filter_machinery_by_op and not active_machinery_df.empty and "operation" in active_machinery_df.columns:
    active_machinery_df = active_machinery_df[active_machinery_df["operation"].str.lower() == selected_op.lower()]

# ------------------------------------------------------------------------------
# 6. Analytics Execution (Invoking Member 2's Functions)
# ------------------------------------------------------------------------------
weather_stats = calculate_weather_statistics(clean_weather_df, rainy_threshold=rainy_threshold)
machinery_stats = calculate_delay_statistics(active_machinery_df)

# ------------------------------------------------------------------------------
# 7. Main Application Tabs (Assembled by Member 3)
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

    # Data Quality and Cleaning Report (from Member 1's clean_data)
    with st.expander("🛠️ Data Quality & Cleaning Summary (clean_data() Report)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Weather Dataset Cleaning (Member 1)**")
            st.write(f"- Initial rows: {weather_clean_report.get('initial_rows', 0)}")
            st.write(f"- Final cleaned rows: {weather_clean_report.get('final_rows', 0)}")
            st.write(f"- Missing values identified: {weather_clean_report.get('missing_values_found', 0)}")
            st.write(f"- Duplicates removed: {weather_clean_report.get('duplicates_removed', 0)}")
            st.write(f"- Anomalies handled: {weather_clean_report.get('anomalies_handled', 0)}")
            if weather_clean_report.get("notes"):
                for note in weather_clean_report["notes"]:
                    st.caption(f"• {note}")

        with c2:
            st.markdown("**Machinery Operations Dataset Cleaning (Member 1)**")
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

    # Section A: Descriptive Weather Statistics (Member 2)
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

    # Section B: Machinery Delay Analysis (Member 2)
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

    # Section C: Basic Visualizations (Member 2)
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

    # Section D: Phase 2 Roadmap & Deferred Features Preview (Member 3)
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

    # Professional Phase 2 Planning Notice (Member 3)
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
# 8. Application Footer & Data Source Transparency
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="font-size: 0.85rem; color: #64748b; line-height: 1.5;">
    <b>Weather-Based Farm Machinery Planner</b> | S.Y. B.Tech Python Programming Laboratory Capstone Project (Phase 1: 50–60% Completion)<br>
    <b>Weather Data Provider:</b> Open-Meteo Historical Archive API (Non-commercial open-access).<br>
    <b>Machinery Operations:</b> Demonstration dataset with explicitly synthetic records for student laboratory analysis.<br>
    <b>Modular Code Architecture:</b> <code>data_pipeline.py</code> (Member 1) | <code>analytics.py</code> (Member 2) | <code>app.py</code> (Member 3).
</div>
""", unsafe_allow_html=True)
