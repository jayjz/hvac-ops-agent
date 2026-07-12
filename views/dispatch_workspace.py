# views/dispatch_workspace.py
# ==============================================================================
# HVAC OpsForge: Dispatch Workspace View
# Description: Core executive dashboard for multi-agent dispatch orchestration.
# Architecture: MVC - View layer responsible for orchestrator trigger & telemetry.
# ==============================================================================

import streamlit as st
import pandas as pd
import json

from utils.engine import execute_pm_run
# [P0 FIX] Updated imports to match the new raw byte generation functions in charts.py
from ui.charts import build_risk_chart_png, build_gantt_chart_png
from utils.exports import build_report_zip, build_quickbooks_xlsx

def render_dispatch_workspace() -> None:
    """
    Renders the primary executive workspace.
    Entry point for the Multi-Agent Orchestrator (LeadArchitect).
    """
    
    # Global UI Header: Spatial Cyber-Physical Theme
    st.markdown('<div class="section-kicker">Executive Dashboard</div>', unsafe_allow_html=True)
    st.title("Dispatch Baseline Engine")
    
    # 1. SETUP PANEL: Configuration for the agentic loop
    st.markdown('<div class="glass-card" style="padding: 2rem; margin-top: 1rem; margin-bottom: 2rem;">', unsafe_allow_html=True)
    setup_col1, setup_col2 = st.columns(2, gap="large")
    
    with setup_col1:
        st.subheader("Data Architecture")
        # Toggle between live DB and Demo/Mock data (Phase B logic integration)
        live_mongo = st.toggle("Enable Live MongoDB Pipeline", value=st.session_state.get("live_mongo_enabled", False))
        st.session_state["live_mongo_enabled"] = live_mongo
        
        if live_mongo:
            st.success("Connected: Agents will read/write to hvac_ops database.")
        else:
            st.info("Synthetic Fallback: Using demo_data.json.")
            
    with setup_col2:
        st.subheader("Analysis Goals")
        # User-defined strategic intent for the LeadArchitect agent
        goal_text = st.text_area(
            "Strategic Targets",
            value="\n".join(st.session_state.get("goals", [])),
            height=120,
            label_visibility="collapsed"
        )
        st.session_state["goals"] = [line.strip() for line in goal_text.splitlines() if line.strip()]
        
    # Execution Trigger: Initiates the Async Orchestration Loop
    if st.button("Execute Multi-Agent Dispatch", width="stretch", type="primary"):
        with st.spinner("LeadArchitect is planning operations..."):
            result = execute_pm_run(
                project_path=None, 
                goals=st.session_state["goals"], 
                live_mongo=live_mongo
            )
            if result:
                st.session_state["pm_result"] = result
                st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. RESULTS PANEL: Data rendering layer
    result = st.session_state.get("pm_result")
    if result:
        st.markdown('<div class="section-kicker">Analysis Output</div>', unsafe_allow_html=True)
        _render_executive_tabs(result)
    else:
        st.info("Awaiting execution. Configure goals and click Execute.")

def _render_executive_tabs(result: dict) -> None:
    """
    Renders high-level project telemetry via tabs.
    Includes ReAct Thought Trace for agent transparency (Phase C).
    """
    
    # Extract data from Orchestrator payload
    report = result.get("pm_report", {})
    req_df = pd.DataFrame(result.get("requirements_register", []))
    risk_df = pd.DataFrame(result.get("risk_register", []))
    sched_df = pd.DataFrame(result.get("optimized_schedule", {}).get("tasks", []))
    baseline_data = result.get("dispatch_baseline", {})

    # [P0 FIX] Generate charts as raw bytes to avoid serialization issues
    risk_chart_bytes = build_risk_chart_png(risk_df)
    gantt_bytes = build_gantt_chart_png(sched_df)

    # UI Tabs: Segregated Views for Executive Focus
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Requirements", "Risks", "Schedule", "Agent Logic"])
    
    with tab1:
        st.markdown('<div class="glass-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.subheader("Executive Snapshot")
        st.write(report.get("summary", "No summary provided."))
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Requirements", len(req_df))
        m2.metric("High Risks", len(risk_df[risk_df.get('severity') == 'High']) if not risk_df.empty else 0)
        m3.metric("Planned Duration", f"{report.get('planned_duration_days', 0)} Days")
        
        st.divider()
        st.subheader("Export Center")
        
        export_col1, export_col2 = st.columns(2)
        
        # Export logic for enterprise hand-off
        with export_col1:
            zip_bytes = build_report_zip(report, req_df, risk_df, sched_df, risk_chart_bytes)
            st.download_button(
                label="📦 Full Project Package (ZIP)",
                data=zip_bytes,
                file_name="hvac_opsforge_baseline.zip",
                mime="application/zip",
                type="primary",
                width="stretch"
            )
            
        with export_col2:
            if baseline_data:
                qb_bytes = build_quickbooks_xlsx(baseline_data)
                st.download_button(
                    label="📊 QuickBooks Sync (XLSX)",
                    data=qb_bytes,
                    file_name="quickbooks_hvac_sync.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="secondary",
                    width="stretch"
                )
                
        st.markdown('</div>', unsafe_allow_html=True)
            
    with tab2:
        if not req_df.empty:
            st.dataframe(req_df, width="stretch", hide_index=True)
        else:
            st.warning("No requirements found.")
            
    with tab3:
        if not risk_df.empty:
            # [P0 FIX] Directly render raw bytes. No Base64 ternary mess.
            if risk_chart_bytes:
                st.image(risk_chart_bytes, width=800)
            st.dataframe(risk_df, width="stretch", hide_index=True)
        else:
            st.warning("No risks identified.")
            
    with tab4:
        if not sched_df.empty:
            # [P0 FIX] Directly render raw bytes for the Gantt chart.
            if gantt_bytes:
                st.image(gantt_bytes, use_container_width=True)
            st.dataframe(sched_df, width="stretch", hide_index=True)
        else:
            st.warning("No schedule tasks generated.")

    with tab5:
        st.subheader("ReAct Thought Trace")
        plan = result.get("execution_plan", [])
        for i, step in enumerate(plan):
            specialist_name = step.get('specialist') or step.get('agent') or step.get('name') or "Unknown"
            with st.expander(f"Step {i+1}: {specialist_name}"):
                st.markdown(f"**Action:** {step.get('action', 'N/A')}")
                thought = step.get('thought', 'No rationale provided.')
                
                # SAFE RENDERING: Only attempt JSON if it looks like JSON
                if isinstance(thought, str) and (thought.strip().startswith('{') or thought.strip().startswith('[')):
                    try:
                        st.json(thought)
                    except:
                        st.text(thought)
                else:
                    st.text(thought) # Fallback to text rendering

# ==============================================================================
# End of File
# ==============================================================================
