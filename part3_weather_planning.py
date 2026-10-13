"""
================================================================================
PART 3: WEATHER-BASED PLANNING & DECISION SUPPORT SYSTEM (TAB 3)
================================================================================
Author / Owner: Team Member 3
Responsibilities:
1. Agronomic operational guidelines & equipment sensitivity heuristics
2. Operation specifications (Ploughing, Sowing, Spraying, Harvesting)
3. Three-tier decision risk matrix (Lower concern, Caution, Higher concern)
4. Rendering Tab 3: Weather-Based Planning UI & Phase 2 Implementation Blueprint
5. Soil trafficability & agronomic field safety disclaimers
================================================================================
"""

import pandas as pd
import streamlit as st


# ------------------------------------------------------------------------------
# 1. Farming Operation Specifications & Heuristic Guidelines
# ------------------------------------------------------------------------------
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
# 2. Render Tab 3: Weather-Based Planning (UI Component owned by Member 3)
# ------------------------------------------------------------------------------
def render_tab3_planning(selected_location, selected_op):
    """
    [Member 3] Assembles and renders Tab 3: Weather-Based Planning.
    Displays the Phase 2 Decision-Support Roadmap, the selected operation's profile,
    the 3-tier risk indicator matrix, the Phase 2 implementation table, and disclaimers.
    """
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
