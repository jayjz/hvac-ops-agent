# views/dispatch_workspace.py
import streamlit as st
from ui.styles import inject_global_css
from ui.components import (
    hero_header,
    kanban_card,
    ai_insight_panel,
    status_badge,
)

# --- Fixtures for illustration ---
JOBS_BY_STAGE = {
    "Unassigned": [
        {"title": "AC Unit Replacement — Unit 4B", "sub": "Riverside Commons · 2 techs req.",
         "badge": "Unassigned", "kind": "danger", "left": "Job #4821", "right": "Due Today"},
    ],
    "In Progress": [
        {"title": "Furnace Tune-Up", "sub": "412 Elm St · Tech: R. Ortiz",
         "badge": "On Site", "kind": "warning", "left": "Job #4790", "right": "Started 8:12 AM"},
    ],
    "Completed": [
        {"title": "Emergency Repair — Compressor", "sub": "Granite Business Park · Tech: M. Chen",
         "badge": "Complete", "kind": "success", "left": "Job #4762", "right": "Invoiced"},
    ],
}

AI_INSIGHTS = [
    {"icon": "⚠️", "text": "2 jobs are unassigned with SLA breach risk in the next 3 hours.", "kind": "danger"},
    {"icon": "📦", "text": "Capacitor stock (Part #C-450) is projected to run out by Friday.", "kind": "warning"},
]

def render_dispatch_workspace() -> None:
    """Fixed router-compatible entry point."""
    inject_global_css()

    hero_header(
        title="Dispatch Workspace",
        subtitle="Live job board · 7 techs on shift · Updated just now",
        right_slot=status_badge("Live", "success"),
    )

    # ---- Top metrics row ----
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Jobs Today", "18", "+3 vs avg")
    m2.metric("Unassigned", "2", "-1", delta_color="inverse")
    m3.metric("Avg Response", "34 min", "-6 min")
    m4.metric("Revenue (MTD)", "$142,300", "+8.2%")

    st.write("")

    board_col, insight_col = st.columns([3, 1], gap="large")

    with board_col:
        stage_cols = st.columns(len(JOBS_BY_STAGE))
        for col, (stage, jobs) in zip(stage_cols, JOBS_BY_STAGE.items()):
            with col:
                st.markdown(
                    f"<div style='font-family:Space Grotesk; font-weight:600; "
                    f"color:var(--text-secondary); margin-bottom:12px;'>{stage} · {len(jobs)}</div>",
                    unsafe_allow_html=True,
                )
                for job in jobs:
                    kanban_card(
                        title=job["title"],
                        subtitle=job["sub"],
                        badge_label=job["badge"],
                        badge_kind=job["kind"],
                        footer_left=job["left"],
                        footer_right=job["right"],
                    )

    with insight_col:
        ai_insight_panel(AI_INSIGHTS)

        st.write("")
        # Use native container for interactive elements, styled globally by our CSS
        with st.container():
            st.markdown(
                "<span style='font-weight:600; font-family:Space Grotesk; color:var(--text-primary);'>Quick Export</span>",
                unsafe_allow_html=True,
            )
            st.caption("Pushes current board state to QuickBooks XLSX")
            if st.button("Export to QuickBooks", width="stretch"):
                st.toast("Export queued — see utils/exports.py", icon="✅")
