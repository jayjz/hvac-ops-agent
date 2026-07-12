# views/technician_view.py
import streamlit as st
import json
import os

def render_technician_view() -> None:
    """Renders the mobile-first operational view for field techs."""
    
    st.markdown('<div class="section-kicker">Field Operations</div>', unsafe_allow_html=True)
    st.title("Technician Dispatch")
    
    # 1. Load Technician Context (Simulate Login)
    # We pull from the seeded data to populate our "login" dropdown
    techs = _load_mock_techs()
    if not techs:
        st.warning("No technician data available. Please run the seed_demo_data.py script.")
        return

    # Create a clean dictionary for the selector: {"TCH-001": "TCH-001 - Tech 1 (Lead Tech)", ...}
    tech_options = {t["id"]: f"{t['id']} - {t['name']} ({t['role']})" for t in techs}
    
    # Sidebar "Login" Context
    with st.sidebar:
        st.subheader("Field Context")
        selected_tech_id = st.selectbox(
            "View As:", 
            options=list(tech_options.keys()), 
            format_func=lambda x: tech_options[x]
        )
        st.caption(f"Currently viewing schedule for: **{tech_options[selected_tech_id]}**")

    # 2. Check for Global State
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

    # 3. Contextual Data Filtering
    schedule = result.get("optimized_schedule", {})
    all_tasks = schedule.get("tasks", [])
    risks = result.get("risk_register", [])
    
    # We need to map the scheduled tasks back to the original jobs to find the assigned tech
    # In a full production app, the scheduler output should include the assigned tech ID directly.
    # For this demo, we cross-reference the raw jobs data.
    raw_jobs = _load_mock_jobs()
    job_to_tech_map = {job["job_id"]: job.get("assigned_tech") for job in raw_jobs}

    # Filter tasks specifically for the selected technician
    tech_tasks = []
    for task in all_tasks:
        task_name = task.get("task", "")
        # Assuming the task name contains the job_id (e.g., "Installation for JOB-1001")
        # We attempt to extract it or map it. For the demo, we'll check if the tech is assigned.
        # If the task name doesn't have the ID, we'll do a loose match or assign it for demo purposes if it's unassigned.
        assigned_tech = None
        for job_id, tech in job_to_tech_map.items():
            if job_id in task_name:
                assigned_tech = tech
                break
        
        # If no specific job_id is found in the task, randomly assign it for the demo,
        # OR strictly filter if your scheduler outputs the tech ID.
        if assigned_tech == selected_tech_id or (assigned_tech is None and "Tech" in task_name):
             tech_tasks.append(task)

    # Two-column layout for desktop, stacks on mobile
    col1, col2 = st.columns([0.6, 0.4], gap="large")
    
    with col1:
        st.subheader(f"Job Sequence: {tech_options[selected_tech_id]}")
        if not tech_tasks:
            st.info("No tasks scheduled for this technician today.")
        else:
            for idx, task in enumerate(tech_tasks, 1):
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
            <h3 style="margin: 0; font-size: 1.2rem; color: var(--text-primary);">{task_name}</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                Status: Ready for Execution
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def _load_mock_techs() -> list:
    """Helper to load technician data from the demo JSON."""
    try:
        path = os.path.join("memory", "demo_data.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("technicians", [])
    except Exception as exc:
        st.error(f"Failed to load technician data: {exc}")
    return []

def _load_mock_jobs() -> list:
     """Helper to load raw jobs to cross-reference assignments."""
     try:
        path = os.path.join("memory", "demo_data.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("jobs", [])
     except Exception:
         pass
     return []