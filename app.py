"""
================================================================================
WEATHER-BASED FARM MACHINERY PLANNER (MASTER APPLICATION RUNNER)
================================================================================
Capstone Project: S.Y. B.Tech Python Programming Laboratory
Problem Statement: Agricultural Mechanization & Farm Productivity
================================================================================
Modular Architecture Divided Across 3 Team Members:
- PART 1 (Member 1): part1_data_overview.py       (Data Ingestion, Cleaning & Tab 1)
- PART 2 (Member 2): part2_historical_analysis.py (Statistical Engine, Charts & Tab 2)
- PART 3 (Member 3): part3_weather_planning.py    (Planning System, Heuristics & Tab 3)
================================================================================
"""

import datetime
import streamlit as st

# ------------------------------------------------------------------------------
# Import Modular Components (Parts 1, 2, and 3 in Sequential Order)
# ------------------------------------------------------------------------------
# Part 1: Member 1 Module
from part1_data_overview import (
    fetch_weather_data,
    load_sample_weather_data,
    load_machinery_data,
    clean_data,
    render_tab1_overview
)

# Part 2: Member 2 Module
from part2_historical_analysis import (
    calculate_weather_statistics,
    calculate_delay_statistics,
    render_tab2_analysis
)

# Part 3: Member 3 Module
from part3_weather_planning import (
    OPERATION_GUIDELINES,
    render_tab3_planning
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
    .main {
        background-color: #f8faf8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
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

FARM_OPERATIONS = list(OPERATION_GUIDELINES.keys())

# ------------------------------------------------------------------------------
# 3. Header Banner & Team Code Division Overview
# ------------------------------------------------------------------------------
st.markdown("""
<div class="header-banner">
    <h1>🌾 Weather-Based Farm Machinery Planner</h1>
    <p>Analyze weather patterns, understand machinery delays, and plan farm operations more effectively.</p>
    <div class="badge">S.Y. B.Tech Python Programming Laboratory Capstone Project | Phase 1 (50–60% Milestone)</div>
</div>
""", unsafe_allow_html=True)

# Team Contribution Card (For College Evaluator / Viva)
with st.expander("👥 Team Code Division (3 Members — Click to View)", expanded=False):
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown("""
        **Part 1: Member 1**  
        *File:* `part1_data_overview.py`  
        - Weather API ingestion & caching  
        - Offline demonstration dataset  
        - Data cleaning pipeline (`clean_data`)  
        - Renders **Tab 1: Dashboard Overview**
        """)
    with c_m2:
        st.markdown("""
        **Part 2: Member 2**  
        *File:* `part2_historical_analysis.py`  
        - Weather & machinery statistics formulas  
        - Schedule variance & hours lost  
        - Matplotlib & Seaborn charting engine  
        - Renders **Tab 2: Historical Analysis**
        """)
    with c_m3:
        st.markdown("""
        **Part 3: Member 3**  
        *File:* `part3_weather_planning.py` & `app.py`  
        - Streamlit master dashboard shell & CSS  
        - Operational heuristic guidelines  
        - Phase 2 decision roadmap blueprint  
        - Renders **Tab 3: Weather-Based Planning**
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

# Academic Division Notice
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background-color: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 0.8rem; color: #475569;'>
    <b>Code Architecture (3 Parts):</b><br>
    • <b>Part 1 (Member 1):</b> <code>part1_data_overview.py</code><br>
    • <b>Part 2 (Member 2):</b> <code>part2_historical_analysis.py</code><br>
    • <b>Part 3 (Member 3):</b> <code>part3_weather_planning.py</code>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. Execute Data Pipeline (Part 1 — Member 1)
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

# Execute Data Cleaning Pipeline
clean_weather_df, weather_clean_report = clean_data(raw_weather_df, dataset_type="weather") if raw_weather_df is not None else ({}, {})
clean_machinery_df, machinery_clean_report = clean_data(raw_machinery_df, dataset_type="machinery") if raw_machinery_df is not None else ({}, {})

# Filter machinery by location if applicable
if not clean_machinery_df.empty and "location" in clean_machinery_df.columns:
    loc_match = clean_machinery_df[clean_machinery_df["location"].str.lower() == selected_location.lower()]
    active_machinery_df = loc_match.copy() if not loc_match.empty else clean_machinery_df.copy()
else:
    active_machinery_df = clean_machinery_df.copy()

# Filter by selected operation if requested
if filter_machinery_by_op and not active_machinery_df.empty and "operation" in active_machinery_df.columns:
    active_machinery_df = active_machinery_df[active_machinery_df["operation"].str.lower() == selected_op.lower()]

# ------------------------------------------------------------------------------
# 6. Execute Analytics Engine (Part 2 — Member 2)
# ------------------------------------------------------------------------------
weather_stats = calculate_weather_statistics(clean_weather_df, rainy_threshold=rainy_threshold)
machinery_stats = calculate_delay_statistics(active_machinery_df)

# ------------------------------------------------------------------------------
# 7. Render Main Tabs (Sequential Order: Parts 1, 2, and 3)
# ------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Tab 1: Dashboard Overview (Part 1)",
    "📈 Tab 2: Historical Analysis (Part 2)",
    "🗓️ Tab 3: Weather-Based Planning (Part 3)"
])

# Tab 1: Delegated to Part 1 (Member 1)
with tab1:
    render_tab1_overview(
        clean_weather_df=clean_weather_df,
        active_machinery_df=active_machinery_df,
        weather_clean_report=weather_clean_report,
        machinery_clean_report=machinery_clean_report,
        weather_stats=weather_stats,
        machinery_stats=machinery_stats,
        selected_location=selected_location,
        is_sample_weather=is_sample_weather,
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        selected_op=selected_op,
        filter_machinery_by_op=filter_machinery_by_op,
        rainy_threshold=rainy_threshold
    )

# Tab 2: Delegated to Part 2 (Member 2)
with tab2:
    render_tab2_analysis(
        clean_weather_df=clean_weather_df,
        active_machinery_df=active_machinery_df,
        weather_stats=weather_stats,
        machinery_stats=machinery_stats,
        rainy_threshold=rainy_threshold
    )

# Tab 3: Delegated to Part 3 (Member 3)
with tab3:
    render_tab3_planning(
        selected_location=selected_location,
        selected_op=selected_op
    )

# ------------------------------------------------------------------------------
# 8. Application Footer
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="font-size: 0.85rem; color: #64748b; line-height: 1.5;">
    <b>Weather-Based Farm Machinery Planner</b> | S.Y. B.Tech Python Programming Laboratory Capstone Project (Phase 1: 50–60% Completion)<br>
    <b>Weather Data Provider:</b> Open-Meteo Historical Archive API (Non-commercial open-access).<br>
    <b>Machinery Operations:</b> Demonstration dataset with explicitly synthetic records for student laboratory analysis.<br>
    <b>Order-Wise Code Division:</b> <code>part1_data_overview.py</code> (Member 1) | <code>part2_historical_analysis.py</code> (Member 2) | <code>part3_weather_planning.py</code> (Member 3).
</div>
""", unsafe_allow_html=True)
