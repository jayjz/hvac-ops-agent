from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st


APP_TITLE = "HVAC OpsForge"
APP_SUBTITLE = "Autonomous AI Operations Co-Pilot for HVAC & Trade Services"


def configure_page() -> None:
    """Configure the Streamlit shell once for a wide, demo-ready dashboard."""
    st.set_page_config(
        page_title=f"{APP_TITLE} Dashboard",
        page_icon="AF",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_brand_css() -> None:
    """Apply lightweight brand styling without adding frontend dependencies."""
    st.markdown(
        """
        <style>
            :root {
                --opsforge-blue: #0f4c81;
                --opsforge-blue-dark: #0b2545;
                --opsforge-green: #0f9f6e;
                --opsforge-mist: #eef7f4;
                --opsforge-border: #d8e2ea;
                --opsforge-text: #102033;
            }
            .main .block-container {
                padding-top: 1.25rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }
            [data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid var(--opsforge-border);
                border-radius: 8px;
                padding: 0.9rem 1rem;
                box-shadow: 0 6px 18px rgba(15, 76, 129, 0.08);
            }
            .opsforge-hero {
                background: linear-gradient(135deg, #0b2545 0%, #0f4c81 58%, #0f9f6e 100%);
                border-radius: 8px;
                color: #ffffff;
                padding: 1.35rem 1.5rem;
                margin-bottom: 1rem;
            }
            .opsforge-brand-row {
                display: flex;
                align-items: center;
                gap: 0.85rem;
            }
            .opsforge-mark {
                align-items: center;
                background: rgba(255, 255, 255, 0.14);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                display: inline-flex;
                font-weight: 800;
                height: 44px;
                justify-content: center;
                letter-spacing: 0;
                width: 44px;
            }
            .opsforge-hero h1 {
                font-size: 2rem;
                line-height: 1.1;
                margin: 0;
            }
            .opsforge-hero p {
                color: rgba(255, 255, 255, 0.86);
                margin: 0.35rem 0 0;
            }
            .opsforge-strip {
                background: var(--opsforge-mist);
                border: 1px solid #cfe8df;
                border-radius: 8px;
                color: var(--opsforge-text);
                padding: 0.8rem 1rem;
            }
            .opsforge-section-label {
                color: var(--opsforge-blue-dark);
                font-size: 0.82rem;
                font-weight: 750;
                letter-spacing: 0;
                margin-bottom: 0.35rem;
                text-transform: uppercase;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def build_demo_dataset(scenario: str = "Busy Monday") -> Dict[str, pd.DataFrame]:
    """Return synthetic HVAC operations data that works without MongoDB."""
    scenario_multiplier = {
        "Busy Monday": 1.0,
        "Heat Wave": 1.24,
        "AR Cleanup": 0.88,
    }.get(scenario, 1.0)

    jobs = pd.DataFrame(
        [
            {
                "job_id": "JOB-001",
                "customer": "Smith Residence",
                "city": "Nashua",
                "priority": "Emergency",
                "risk": "Missing HP-001",
                "eta_window": "8:00-10:00",
            },
            {
                "job_id": "JOB-005",
                "customer": "Johnson Family",
                "city": "Hudson",
                "priority": "High",
                "risk": "Condenser capacitor low stock",
                "eta_window": "10:30-12:00",
            },
            {
                "job_id": "JOB-003",
                "customer": "XYZ Office",
                "city": "Merrimack",
                "priority": "Standard",
                "risk": "AR balance open",
                "eta_window": "1:00-3:00",
            },
        ]
    )
    inventory = pd.DataFrame(
        [
            {
                "sku": "HP-001",
                "part": "Heat pump control board",
                "on_hand": 2,
                "reorder_point": 5,
                "status": "Critical",
            },
            {
                "sku": "CAP-5TON",
                "part": "5 ton capacitor",
                "on_hand": 4,
                "reorder_point": 8,
                "status": "Low",
            },
            {
                "sku": "FILTER-20X25",
                "part": "20x25 filter",
                "on_hand": 32,
                "reorder_point": 18,
                "status": "Healthy",
            },
        ]
    )
    ar = pd.DataFrame(
        [
            {
                "invoice": "INV-001",
                "customer": "Smith Residence",
                "amount": int(1250 * scenario_multiplier),
                "days_overdue": 14,
                "next_action": "Send owner-approved reminder",
            },
            {
                "invoice": "INV-003",
                "customer": "XYZ Office",
                "amount": int(2100 * scenario_multiplier),
                "days_overdue": 31,
                "next_action": "Escalate with service history",
            },
        ]
    )
    return {"jobs": jobs, "inventory": inventory, "ar": ar}


def build_simulation_result(dataset: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Build the deterministic demo result shown after the agent run."""
    overdue_total = int(dataset["ar"]["amount"].sum())
    critical_parts = int((dataset["inventory"]["status"] != "Healthy").sum())
    total_monthly_savings = 8400 + (critical_parts * 250)
    return {
        "total_monthly_savings": total_monthly_savings,
        "downtime_reduction": 0.42,
        "wasted_rolls_reduction": 0.30,
        "ar_improvement": max(12000, overdue_total * 3),
        "inventory_turns": 0.25,
        "agent_trace": [
            "LeadArchitect assembled the Monday operating plan.",
            "PartsAvailabilityChecker flagged HP-001 and CAP-5TON before dispatch.",
            "SchedulerOptimizer resequenced three priority stops around parts risk.",
            "ARCollector prepared two follow-up actions for overdue balances.",
            "RiskAssessor summarized downtime, cashflow, and first-visit-completion risk.",
        ],
    }


def _ensure_session_defaults() -> None:
    if "scenario" not in st.session_state:
        st.session_state.scenario = "Busy Monday"
    if "demo_loaded" not in st.session_state:
        st.session_state.demo_loaded = False
    if "dataset" not in st.session_state:
        st.session_state.dataset = build_demo_dataset(st.session_state.scenario)
    if "simulation" not in st.session_state:
        st.session_state.simulation = None


def render_sidebar() -> None:
    """Render the basic controls for the Phase 1 demo loop."""
    st.sidebar.markdown("### HVAC OpsForge")
    st.sidebar.caption(APP_SUBTITLE)
    scenario = st.sidebar.selectbox(
        "Demo scenario",
        ["Busy Monday", "Heat Wave", "AR Cleanup"],
        index=["Busy Monday", "Heat Wave", "AR Cleanup"].index(st.session_state.scenario),
    )
    if scenario != st.session_state.scenario:
        st.session_state.scenario = scenario
        st.session_state.dataset = build_demo_dataset(scenario)
        st.session_state.simulation = None
        st.session_state.demo_loaded = False

    st.sidebar.checkbox(
        "Use Live Mongo",
        value=False,
        help="Off keeps the demo fully self-contained with synthetic HVAC data.",
        key="use_live_mongo",
    )
    st.sidebar.checkbox("Show Agent Trace", value=True, key="show_agent_trace")

    if st.sidebar.button("Load Demo Company", use_container_width=True):
        st.session_state.dataset = build_demo_dataset(st.session_state.scenario)
        st.session_state.demo_loaded = True
        st.session_state.simulation = None
        st.sidebar.success("Demo company loaded.")

    if st.sidebar.button("Run Multi-Agent Dispatch", use_container_width=True):
        dataset = st.session_state.dataset
        with st.spinner("Lead Architect is coordinating specialist agents..."):
            st.session_state.simulation = build_simulation_result(dataset)
            st.session_state.demo_loaded = True
        st.sidebar.success("Agent run complete.")


def render_hero() -> None:
    """Render the branded top section."""
    st.markdown(
        f"""
        <section class="opsforge-hero">
            <div class="opsforge-brand-row">
                <div class="opsforge-mark">AF</div>
                <div>
                    <h1>{APP_TITLE}</h1>
                    <p>{APP_SUBTITLE}</p>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="opsforge-strip">
            Load a synthetic HVAC company, run the Lead Architect orchestration, and inspect the
            specialist outputs that protect first-visit completion, inventory turns, routes, and cashflow.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(simulation: Dict[str, Any] | None) -> None:
    """Render business outcome metrics for the current demo state."""
    sim = simulation or {
        "total_monthly_savings": 0,
        "downtime_reduction": 0.0,
        "wasted_rolls_reduction": 0.0,
        "ar_improvement": 0,
        "inventory_turns": 0.0,
    }
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Monthly Savings", f"${sim['total_monthly_savings']:,}", "$8.4k target")
    col2.metric("Downtime", f"-{sim['downtime_reduction'] * 100:.0f}%", "owner-visible")
    col3.metric("Wasted Trips", f"-{sim['wasted_rolls_reduction'] * 100:.0f}%", "fewer rolls")
    col4.metric("AR Cashflow", f"+${sim['ar_improvement']:,}", "faster collection")
    col5.metric("Inventory Turns", f"+{sim['inventory_turns'] * 100:.0f}%", "leaner stock")


def render_agent_console(simulation: Dict[str, Any] | None) -> None:
    """Show the multi-agent roster and the current synthetic execution state."""
    st.subheader("Agent Command Center")
    st.caption("Lead Architect coordinates specialist agents while the owner stays in control.")
    roster = pd.DataFrame(
        [
            {"Agent": "LeadArchitect", "Role": "Plans and coordinates the workflow", "Status": "Ready"},
            {"Agent": "PartsAvailabilityChecker", "Role": "Validates parts before dispatch", "Status": "Ready"},
            {"Agent": "SchedulerOptimizer", "Role": "Sequences stops by risk and location", "Status": "Ready"},
            {"Agent": "ARCollector", "Role": "Prepares overdue invoice follow-ups", "Status": "Ready"},
            {"Agent": "RiskAssessor", "Role": "Flags downtime, cashflow, and job risk", "Status": "Ready"},
        ]
    )
    if simulation:
        roster["Status"] = "Completed"
    st.dataframe(roster, use_container_width=True, hide_index=True)

    if simulation and st.session_state.get("show_agent_trace", True):
        st.markdown('<div class="opsforge-section-label">Execution Trace</div>', unsafe_allow_html=True)
        for item in simulation["agent_trace"]:
            st.info(item)


def render_operations_tabs(dataset: Dict[str, pd.DataFrame]) -> None:
    """Render basic interactive tables for the Phase 1 demo."""
    jobs_tab, inventory_tab, ar_tab = st.tabs(["Dispatch", "Inventory", "AR Follow-up"])
    with jobs_tab:
        st.subheader("Priority Dispatch Board")
        st.dataframe(dataset["jobs"], use_container_width=True, hide_index=True)
    with inventory_tab:
        st.subheader("Parts Availability Watchlist")
        st.dataframe(dataset["inventory"], use_container_width=True, hide_index=True)
        st.caption("Focus: prevent failed first visits by surfacing low-stock parts before the truck rolls.")
    with ar_tab:
        st.subheader("Accounts Receivable Follow-up Queue")
        st.dataframe(dataset["ar"], use_container_width=True, hide_index=True)
        st.caption("Focus: protect cashflow with owner-reviewed next actions.")


def owner_roi_simulator() -> None:
    """Render the branded owner ROI simulator for synthetic HVAC demo data."""
    dataset = st.session_state.dataset
    simulation = st.session_state.simulation
    render_hero()

    if not st.session_state.demo_loaded:
        st.warning("Start in the sidebar: load the demo company, then run the multi-agent dispatch.")

    render_kpi_row(simulation)
    st.divider()
    render_agent_console(simulation)
    st.divider()
    render_operations_tabs(dataset)


def parts_availability_dashboard() -> None:
    """Use Live Mongo toggle, validated schemas from PROJECT_MEMORY.md canonical VP, and 30-50% less downtime framing."""
    st.title("HVAC Parts Availability Command Center")
    st.checkbox(
        "Use Live Mongo (validated schemas from PROJECT_MEMORY.md canonical VP)",
        value=st.session_state.get("use_live_mongo", False),
    )
    st.caption(
        "Parts visibility protects first-visit completion, reduces wasted rolls, and supports the 30-50% downtime reduction target."
    )
    dataset = st.session_state.get("dataset", build_demo_dataset())
    st.dataframe(dataset["inventory"], use_container_width=True, hide_index=True)
    st.success("Parts tab maintains the 25% inventory optimization target from the canonical metrics.")


def main() -> None:
    configure_page()
    inject_brand_css()
    _ensure_session_defaults()
    render_sidebar()

    tab1, tab2 = st.tabs(["Owner ROI Simulator", "Parts Availability"])
    with tab1:
        owner_roi_simulator()
    with tab2:
        parts_availability_dashboard()


if __name__ == "__main__":
    main()
