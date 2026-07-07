# views/technician_view.py
import streamlit as st
import pandas as pd

def render_technician_view() -> None:
    """Renders the mobile-first operational view for field techs."""
    
    st.markdown('<div class="section-kicker">Field Operations</div>', unsafe_allow_html=True)
    st.title("Technician Dispatch")
    
    result = st.session_state.get("pm_result")
    
    if not result:
        st.markdown('<div class="glass-card" style="padding: 2rem; text-align: center;">', unsafe_allow_html=True)
        st.warning("No active dispatch baseline found. Please run the orchestrator in the Dispatch Workspace first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown(
        """
        <p style='color: var(--text-secondary); margin-bottom: 2rem;'>
        Today's work, parts readiness, risks, and route sequence in a phone-first view.
        </p>
        """, 
        unsafe_allow_html=True
    )

    # Extract data from global state
    schedule = result.get("optimized_schedule", {})
    tasks = schedule.get("tasks", [])
    risks = result.get("risk_register", [])

    col1, col2 = st.columns([0.6, 0.4], gap="large")
    
    with col1:
        st.subheader("Job Sequence")
        if not tasks:
            st.info("No tasks scheduled.")
        else:
            for idx, task in enumerate(tasks[:5], 1): # Show top 5 for mobile
                _render_job_card(idx, task)

    with col2:
        st.markdown('<div class="glass-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.subheader("Critical Field Risks")
        if not risks:
            st.success("No critical risks flagged for today's route.")
        else:
            for risk in risks[:3]:
                if risk.get("severity") == "High":
                    st.error(f"**{risk.get('risk')}**\n\nMitigation: {risk.get('mitigation')}")
                else:
                    st.warning(f"**{risk.get('risk')}**")
        st.markdown('</div>', unsafe_allow_html=True)


def _render_job_card(sequence: int, task: dict) -> None:
    """Renders a single heavily styled glass card for a job."""
    task_name = task.get("task", f"Job {sequence}")
    duration = task.get("duration_days", 1)
    
    st.markdown(
        f"""
        <div class="glass-card tech-job-card" style="padding: 1.2rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--accent-teal); font-weight: 700; font-size: 0.8rem;">STOP {sequence}</span>
                <span style="background: var(--border-subtle); padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem;">{duration} Days</span>
            </div>
            <h3 style="margin: 0; font-size: 1.2rem;">{task_name}</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                Status: Ready for Execution
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )