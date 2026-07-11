# views/dispatch_workspace.py
import streamlit as st
import pandas as pd
import base64
from utils.engine import execute_pm_run
from ui.charts import build_risk_chart_png, build_gantt_figure_b64
# [UPDATED IMPORT] Bring in the new QuickBooks wrapper
from utils.exports import build_report_zip, build_quickbooks_xlsx

def render_dispatch_workspace() -> None:
    """Renders the primary executive workspace and execution controls."""
    
    st.markdown('<div class="section-kicker">Executive Dashboard</div>', unsafe_allow_html=True)
    st.title("Dispatch Baseline Engine")
    
    # 1. SETUP PANEL
    st.markdown('<div class="glass-card" style="padding: 2rem; margin-top: 1rem; margin-bottom: 2rem;">', unsafe_allow_html=True)
    setup_col1, setup_col2 = st.columns(2, gap="large")
    
    with setup_col1:
        st.subheader("Data Architecture")
        live_mongo = st.toggle("Enable Live MongoDB Pipeline", value=st.session_state.get("live_mongo_enabled", False))
        st.session_state["live_mongo_enabled"] = live_mongo
        
        if live_mongo:
            st.success("Connected: Agents will read/write to hvac_ops database.")
        else:
            st.info("Synthetic Fallback: Using safe demo data.")
            
    with setup_col2:
        st.subheader("Analysis Goals")
        goal_text = st.text_area(
            "Strategic Targets",
            value="\n".join(st.session_state.get("goals", [])),
            height=120,
            label_visibility="collapsed"
        )
        st.session_state["goals"] = [line.strip() for line in goal_text.splitlines() if line.strip()]
        
    if st.button("Execute Multi-Agent Dispatch", width="stretch", type="primary"):
        result = execute_pm_run(
            project_path=None, 
            goals=st.session_state["goals"], 
            live_mongo=live_mongo
        )
        if result:
            st.session_state["pm_result"] = result
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. RESULTS PANEL
    result = st.session_state.get("pm_result")
    if result:
        st.markdown('<div class="section-kicker">Analysis Output</div>', unsafe_allow_html=True)
        _render_executive_tabs(result)
    else:
        st.info("Awaiting execution. Configure goals and click Execute.")

def _render_executive_tabs(result: dict) -> None:
    """Renders the high-level project data using our chart utilities."""
    
    report = result.get("pm_report", {})
    req_df = pd.DataFrame(result.get("requirements_register", []))
    risk_df = pd.DataFrame(result.get("risk_register", []))
    sched_df = pd.DataFrame(result.get("optimized_schedule", {}).get("tasks", []))
    
    # [FIX] Extract the full baseline dictionary needed for QuickBooks formatting
    baseline_data = result.get("dispatch_baseline", {})

    risk_chart_bytes = build_risk_chart_png(risk_df)
    gantt_fig = build_gantt_figure_b64(sched_df)

    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Requirements", "Risks", "Schedule"])
    
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
        
        # [FIX] Split the exports into a clean, two-column layout
        export_col1, export_col2 = st.columns(2)
        
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
            else:
                st.info("QuickBooks data unavailable.")
                
        st.markdown('</div>', unsafe_allow_html=True)
            
    with tab2:
        if not req_df.empty:
            st.dataframe(req_df, width="stretch", hide_index=True)
        else:
            st.warning("No requirements found.")
            
    with tab3:
        if not risk_df.empty:
            if risk_chart_bytes:
                b64 = base64.b64encode(risk_chart_bytes.encode()) if isinstance(risk_chart_bytes, str) else base64.b64encode(risk_chart_bytes).decode()
                st.image(f"data:image/png;base64,{b64}", width=800)
            st.dataframe(risk_df, width="stretch", hide_index=True)
        else:
            st.warning("No risks identified.")
            
    with tab4:
        if not sched_df.empty:
            if gantt_fig:
                st.pyplot(gantt_fig, width="stretch")
            st.dataframe(sched_df, width="stretch", hide_index=True)
        else:
            st.warning("No schedule tasks generated.")